from weasyprint import default_url_fetcher
from django.core.files.storage import default_storage
from django.contrib.staticfiles.finders import find
import importlib.resources
from pptx import Presentation
from django.utils.timezone import now


def url_fetcher(url, timeout=5, ssl_context=None):
    # handle local media
    if url.startswith("local:"):
        path = url[6:]
        file_obj = default_storage.open(path, "rb")
        return {
            "file_obj": file_obj,
        }
    if url.startswith("static:"):
        path = url[7:]
        abs_path = find(path)
        return {"file_obj": open(abs_path, "rb")}

    return default_url_fetcher(url, timeout=timeout, ssl_context=ssl_context)


def render_pptx(target):
    prs = Presentation(importlib.resources.open_binary('defects.data', 'anniversaries-report.pptx'))

    prs.slides[0].placeholders[0].text = "Defect Elimination\n\nSignificant Incident Anniversaries"
    prs.slides[0].placeholders[1].text = now().strftime("%B %Y")


    prs.save(target)
