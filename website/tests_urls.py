from django import test
from django.urls import reverse
from django.conf import settings
import importlib


class UrlsTest(test.TestCase):
    fixtures = ["initial_data.json"]

    def test_responses(
        self,
        allowed_http_codes=[200, 302, 405],
        credentials={},
        logout_url="",
        default_kwargs={},
        quiet=False,
    ):

        module = importlib.import_module(settings.ROOT_URLCONF)
        if credentials:
            self.client.login(**credentials)

        def check_urls(urlpatterns, prefix=""):
            for pattern in urlpatterns:
                if hasattr(pattern, "url_patterns"):
                    # this is an included urlconf
                    new_prefix = prefix
                    if pattern.namespace:
                        new_prefix = (
                            prefix + (":" if prefix else "") + pattern.namespace
                        )
                    check_urls(pattern.url_patterns, prefix=new_prefix)
                params = {}
                skip = False
                # print(dir(pattern))
                # print(pattern.pattern)
                # print(dir(pattern.pattern))
                regex = pattern.pattern.regex
                if regex.groups > 0:
                    # the url expects parameters
                    # use default_kwargs supplied
                    if regex.groups > len(list(regex.groupindex.keys())) or set(
                        regex.groupindex.keys()
                    ) - set(default_kwargs.keys()):
                        # there are positional parameters OR
                        # keyword parameters that are not supplied in default_kwargs
                        # so we skip the url
                        skip = True
                    else:
                        for key in set(default_kwargs.keys()) & set(
                            regex.groupindex.keys()
                        ):
                            params[key] = default_kwargs[key]
                if hasattr(pattern, "name") and pattern.name:
                    name = pattern.name
                else:
                    # if pattern has no name, skip it
                    skip = True
                    name = ""
                fullname = (prefix + ":" + name) if prefix else name
                if not skip:
                    url = reverse(fullname, kwargs=params)
                    print("testing", url)
                    response = self.client.get(url)
                    self.assertIn(response.status_code, allowed_http_codes)
                    # print status code if it is not 200
                    status = (
                        ""
                        if response.status_code == 200
                        else str(response.status_code) + " "
                    )
                    if not quiet:
                        print((status + url))
                    if url == logout_url and credentials:
                        # if we just tested logout, then login again
                        self.client.login(**credentials)
                else:
                    if not quiet:
                        print(("SKIP " + "regex.pattern" + " " + fullname))

        check_urls(module.urlpatterns)


# from django.conf import settings
# from django.test.testcases import TestCase
# import re

# # from urlparse import urlsplit, urljoin

# from urllib.parse import urlsplit, urljoin


# class GenericTestCase(TestCase):
#     fixtures = []

#     def test_links(self):
#         self.p1 = re.compile(r'href="([^"]*)"')
#         self.p2 = re.compile(r"href='([^']*)'")
#         self.visited_urls = set()
#         self.visit("/", 0)

#     def visit(self, url, depth):
#         print("-" * depth + url),
#         self.visited_urls.add(url)
#         response = self.client.get(url, follow=True)
#         if response.redirect_chain:
#             url = urlsplit(response.redirect_chain[-1][0]).path
#             print(" => " + url)
#             if url in self.visited_urls:
#                 return
#             self.visited_urls.add(url)
#         else:
#             print("")

#         self.assertEquals(response.status_code, 200)

#         refs = self.get_refs(response.content)
#         for relative_url in refs:
#             absolute_url = urljoin(url, relative_url)
#             if not self.skip_url(absolute_url, relative_url):
#                 self.visit(absolute_url, depth + 1)

#     def skip_url(self, absolute_url, relative_url):
#         return (
#             absolute_url in self.visited_urls
#             or ":" in absolute_url
#             or absolute_url.startswith(settings.STATIC_URL)
#             or relative_url.startswith("#")
#         )

#     def get_refs(self, text):
#         urls = set()
#         urls.update(self.p1.findall(text))
#         urls.update(self.p2.findall(text))
#         return urls