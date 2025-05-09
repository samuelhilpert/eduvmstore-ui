from django.utils.translation import gettext_lazy as _
import horizon


# Todo: bad name
class MySecondPanel(horizon.Panel):
    """
        Custom Horizon panel for the EduVMStore Admin section.

        :attributes:
            - name: The display name for the panel, set to "EduVMStore Admin".
            - slug: A unique identifier for the panel, set to "admin".
    """
    name = _("EduVMStore Admin")
    slug = "admin"
