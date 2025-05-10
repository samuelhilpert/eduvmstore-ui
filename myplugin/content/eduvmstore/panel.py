from django.utils.translation import gettext_lazy as _
import horizon


class MyPanel(horizon.Panel):
    """
        Custom Horizon panel for the EduVMStore Dashboard.

        :attributes:
            - name: The display name for the panel, set to "Dashboard".
            - slug: A unique identifier for the panel, set to "eduvmstore".
        """
    name = _("Dashboard")
    slug = "eduvmstore"
