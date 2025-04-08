from django.utils.translation import gettext_lazy as _
import horizon

class TutorialPanelOne(horizon.Panel):
    name = _("Tutorial 1")
    slug = "tutorial_1"

class TutorialPanelTwo(horizon.Panel):
    name = _("Tutorial 2")
    slug = "tutorial_2"

class TutorialPanelThree(horizon.Panel):
    name = _("Tutorial 3")
    slug = "tutorial_3"

class TutorialPanelFour(horizon.Panel):
    name = _("Tutorial 4")
    slug = "tutorial_4"

class TutorialPanel(horizon.Panel):
    name = _("Tutorial")
    slug = "tutorial"
    panels = (
        TutorialPanelOne,
        TutorialPanelTwo,
        TutorialPanelThree,
        TutorialPanelFour,
    )
