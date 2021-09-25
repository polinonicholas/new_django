from urllib.parse import urlparse
from requests.exceptions import ConnectionError
import functools
from bleach.sanitizer import Cleaner
from bleach.linkifier import LinkifyFilter
import re
from django.conf import settings
import requests


def custom_nofollow_maker(attrs, new=False):
    href_key = (None, u"href")

    if href_key not in attrs:
        return attrs

    if attrs[href_key].startswith(u"mailto:"):
        return attrs

    p = urlparse(attrs[href_key])
    if p.netloc not in settings.NOFOLLOW_EXCEPTIONS:
        # Before we add the `rel="nofollow"` let's first check that this is a
        # valid domain at all.
        root_url = p.scheme + "://" + p.netloc
        try:
            response = requests.head(root_url)
            if response.status_code == 301:
                redirect_p = urlparse(response.headers["location"])
                # If the only difference is that it redirects to https instead
                # of http, then amend the href.
                if (
                    redirect_p.scheme == "https"
                    and p.scheme == "http"
                    and p.netloc == redirect_p.netloc
                ):
                    attrs[href_key] = attrs[href_key].replace("http://", "https://")

        except ConnectionError:
            return None

        rel_key = (None, u"rel")
        rel_values = [val for val in attrs.get(rel_key, "").split(" ") if val]
        if "nofollow" not in [rel_val.lower() for rel_val in rel_values]:
            rel_values.append("nofollow")
        attrs[rel_key] = " ".join(rel_values)

    return attrs


cleaner = Cleaner(
    tags=settings.BLEACH_ALLOWED_TAGS,
    filters=[functools.partial(LinkifyFilter, callbacks=[custom_nofollow_maker])],
)

whitespace_start_regex = re.compile(r"^\n*(\s+)", re.M)
def render_comment_text(text):
    html = cleaner.clean(text)

    # So you can write comments with code with left indentation whitespace
    def subber(m):
        return m.group().replace(" ", "&nbsp;")

    html = whitespace_start_regex.sub(subber, html)

    html = html.replace("\n", "<br>")
    return html