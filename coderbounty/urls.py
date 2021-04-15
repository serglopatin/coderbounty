from django.conf.urls import include, url

from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from website.views import (
    UserProfileDetailView,
    IssueDetailView,
    UserProfileEditView,
    LeaderboardView,
    PostAll,
    PayView,
)
from django.views.generic.base import TemplateView
from rest_framework import routers, serializers, viewsets
from website.models import Issue, Service
from django.contrib.auth.models import User
import website
from django.views.generic.base import RedirectView

favicon_view = RedirectView.as_view(url="/static/favicon.ico", permanent=True)

admin.autodiscover()


urlpatterns = (
    url(r"^$", website.views.home, name="home"),
    url(r"^about/$", TemplateView.as_view(template_name="about.html"), name="about"),
    url(r"^accounts/", include("allauth.urls")),
    path("admin/", admin.site.urls),
    url(
        r"^edit_profile/$",
        login_required(UserProfileEditView.as_view()),
        name="edit_profile",
    ),
    url(r"^help/$", TemplateView.as_view(template_name="help.html"), name="help"),
    url(r"^issue/(?P<id>\w+)/$", IssueDetailView.as_view(), name="issue"),
    url(r"^leaderboard/$", LeaderboardView.as_view(), name="leaderboard"),
    url(r"^list/$", website.views.list, name="list"),
    url(
        r"^get_bounty_image/(?P<id>\w+)/$",
        website.views.get_bounty_image,
        name="get_bounty_image",
    ),
    url(r"^parse_url_ajax/$", website.views.parse_url_ajax, name="parse_url_ajax"),
    url(r"^post/$", website.views.create_issue_and_bounty, name="post"),
    url(r"^post_all/$", login_required(PostAll.as_view()), name="post_all"),
    url(r"^profile/$", website.views.profile, name="profile"),
    url(r"^profile/(?P<slug>[^/]+)/$", UserProfileDetailView.as_view(), name="profile"),
    url(r"^robots.txt$", TemplateView.as_view(template_name="robots.txt")),
    url(r"^terms/$", TemplateView.as_view(template_name="terms.html"), name="terms"),
    url(r"^pay/(?P<pk>\d+)/$", login_required(PayView.as_view()), name="pay"),
    url(r"^favicon\.ico$", favicon_view),
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "date_joined", "last_login")


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = (
            "name",
            "domain",
            "template",
            "regex",
            "type",
            "api_url",
            "link_template",
        )


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class IssueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Issue
        fields = (
            "id",
            "service",
            "project",
            "user",
            "number",
            "image",
            "title",
            "content",
            "language",
            "status",
            "winner",
            "paid",
            "closed_by",
            "created",
            "modified",
            "notified_user",
            "views",
        )


class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer


router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"issues", IssueViewSet)
router.register(r"services", ServiceViewSet)

urlpatterns += (
    url(r"^api/", include(router.urls)),
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
)
