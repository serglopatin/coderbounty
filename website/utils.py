from django.contrib import messages
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings

from string import Template
from .models import Service, Issue, Bounty, Taker, Comment
from django.contrib.auth.models import User
from django.db.models import Sum
from urllib.parse import urlparse
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import base64
import http.cookiejar
import datetime, time
import re
from django.utils.encoding import smart_str

from hashlib import sha1 as sha_constructor
from hashlib import md5 as md5_constructor

# from django.utils
import json
from django.db.models import Count

from urllib.request import urlopen

import urllib.request, urllib.error, urllib.parse
import requests


def find_api_url(url):
    parsed_url = urlparse(url)
    path_and_query = parsed_url.path + "?" + parsed_url.query
    netloc = parsed_url.netloc
    service = Service.objects.get(domain=netloc)
    template = Template(service.template)
    regex = re.compile(service.regex)
    r = regex.search(path_and_query)
    replaced_url = service.api_url + template.substitute(r.groupdict())
    return replaced_url


def leaderboard():
    return (
        User.objects.filter(payment__amount__gt=0)
        .annotate(total=Sum("payment__amount"))
        .order_by("-total")[:10]
    )


class AbstractIssueHelper(object):

    issue_data = []
    service = None

    def get_issue(self, request, url):
        raise NotImplementedError("Please Implement this method")

    def _get_api_request(self, request, url):
        parsed_url = urlparse(url)
        path_and_query = parsed_url.path
        if parsed_url.query:
            path_and_query = path_and_query + "?" + parsed_url.query
        netloc = parsed_url.netloc
        try:
            service = Service.objects.get(domain=netloc)
        except Exception as e:
            messages.error(request, str(e))
            return str(e)
        template = Template(service.template)
        regex = re.compile(service.regex)
        r = regex.search(path_and_query)
        try:
            replaced_url = service.api_url + template.substitute(r.groupdict())
            self.issue_data = r.groupdict()
            req = urllib.request.Request(
                replaced_url
                + "?client_id="
                + settings.GITHUB_CLIENT_ID
                + "&client_secret="
                + settings.GITHUB_CLIENT_SECRET,
                None,
                {"Content-Type": "application/" + service.type},
            )

        except Exception as e:
            messages.error(request, str(e))
            return str(e)

        return req


class GithubIssueHelper(AbstractIssueHelper):
    def get_issue(self, request, url):
        req = self._get_api_request(request, url)

        try:
            opened_url = urlopen(req)
        except Exception as e:
            messages.error(request, str(e) + url)
            return str(e) + url
        try:
            result = json.load(opened_url)
        except Exception as e:
            messages.error(request, str(e) + str(opened_url))
            return str(e) + str(opened_url)
        data = self.issue_data
        data["status"] = result["state"]
        data["title"] = result["title"]
        data["content"] = result["body"][:400]
        if "closed_by" in result:
            data["closed_by"] = result["closed_by"]
        data["service"] = self.service.name
        data["avatar_url"] = result["user"]["avatar_url"]

        return data


class BitbucketIssueHelper(AbstractIssueHelper):
    def get_issue(self, request, url):
        req = self._get_api_request(request, url)
        data = self.issue_data

        try:
            result = json.load(urlopen(req))
        except Exception as e:
            error = (
                "I wasn't able to retrieve "
                + data["user"]
                + " / "
                + data["project"]
                + " issue #"
                + data["number"]
            )
            if not request:
                return error
            messages.error(request, error)
            return False

        data["status"] = (
            (result["status"] == "new" or result["status"] == "open")
            and "open"
            or "closed"
        )
        data["title"] = result["title"]
        data["content"] = result["content"]
        data["service"] = self.service.name

        return data


class GoogleCodeIssueHelper(AbstractIssueHelper):
    def get_issue(self, request, url):
        req = self._get_api_request(request, url)
        data = self.issue_data

        try:
            url = urlopen(req)
            xml = url.read()
            doc = BeautifulSoup(xml)
        except Exception as e:
            error = (
                "Sorry, I could not get "
                + data["project"]
                + " issue #"
                + data["number"]
            )
            if not request:
                return error
            messages.error(request, error)
            return False

        status = doc.find("issues:state").contents[0]
        data["status"] = (
            (
                status == "new"
                or status == "open"
                or status == "accepted"
                or status == "started"
            )
            and "open"
            or "closed"
        )
        data["title"] = doc.find("entry").find("title").contents[0]
        data["content"] = doc.find("content").contents[0]
        data["service"] = self.service.name

        return data


def get_helper_instance(service, type):
    # ex.: converts "Google Code" to "GoogleCode"
    helper_name = "".join([x.title() for x in service.name.split(" ")])
    helper = globals()["{}{}".format(helper_name, type)]()
    helper.service = service
    return helper


def get_issue_helper(request, url):
    parsed_url = urlparse(url)

    try:
        service = Service.objects.get(domain=parsed_url.netloc)
    except Service.DoesNotExist:
        messages.error(request, "Not specified service")
        return False

    helper = get_helper_instance(service, "IssueHelper")

    return helper


