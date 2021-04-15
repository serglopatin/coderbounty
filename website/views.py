from .forms import IssueCreateForm, BountyCreateForm, UserProfileForm
from actstream import action
from actstream.models import Action, user_stream
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core import serializers
from django.urls import reverse

from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import ListView, DetailView, FormView, TemplateView, View
from django.views.generic.edit import UpdateView
from django.views.generic.detail import SingleObjectMixin
from .models import Issue, UserProfile, Bounty, Service, Taker, Solution, Payment
from .utils import (
    get_issue_helper,
    leaderboard,
    post_to_slack,
    submit_issue_taker,
    get_comment_helper,
    create_comment,
)
from wepay import WePay
from time import strftime
import datetime
import json

from allauth.socialaccount.models import (
    SocialToken,
    SocialApp,
    SocialAccount,
    SocialLogin,
)
import requests
from django.http import Http404
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.db.models import Sum


def parse_url_ajax(request):
    url = request.POST.get("url", "https://github.com/twbs/bootstrap/issues/21814")
    helper = get_issue_helper(request, url)
    issue = helper.get_issue(request, url)
    return HttpResponse(json.dumps(issue))


# @cache_page(432000) #5 days
def home(request, template="index.html"):
    activities = Action.objects.all()[0:10]
    context = {
        "activities": activities,
        "leaderboard": leaderboard(),
    }
    response = render(request, template, context)
    return response


@login_required
def create_issue_and_bounty(request):
    languages = []
    for lang in Issue.LANGUAGES:
        languages.append(lang[0])
    user = request.user

    if request.method == "GET":
        url = request.GET.get("url")
        if url:
            helper = get_issue_helper(request, url)
            issue_data = helper.get_issue(request, url)

            if not "title" in issue_data:
                messages.error(request, "Please provide an valid issue url")
                return redirect("/post")

            form = IssueCreateForm(
                initial={
                    "issueUrl": request.GET.get("url"),
                    "title": issue_data["title"],
                    "content": issue_data["content"] or "Added from Github",
                }
            )
        else:
            form = IssueCreateForm()
        return render(
            request,
            "post.html",
            {
                "languages": languages,
                "form": form,
            },
        )
    if request.method == "POST":
        url = request.POST.get("issueUrl", "")
        if not url:
            messages.error(request, "Please provide an issue url")
            return render(request, "post.html", {"languages": languages})
        try:
            helper = get_issue_helper(request, url)
            issue_data = helper.get_issue(request, url)
            service = Service.objects.get(name=issue_data["service"])
            instance = Issue(
                number=issue_data["number"],
                project=issue_data["project"],
                user=issue_data["user"],
                service=service,
            )
            form = IssueCreateForm(request.POST, instance=instance)

        except Exception as e:
            return render(
                request,
                "post.html",
                {
                    "languages": languages,
                    "message": "Error: " + str(e),
                },
            )

        bounty_form = BountyCreateForm(request.POST)
        bounty_form_is_valid = bounty_form.is_valid()
        if form.is_valid() and bounty_form_is_valid:
            price = bounty_form.cleaned_data["price"]
            if int(price) < 5:
                return render(
                    request,
                    "post.html",
                    {
                        "languages": languages,
                        "message": "Bounty must be greater than $5",
                    },
                )
            try:
                issue = form.save()
            except:
                issue = Issue.objects.get(
                    number=issue_data["number"],
                    project=issue_data["project"],
                    user=issue_data["user"],
                    service=service,
                )

            bounty_instance = Bounty(user=user, issue=issue, price=price)
            if int(request.user.userprofile.balance or 0) >= int(
                request.POST.get("grand_total")
            ):
                profile = request.user.userprofile
                profile.balance = int(request.user.userprofile.balance) - int(
                    request.POST.get("grand_total")
                )
                profile.save()
                bounty_instance.save()
                if not settings.DEBUG:
                    create_comment(issue)
                return redirect(issue.get_absolute_url())
            else:
                data = serializers.serialize(
                    "json",
                    [
                        bounty_instance,
                    ],
                )
                # https://devtools-paypal.com/guide/pay_paypal/python?env=sandbox
                import paypalrestsdk

                paypalrestsdk.configure(
                    {
                        "mode": settings.MODE,
                        "client_id": settings.CLIENT_ID,
                        "client_secret": settings.CLIENT_SECRET,
                    }
                )

                payment = paypalrestsdk.Payment(
                    {
                        "intent": "sale",
                        "payer": {"payment_method": "paypal"},
                        "redirect_urls": {
                            "return_url": request.build_absolute_uri(
                                issue.get_absolute_url()
                            ),
                            "cancel_url": "https://coderbounty.com/post",
                        },
                        "transactions": [
                            {
                                "amount": {
                                    "total": request.POST.get("grand_total"),
                                    "currency": "USD",
                                },
                                "description": "Coderbounty #" + str(issue.id),
                                "custom": data,
                            }
                        ],
                    }
                )

                if payment.create():
                    for link in payment.links:
                        if link.method == "REDIRECT":
                            redirect_url = link.href
                    return redirect(redirect_url)
                else:
                    messages.error(request, payment.error)
                    return render(request, "post.html", {"languages": languages})

        else:
            return render(
                request,
                "post.html",
                {
                    "languages": languages,
                    "message": form.errors,
                    "errors": form.errors,
                    "form": form,
                    "bounty_errors": bounty_form.errors,
                },
            )


