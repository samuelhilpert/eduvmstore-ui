from django.utils.translation import gettext_lazy as _
import horizon


class TutorialPanel(horizon.Panel):
    name = _("Tutorial")
    slug = "tutorial"
