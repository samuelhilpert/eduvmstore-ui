from django.utils.translation import gettext_lazy as _
import horizon

class ExamplePanel(horizon.Panel):
    name = "Example"
    slug = "example"