def list(request):
    status = request.GET.get("status", "open")
    language = request.GET.get("language")
    sort = request.GET.get("sort", "-created")
    layout = request.GET.get("layout", "grid")

    if sort not in ["-created", "-bounty", "-views", "-modified"]:
        messages.error(request, "invalid sort option")
        return redirect("/list")

    if not any(language in lang for lang in Issue.LANGUAGES) and language:
        messages.error(request, "invalid language")
        return redirect("/list")

    if not any(status in stat for stat in Issue.STATUS_CHOICES) and status != "all":
        messages.error(request, "invalid status")
        return redirect("/list")

    if status == "all":
        issues = Issue.objects.all().order_by(sort)
    else:
        issues = Issue.objects.filter(status=status).order_by(sort)

    if language:
        issues = issues.filter(language=language)

    languages = []
    for lang in Issue.LANGUAGES:
        languages.append(lang[0])

    context = {
        "issues": issues,
        "language": language,
        "languages": languages,
        "status": status,
        "sort": sort,
        "layout": layout,
    }
    if layout == "grid":
        response = render(request, "list.html", context)
    else:
        response = render(request, "newlist.html", context)
    return response


def profile(request):
    """Redirects to profile page if the requested user is loggedin"""
    try:
        return redirect("/profile/" + request.user.username)
    except Exception:
        return redirect("/")


class UserProfileDetailView(DetailView):
    model = get_user_model()
    slug_field = "username"
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, "That user was not found.")
            return redirect("/")
        return super(UserProfileDetailView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        user = super(UserProfileDetailView, self).get_object(queryset)
        UserProfile.objects.get_or_create(user=user)
        return user

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)
        context["activities"] = user_stream(self.get_object(), with_user_activity=True)
        return context