def add_issue_to_database(request):

    issue = request.session.get("issue", False)
    service = Service.objects.get(name=issue["service"])

    try:
        db_issue = Issue.objects.get(
            service=service, number=issue["number"], project=issue["project"]
        )
        if db_issue.status == "paid":
            error = "I see that issue has been closed and paid already."
            messages.error(request, error)
            return False
    except:

        db_issue = Issue(
            service=service,
            number=issue["number"],
            project=issue["project"],
            user="user" in issue and issue["user"] or "",
            title=issue["title"],
            content=issue["content"][:350],
            status=issue["status"],
        )
        filename, file = get_image_for_issue(service, issue)
        if filename:
            db_issue.image.save(filename, file)
        db_issue.save()
        if not settings.DEBUG:
            create_comment(db_issue)

    ends = issue["limit"]
    hour_day = ends[-1]
    number = ends.rstrip(hour_day)
    if hour_day == "h":
        limit = datetime.timedelta(hours=int(number))
    else:
        limit = datetime.timedelta(days=int(number))
    bounty = Bounty(
        user=request.user,
        issue=db_issue,
        price=issue["bounty"],
        ends=datetime.datetime.now() + limit,
    )
    bounty.save()
    # alert_watchers_increase(db_issue, int(request.GET.get("bounty", 0)))
    del request.session["issue"]
    return True


# def alert_watchers_increase(issue, bounty):
#     watchers = Watcher.objects.filter(issue=issue.id, bounty=True)
#     sender = "Coder Bounty<%s>" % settings.SERVER_EMAIL
#     subject = "%s issue #%s bounty is now $%s" % (
#         issue.project,
#         issue.number,
#         issue.bounty(),
#     )
#     text = """$%s was added.
#                 <p>Description: %s.</p>
#                 Go to http://coderbounty.com/#%s to see more.
#             """ % (
#         issue.bounty(),
#         issue.content,
#         issue.id,
#     )
#     for watcher in watchers:
#         message = EmailMultiAlternatives(
#             subject, from_email=sender, to=[watcher.user.email]
#         )

#         message.attach_alternative(text, "text/html")
#         message.send()


def get_image_for_issue(service, issue):

    if service.name == "Google Code":
        image_path = "/p/" + issue["project"] + "/logo"

        img_temp = NamedTemporaryFile()
        try:
            url_opened = urlopen("http://" + service.domain + image_path)
        except Exception as e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue["project"] + ".jpg", File(img_temp)

        img_temp.flush()

    if service.name == "Github":
        org_url = service.api_url + "/orgs/" + issue["project"]
        req = urllib.request.Request(
            org_url, None, {"Content-Type": "application/json"}
        )
        try:
            result = json.load(urlopen(req))
        except Exception as e:
            return False, False
        img_temp = NamedTemporaryFile()
        try:
            url_opened = urlopen(result["avatar_url"])
            file_ext = url_opened.info()["Content-Type"].split("/")[1]
        except Exception as e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue["project"] + "." + file_ext, File(img_temp)

    if service.name == "Bitbucket":
        org_url = (
            service.api_url + "/repositories/" + issue["user"] + "/" + issue["project"]
        )
        req = urllib.request.Request(
            org_url, None, {"Content-Type": "application/json"}
        )
        result = json.load(urlopen(req))
        logo = result["logo"]
        img_temp = NamedTemporaryFile()
        try:
            url_opened = urlopen(logo)
        except Exception as e:
            return False, False
        if url_opened:
            buffer = url_opened.read()
            if len(buffer) > 0:
                img_temp.write(buffer)
                img_temp.flush()
                return issue["project"] + ".png", File(img_temp)

    return False, False


def get_twitter_count():
    twitter_count_url = (
        "http://urls.api.twitter.com/1/urls/count.json?url=http://coderbounty.com"
    )
    req = urllib.request.Request(
        twitter_count_url, None, {"Content-Type": "application/json"}
    )
    result = json.load(urlopen(req))
    return result["count"]


def get_facebook_count():
    facebook_count_url = "https://graph.facebook.com/235042326555141"
    req = urllib.request.Request(
        facebook_count_url, None, {"Content-Type": "application/json"}
    )
    result = json.load(urlopen(req))
    return result["likes"]


def create_comment(issue=None, comment=None):
    if not comment:
        comment = (
            "![Coderbounty](http://www.coderbounty.com/get_bounty_image/"
            + str(issue.id)
            + "/) http://coderbounty.com/issue/"
            + str(issue.id)
        )
    # see if we've commented already and just update
    # try to have one comment that we update
    return globals()[
        "post_" + issue.service.name.replace(" ", "_").lower() + "_comment"
    ](issue, comment)


