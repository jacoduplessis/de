from weasyprint import default_url_fetcher
from django.core.files.storage import default_storage
from django.contrib.staticfiles.finders import find


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
