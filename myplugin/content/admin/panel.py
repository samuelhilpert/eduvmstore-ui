from django.utils.translation import gettext_lazy as _
import horizon


class MySecondPanel(horizon.Panel):
    name = _("EduVMStore Admin")
    slug = "admin"
