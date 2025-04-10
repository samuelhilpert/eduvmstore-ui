from django.utils.translation import gettext_lazy as _
import horizon


class TutorialPanel(horizon.Panel):
    """
        Custom Horizon panel for the Tutorial section.

        :attributes:
            - name: The display name for the panel, set to "Tutorial".
            - slug: A unique identifier for the panel, set to "tutorial".
    """
    name = _("Tutorial")
    slug = "tutorial"