from django.utils.translation import gettext_lazy as _
import horizon


class MyPanel(horizon.Panel):
    name = _("Dashboard")
    slug = "eduvmstore"