class UserProfileEditView(SuccessMessageMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/edit.html"
    success_message = "Profile saved"

    def get_object(self, queryset=None):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_success_url(self):
        # return reverse("profile", kwargs={'slug': self.request.user})
        return reverse("edit_profile")

    def form_valid(self, form):
        user_id = form.cleaned_data.get("user")
        user = User.objects.get(id=user_id)
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.email = form.cleaned_data.get("email")
        user.save()

        return super(UserProfileEditView, self).form_valid(form)

    def get_success_message(self, cleaned_data):
        return self.success_message


class PostAll(TemplateView):
    template_name = "post_all.html"

    def get_context_data(self, **kwargs):
        # find all github issues
        accounts = {}
        for account in self.request.user.socialaccount_set.all().iterator():
            providers = accounts.setdefault(account.provider, [])
            providers.append(account)

        try:
            service = Service.objects.get(name="Github")
        except Service.DoesNotExist:
            raise Http404("That service was not found.")

        try:
            access_token = SocialToken.objects.get(
                account__user=self.request.user, account__provider="github"
            )
        except Exception as e:
            messages.error(self.request, str(e))
            # return str(e) + 'Not implemented yet - https://github.com/CoderBounty/coderbounty/issues/16'

        # the_url = service.api_url + "/" + accounts['github'][0].extra_data['login'] + "/user/issues"

        # the_url = service.api_url + "/issues"
        # print the_url

        # resp = requests.get(the_url, params={'access_token': access_token}, headers={"content-type": 'application/vnd.github+json'})
        # gres = resp.json()
        # print gres

        # the_url = service.api_url + "/user/issues?filter=all"

        # the_url = 'https://api.github.com/user'

        # /user/issues?filter=all

        # resp = requests.get(the_url, params={'access_token': access_token})
        # user_info = resp.json()

        # resp = requests.get(user_info['repos_url'], params={'access_token': access_token})
        # repos = resp.json()
        # for repo in repos:
        #   if repo['open_issues_count'] > 1:
        #       print repo['name'], repo['open_issues_count']

        # resp = requests.get(user_info['organizations_url'], params={'access_token': access_token})
        # repos = resp.json()
        # print repos
        # for repo in repos:
        #   if repo['open_issues_count'] > 1:
        #       print repo['name'], repo['open_issues_count']

        context = super(PostAll, self).get_context_data(**kwargs)
        # context['leaderboard'] = leaderboard()
        return context


# @cache_page(432000) #5 days
# class LeaderboardView(ListView):
#     template_name = "leaderboard.html"

#     def get_queryset(self):
#         return User.objects.all().annotate(
#             null_position=Count('userprofile__balance')).order_by(
#             '-null_position', '-userprofile__balance', '-last_login')

#     def get_context_data(self, **kwargs):
#         context = super(LeaderboardView, self).get_context_data(**kwargs)
#         context['leaderboard'] = leaderboard()
#         return context


class LeaderboardView(ListView):
    model = User
    paginate_by = 25
    template_name = "leaderboard.html"

    def get_queryset(self):
        return (
            User.objects.filter(payment__amount__gt=0)
            .annotate(total=Sum("payment__amount"))
            .order_by("-total")
        )

    def get_context_data(self, **kwargs):
        context = super(LeaderboardView, self).get_context_data(**kwargs)
        leaderboard_users = (
            User.objects.filter(payment__amount__gt=0)
            .annotate(total=Sum("payment__amount"))
            .order_by("-total")
        )
        paginator = Paginator(leaderboard_users, self.paginate_by)
        page = self.request.GET.get("page")

        try:
            leaderboard_users_paginated = paginator.page(page)
        except PageNotAnInteger:
            leaderboard_users_paginated = paginator.page(1)
        except EmptyPage:
            leaderboard_users_paginated = paginator.page(paginator.num_pages)

        context["leaderboard"] = leaderboard()
        context["object_list"] = leaderboard_users_paginated
        return context


class PayView(DetailView):
    model = Solution

    def get(self, request, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            messages.error(self.request, "That solution was not found.")
            return redirect("/")

        # temporarally until we add creator to issues
        if Bounty.objects.filter(user=self.request.user).filter(
            issue=self.object.issue
        ):

            import paypalrestsdk
            import random
            import string

            paypalrestsdk.configure(
                {
                    "mode": settings.MODE,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                }
            )
            sender_batch_id = "".join(
                random.choice(string.ascii_uppercase) for i in range(12)
            )

            payout = paypalrestsdk.Payout(
                {
                    "sender_batch_header": {
                        "sender_batch_id": sender_batch_id,
                        "email_subject": "You have a payment from Coderbounty",
                    },
                    "items": [
                        {
                            "recipient_type": "EMAIL",
                            "amount": {
                                "value": self.object.issue.bounty(),
                                "currency": "USD",
                            },
                            "receiver": self.object.user.userprofile.payment_service_email,
                            "note": "Thank you for your solution",
                            "sender_item_id": str(self.object.issue),
                        }
                    ],
                }
            )

            if payout.create(sync_mode=True):
                messages.success(
                    self.request,
                    "payout[%s] created successfully"
                    % (payout.batch_header.payout_batch_id),
                )
                self.object.status = Solution.PAID
                self.object.save()
                self.object.issue.winner = self.object.user
                self.object.issue.status = Issue.PAID_STATUS
                self.object.issue.paid = self.object.issue.bounty()
                self.object.issue.save()
                Payment.objects.create(
                    issue=self.object.issue,
                    solution=self.object,
                    user=self.object.user,
                    txn_id=payout.items.get("transaction_id"),
                    amount=self.object.issue.bounty(),
                    created=datetime.datetime.now(),
                    modified=datetime.datetime.now(),
                )

            else:
                messages.error(self.request, payout.error)

        return redirect("/issue/" + str(self.object.issue.id))


class IssueDetailView(DetailView):
    model = Issue
    slug_field = "id"
    template_name = "issue.html"

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except:
            messages.error(self.request, "That issue was not found.")
            return redirect("/")

        if self.request.GET.get("paymentId"):
            import paypalrestsdk

            paypalrestsdk.configure(
                {
                    "mode": settings.MODE,
                    "client_id": settings.CLIENT_ID,
                    "client_secret": settings.CLIENT_SECRET,
                }
            )

            payment = paypalrestsdk.Payment.find(self.request.GET.get("paymentId"))

            custom = payment.transactions[0].custom

            if payment.execute({"payer_id": self.request.GET.get("PayerID")}):
                send_mail(
                    "Processed Payment PayerID"
                    + self.request.GET.get("PayerID")
                    + " paymentID"
                    + self.request.GET.get("paymentId"),
                    "payment occured",
                    "support@coderbounty.com",
                    ["support@coderbounty.com"],
                    html_message="payment occured",
                )
                for obj in serializers.deserialize(
                    "json", custom, ignorenonexistent=True
                ):
                    obj.object.created = datetime.datetime.now()
                    obj.object.checkout_id = self.request.GET.get("checkout_id")
                    obj.save()
                    action.send(
                        self.request.user,
                        verb="placed a $" + str(obj.object.price) + " bounty on ",
                        target=obj.object.issue,
                    )
                    post_to_slack(obj.object)
                    if not settings.DEBUG:
                        create_comment(obj.object.issue)
            else:
                messages.error(request, payment.error)
                send_mail(
                    "Payment error: PayerID"
                    + self.request.GET.get("PayerID")
                    + " paymentID"
                    + self.request.GET.get("paymentId"),
                    "payment error",
                    "support@coderbounty.com",
                    ["support@coderbounty.com"],
                    html_message="payment error",
                )

        return super(IssueDetailView, self).get(request, *args, **kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        comment_service_helper = get_comment_helper(self.get_object().service)

        comment_service_helper.load_comments(self.get_object())
        if self.get_object().status in ("open", "in review"):
            if self.get_object().get_api_data()["state"] == "closed":
                issue = self.get_object()
                if Solution.objects.filter(issue=issue):
                    # process the payment here and mark it as paid if the solution was accepted
                    issue.status = "in review"
                else:
                    issue.status = "closed"
                issue.save()
        if self.request.POST.get("take"):
            if self.request.user.is_authenticated():
                taker = Taker(issue=self.get_object(), user=self.request.user)
                taker.save()
                issue = self.get_object()
                issue.status = "taken"
                issue.save()
                action.send(
                    self.request.user, verb="has taken ", target=self.get_object()
                )
                msg_plain = render_to_string(
                    "email/issue_taken.txt",
                    {
                        "user": self.request.user,
                        "issue": self.get_object(),
                        "time_remaining": taker.time_remaining,
                    },
                )
                msg_html = render_to_string(
                    "email/issue_taken.txt",
                    {
                        "user": self.request.user,
                        "issue": self.get_object(),
                        "time_remaining": taker.time_remaining,
                    },
                )

                send_mail(
                    "You have taken issue: "
                    + self.get_object().project
                    + " issue #"
                    + str(self.get_object().number),
                    msg_plain,
                    "support@coderbounty.com",
                    [self.request.user.email],
                    html_message=msg_html,
                )
            else:
                return redirect(
                    "/accounts/login/?next=/issue/" + str(self.get_object().id)
                )
        if self.request.POST.get("solution"):
            if self.get_object().status not in ("closed", "in review"):

                if self.request.user.is_authenticated():
                    solution = Solution(
                        issue=self.get_object(),
                        user=self.request.user,
                        url=request.POST.get("solution"),
                    )
                    solution.save()
                    issue = self.get_object()
                    issue.status = "in review"
                    issue.save()
                    action.send(
                        self.request.user,
                        verb="posted ",
                        action_object=solution,
                        target=self.get_object(),
                    )

                    bounty_poster = Bounty.objects.filter(issue=self.get_object())[
                        :1
                    ].get()

                    msg_plain = render_to_string(
                        "email/solution_posted.txt",
                        {"user": bounty_poster.user, "issue": self.get_object()},
                    )
                    msg_html = render_to_string(
                        "email/solution_posted.txt",
                        {"user": bounty_poster.user, "issue": self.get_object()},
                    )

                    send_mail(
                        "Coderbounty solution posted on "
                        + self.get_object().project
                        + " issue #"
                        + str(self.get_object().number),
                        msg_plain,
                        "support@coderbounty.com",
                        [bounty_poster.user.email],
                        html_message=msg_html,
                    )

                else:
                    return redirect(
                        "/accounts/login/?next=/issue/" + str(self.get_object().id)
                    )

        return super(IssueDetailView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(IssueDetailView, self).get_context_data(**kwargs)
        context["leaderboard"] = leaderboard()
        context["taker"] = self.get_object().get_taker()
        context["takers"] = Taker.objects.filter(issue=self.get_object()).order_by(
            "-created"
        )
        context["solutions"] = Solution.objects.filter(
            issue=self.get_object()
        ).order_by("-created")
        if not context["taker"] and self.get_object().status == "taken":
            issue = self.get_object()
            issue.status = "open"
            issue.save()
        return context

    def get_object(self):
        object = super(IssueDetailView, self).get_object()
        if self.request.user.is_authenticated():
            object.views = object.views + 1
            object.save()
        return object


def get_bounty_image(request, id):
    try:
        issue = Issue.objects.get(id=id)
    except Issue.DoesNotExist:
        raise Http404("That issue was not found.")

    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw

    size_map = {6: 510, 5: 515, 4: 525, 3: 530, 2: 533, 1: 533}
    img = Image.open("coderbounty/static/images/layout/github-poster.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("coderbounty/static/fonts/regulators/regulators.ttf", 24)
    draw.text(
        (size_map[len(str(issue.bounty()))], 46),
        "${:,}".format(issue.bounty()),
        (163, 75, 51),
        font=font,
    )
    response = HttpResponse(content_type="image/jpeg")
    img.save(response, "JPEG")
    return response
