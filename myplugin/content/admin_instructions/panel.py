from django.utils.translation import gettext_lazy as _
import horizon

class AdminInstructionsPanel(horizon.Panel):
    name = "Admin Instructions"
    slug = "admin_instructions"
