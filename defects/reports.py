from django.core.files.storage import default_storage
from django.contrib.staticfiles.finders import find
import importlib.resources
from pptx import Presentation
from django.utils.timezone import now



def render_pptx(target):
    prs = Presentation(importlib.resources.open_binary('defects.data', 'anniversaries-report.pptx'))

    prs.slides[0].placeholders[0].text = "Defect Elimination\n\nSignificant Incident Anniversaries"
    prs.slides[0].placeholders[1].text = now().strftime("%B %Y")


    prs.save(target)