def post_bitbucket_comment(issue, comment=""):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)

    url = urlopen("https://bitbucket.org/account/signin/")
    html = url.read()
    doc = BeautifulSoup(html)
    csrf_input = doc.find(attrs=dict(name="csrfmiddlewaretoken"))
    csrf_token = csrf_input["value"]

    params = urllib.parse.urlencode(
        dict(
            username=settings.BITBUCKET_USERNAME,
            password=settings.BITBUCKET_PASSWORD,
            csrfmiddlewaretoken=csrf_token,
            next="/",
            submit="Log in",
        )
    )
    req = urllib.request.Request("https://bitbucket.org/account/signin/", params)
    req.add_header("Referer", "https://bitbucket.org/account/signin/")
    url = urlopen(req)

    # we may not need this whole block
    # looked again on 1/2 - definitly looks like we can delete this block, please test
    url = urlopen(issue.html_url)
    # maybe not needed html
    html = url.read()
    csrf_input = doc.find(attrs=dict(name="csrfmiddlewaretoken"))
    csrf_token = csrf_input["value"]

    params = urllib.parse.urlencode(
        dict(content=comment, csrfmiddlewaretoken=csrf_token)
    )
    req = urllib.request.Request(issue.html_url, params)
    req.add_header("Referer", issue.html_url)
    url = urlopen(req)
    try:
        url = urlopen(issue.html_url + "follow")
    except:
        pass
    return True


def post_github_comment(issue, comment=""):
    json_data = '{"body": "' + comment + '"}'
    gh_url = issue.api_url() + "/comments"

    req = urllib.request.Request(gh_url, data=json_data)
    base64string = base64.encodestring(
        "%s:%s" % (settings.GITHUB_USERNAME, settings.GITHUB_PASSWORD)
    )[:-1]
    authheader = "Basic %s" % base64string
    req.add_header("Authorization", authheader)
    urlopen(req)
    return True


def issue_counts():
    counts = {
        "open": Issue.objects.filter(status=Issue.OPEN_STATUS).annotate(Count("id")),
        "in_review": Issue.objects.filter(status=Issue.IN_REVIEW_STATUS).annotate(
            Count("id")
        ),
        "paid": Issue.objects.filter(status=Issue.PAID_STATUS).annotate(Count("id")),
    }
    return counts


def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == "crypt":
        try:
            import crypt
        except ImportError:
            raise ValueError(
                '"crypt" password algorithm not supported in this environment'
            )
        return crypt.crypt(raw_password, salt)

    if algorithm == "md5":
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == "sha1":
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def post_to_slack(bounty):
    if not settings.DEBUG:

        payload = {
            "text": str(bounty.user)
            + " placed a Bounty of $"
            + str(bounty.price)
            + " More details at http://coderbounty.com"
            + str(bounty.issue.get_absolute_url())
        }

        url = "https://hooks.slack.com/services/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"
        r = requests.post(url, data=json.dumps(payload))


def submit_issue_taker(data):
    issueID = data["issue"]
    user = data["user"]
    issuetakenTime = data["issueStartTime"]
    issueTaker = data["user"]
    issueEndtime = issuetakenTime + datetime.timedelta(hours=24)
    issue = Issue.objects.get(pk=issueID)
    issue.status = "taken"
    issue.save()
    taker = Taker(
        is_taken=True,
        issu_id=issueID,
        issue=issue,
        user=user,
        status="taken",
        issueTaken=issuetakenTime,
        issueEnd=issueEndtime,
    )
    taker.save()
    return data


def timecounter(issuetakenTime, duration):
    pass


# time.struct_time(tm_year=2015, tm_mon=11, tm_mday=22, tm_hour=17, tm_min=25, tm_sec=21, tm_wday=6, tm_yday=326, tm_isdst=-1)


class AbstractCommentHelper(object):

    service = None

    def load_comments(self, issue):
        raise NotImplementedError("Please Implement this method")

    def sync_comments(self, issue):
        raise NotImplementedError("Please Implement this method")

    def post_comment(self, issue, comment):
        raise NotImplementedError("Please Implement this method")


class GithubCommentHelper(AbstractCommentHelper):
    def load_comments(self, issue):
        url = issue.api_url() + "/comments"
        comments = issue.get_api_data(url)

        for comment in comments:
            Comment.objects.update_or_create(
                issue=issue,
                service_comment_id=comment["id"],
                defaults={
                    "content": comment["body"],
                    "username": comment["user"]["login"],
                    "created": comment["created_at"],
                    "updated": comment["updated_at"],
                },
            )

    def sync_comments(self, issue):
        pass

    def post_comment(self, issue, comment):
        pass


class BitbucketCommentHelper(AbstractCommentHelper):
    def load_comments(self, issue):
        pass

    def sync_comments(self, issue):
        pass

    def post_comment(self, issue, comment):
        pass


class GoogleCodeCommentHelper(AbstractCommentHelper):
    def load_comments(self, issue):
        pass

    def sync_comments(self, issue):
        pass

    def post_comment(self, issue, comment):
        pass


def get_comment_helper(service):
    helper = get_helper_instance(service, "CommentHelper")
    return helper
