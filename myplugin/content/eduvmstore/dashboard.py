from horizon import Dashboard, PanelGroup

class EduVMStorePanelGroup(PanelGroup):
    slug = "eduvmstore_group"
    name = "Edu VM Store Group"
    panels = ('eduvmstore', 'admin')

class EduDashboard(Dashboard):
    name = "Edu Dashboard"
    slug = "edu_dashboard"
    panels = ('eduvmstore_group',)
    default_panel = 'eduvmstore'

Horizon.register(EduDashboard)
