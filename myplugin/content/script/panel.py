from django.utils.translation import gettext_lazy as _
import horizon

class ScriptPanel(horizon.Panel):
    name = "Script"
    slug = "script"
