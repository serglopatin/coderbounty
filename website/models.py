from actstream import action
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.db.models import Sum
from django.db.models.signals import post_save
from django.utils.timesince import timeuntil
from string import Template
import datetime
import hashlib
import json
import os
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from django.utils.timezone import utc
import tweepy
from slacker import Slacker
from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.core.cache import cache


class Service(models.Model):
    """
    A web service that allows users to enter issues on projects
    """

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    template = models.CharField(max_length=255)
    regex = models.CharField(max_length=255)
    type = models.CharField(
        max_length=255, choices=(("json", "json"), ("xml", "xml"), ("http", "http"))
    )
    api_url = models.CharField(max_length=255, blank=True)
    link_template = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


def process_comments(sender, instance, *args, **kwargs):
    from .utils import get_comment_helper

    comment_service_helper = get_comment_helper(instance.service)

    if kwargs["created"]:
        comment_service_helper.load_comments(instance)


class Issue(models.Model):
    """
    An issue from a web service entered into Coder Bounty
    """

    OPEN_STATUS = "open"
    IN_REVIEW_STATUS = "in review"
    PAID_STATUS = "paid"
    CLOSED_STATUS = "closed"
    TAKEN_STATUS = "taken"
    STATUS_CHOICES = (
        (OPEN_STATUS, "open"),
        (IN_REVIEW_STATUS, "in review"),
        (TAKEN_STATUS, "taken"),
        (PAID_STATUS, "paid"),
        (CLOSED_STATUS, "closed"),
    )
    LANGUAGES = (
        ("C#", "C#"),
        ("C", "C"),
        ("C++", "C++"),
        ("CSS", "CSS"),
        ("Erlang", "Erlang"),
        ("Go", "Go"),
        ("Haskell", "Haskell"),
        ("HTML", "HTML"),
        ("Java", "Java"),
        ("JavaScript", "JavaScript"),
        ("NodeJS", "NodeJS"),
        ("Perl", "Perl"),
        ("PHP", "PHP"),
        ("Python", "Python"),
        ("Ruby", "Ruby"),
        ("Scala", "Scala"),
        ("Shell", "Shell"),
        ("VB", "VB"),
    )

    # creator = models.ForeignKey(User, related_name="+", null=True, blank=True)
    service = models.ForeignKey(Service, related_name="+", on_delete=models.CASCADE)
    number = models.IntegerField()
    project = models.CharField(max_length=255)
    user = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to="images/projects", blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=400)
    language = models.CharField(max_length=255, choices=LANGUAGES, blank=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default=OPEN_STATUS
    )
    winner = models.ForeignKey(
        User, related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    paid = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    closed_by = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    notified_user = models.BooleanField(default=False)
    views = models.IntegerField(default=1)

    def bounties(self):
        return Bounty.objects.filter(issue=self).order_by("-ends")

    def all_bounties(self):
        return Bounty.objects.filter(issue=self).order_by("-ends")

    def bounty(self):
        return int(self.bounties().aggregate(Sum("price"))["price__sum"] or 0)

    def html_url(self):
        service = self.service
        template = Template(service.link_template)
        return (
            "http://"
            + service.domain
            + template.substitute(
                {"user": self.user, "project": self.project, "number": self.number}
            )
        )

    def api_url(self):
        service = self.service
        template = Template(service.template)
        return service.api_url + template.substitute(
            {"user": self.user, "project": self.project, "number": self.number}
        )

    def get_api_data(self, url=None):
        if self.service.name == "Github":
            if not url:
                url = self.api_url()
            return json.load(urllib.request.urlopen(url))

    def __unicode__(self):
        return "%s issue #%s" % (self.project, self.number)

    def get_absolute_url(self):
        return "/issue/%s" % self.id

    def get_taker(self):
        date_from = datetime.datetime.now() - datetime.timedelta(days=1)
        try:
            return Taker.objects.filter(issue=self, created__gte=date_from).order_by(
                "-created"
            )[0]
        except:
            return False

    class Meta:
        ordering = ["-created"]
        unique_together = ("service", "number", "project")

    # there was an issue when saving from admin
    # def save(self, *args, **kwargs):
    #     #add issue status to activity feed
    #     super(Issue, self).save(*args, **kwargs)
    #     if self.status == Issue.IN_REVIEW_STATUS:
    #         action.send(self.user, verb="is in review now",  target=self.number)
    #     elif self.status == Issue.OPEN_STATUS:
    #         action.send(self.user, verb="opened issue", target=self)
    #     elif self.status == Issue.PAID_STATUS:
    #         action.send(self.user, verb="was paid", target=self.number)


signals.post_save.connect(process_comments, sender=Issue)


class Bounty(models.Model):
    """
    A bounty made on an issue
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    ends = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    checkout_id = models.IntegerField(null=True)

    def time_remaining(self):
        if self.issue.status == Issue.OPEN_STATUS:
            return timeuntil(self.ends, datetime.datetime.now()).split(",")[0]
        return timeuntil(self.ends, self.created).split(",")[0]

    def get_twitter_message(self):
        msg = "Added $%s bounty for %s issue %s. http://coderbounty.com/issue/%s" % (
            self.price,
            self.issue.project,
            self.issue.number,
            self.issue.id,
        )
        return msg

    def save(self, *args, **kwargs):
        if self.pk is None:
            action.send(
                self.user,
                verb="placed a $" + str(self.price) + " bounty on ",
                target=self.issue,
            )
            cache.clear()

        super(Bounty, self).save(*args, **kwargs)


class UserProfile(models.Model):
    CHOICE_PAYMANT_SERVICE = (("paypal", "Paypal"),)

    user = models.OneToOneField(
        User, related_name="userprofile", on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    payment_service = models.CharField(
        max_length=255, null=True, blank=True, choices=CHOICE_PAYMANT_SERVICE
    )
    payment_service_email = models.EmailField(
        max_length=255, null=True, blank=True, default=""
    )

    def avatar(self, size=36):
        for account in self.user.socialaccount_set.all():
            if "avatar_url" in account.extra_data:
                return account.extra_data["avatar_url"]
            elif "picture" in account.extra_data:
                return account.extra_data["picture"]

        gravatar_url = "http://www.gravatar.com/avatar.php?"
        gravatar_url += urllib.parse.urlencode(
            {
                "gravatar_id": hashlib.md5(self.user.email.lower().encode('utf-8')).hexdigest(),
                "default": "retro",
                "size": str(size),
            }
        )
        return gravatar_url

    def avatar_large(self, size=200):
        return self.avatar(size=200)

    def bounties_won(self, size=200):
        return (
            Payment.objects.filter(user=self.user).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

    def save(self, *args, **kwargs):
        if self.pk is None:
            action.send(self.user, verb="signed up")
            cache.clear()
        super(UserProfile, self).save(*args, **kwargs)

    def bounties_placed(self):
        return (
            Bounty.objects.filter(user=self.user).aggregate(Sum("price"))["price__sum"]
            or 0
        )

    def __unicode__(self):
        return self.user.email


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = UserProfile(user=user)
        profile.save()


post_save.connect(create_profile, sender=User)


@receiver(
    user_signed_up, dispatch_uid="some.unique.string.id.for.allauth.user_signed_up"
)
def user_signed_up_(request, user, **kwargs):

    msg_plain = render_to_string("email/welcome.txt", {"user": user})
    msg_html = render_to_string("email/welcome.txt", {"user": user})

    send_mail(
        "Welcome to Coderbounty!",
        msg_plain,
        "support@coderbounty.com",
        [user.email],
        html_message=msg_html,
    )


@receiver(
    user_logged_in, dispatch_uid="some.unique.string.id.for.allauth.user_logged_in"
)
def user_logged_in_(request, user, **kwargs):
    if not settings.TESTING and not settings.DEBUG:
        slack = Slacker(settings.SLACK_API_TOKEN)
        slack.chat.post_message("#logins", request.user.username + " logged in")


TWITTER_MAXLENGTH = getattr(settings, "TWITTER_MAXLENGTH", 140)


def post_to_twitter(sender, instance, *args, **kwargs):
    """
    Post new saved objects to Twitter.
        models.signals.post_save.connect(post_to_twitter, sender=MyModel)
    """

    # avoid to post the same object twice
    if not kwargs.get("created"):
        return False

    # check if there's a twitter account configured

    try:
        consumer_key = os.environ["TWITTER_CONSUMER_KEY"]
        consumer_secret = os.environ["TWITTER_CONSUMER_SECRET"]
        access_key = os.environ["TWITTER_ACCESS_KEY"]
        access_secret = os.environ["TWITTER_ACCESS_SECRET"]
    except KeyError:
        print("WARNING: Twitter account not configured.")
        return False

    # create the twitter message
    try:
        text = instance.get_twitter_message()
    except AttributeError:
        text = str(instance)

    mesg = "%s" % (text)
    if len(mesg) > TWITTER_MAXLENGTH:
        size = len(mesg + "...") - TWITTER_MAXLENGTH
        mesg = "%s..." % (text[:-size])

    if not settings.DEBUG:
        try:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_key, access_secret)
            api = tweepy.API(auth)
            api.update_status(mesg)
        except urllib.error.HTTPError as ex:
            print(("ERROR:", str(ex)))
            return False


def delete_issue(sender, instance, *args, **kwargs):
    if Issue.objects.filter(bounty=instance).exists():
        if not instance.issue.bounties().exists():
            instance.issue.delete()


# def alert_winner(instance, created, **kwargs):
#     email_subj = "Issue %s in review"
#     email_text = """----
#     You've resolved the issue! If all checks out in 3 days you'll receive the bounty.
#     Coder Bounty
#     ---"""
#     if not created and instance.winner:
#         if instance.status == instance.IN_REVIEW_STATUS:
#             instance.winner.email_user(email_subj % instance, email_text)

# signals.post_save.connect(alert_winner, sender=Issue)

signals.post_save.connect(post_to_twitter, sender=Bounty)
signals.post_delete.connect(delete_issue, sender=Bounty)


class Solution(models.Model):

    OPEN = "open"
    MERGED = "merged"
    PAID = "paid"
    STATUS_CHOICES = (
        (OPEN, "open"),
        (MERGED, "merged"),
        (PAID, "paid"),
    )

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    url = models.URLField(help_text="Pull Request URL")
    status = models.CharField(max_length=250, choices=STATUS_CHOICES, default=OPEN)

    def get_absolute_url(self):
        return self.url

    def __unicode__(self):
        return "solution #%s" % self.id

    def notify_owner(self):
        """Email Bounty Owner"""
        pass

    def notify_coder(self, status):
        "notify coder about solution status"
        pass

    def notify_coderbounty(self):
        "notify coderbounty to realse funds"
        pass

    def save(self, *args, **kwargs):
        if self.pk is None:
            # notify owner if there's a new solution
            # a solution for project issue #34 has been submitted by username!  Please take a look at it here0link
            # and either approve or reject it.
            self.notify_owner()

        if self.status == Solution.PAID:
            # notify coder to revision the solution
            # your solution was not approved, please revise it and submit another solution.

            self.notify_coder(status=self.status)

        if self.status == Solution.MERGED:
            # ask cb to realease bounty
            # notify coder that PR has been accepted
            # your solution has been approved, the payment is on it's way!
            self.notify_coderbounty()
            self.notify_coder(status=self.status)

        super(Solution, self).save(*args, **kwargs)


class Taker(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def time_remaining(self):
        date_from = self.created + datetime.timedelta(hours=6)
        end_time = date_from - datetime.datetime.utcnow().replace(tzinfo=utc)
        return str(end_time).split(".")[0]

    def time_remaining_seconds(self):
        date_from = self.created + datetime.timedelta(hours=6)
        return (date_from - datetime.datetime.utcnow().replace(tzinfo=utc)).seconds

    def expired(self):
        return (datetime.datetime.utcnow().replace(tzinfo=utc) - self.created).days >= 3


#    def clean(self):
#       raise ValidationError('The issue is already taken.')

# use paypal IPN tracking
class Payment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=0)
    txn_id = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()


class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    content = models.TextField()
    service_comment_id = models.IntegerField(unique=True)
    username = models.CharField(max_length=255)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    def __unicode__(self):
        return self.content
