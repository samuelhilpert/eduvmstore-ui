import horizon

# Neues Dashboard definieren
class MyNewDashboard(horizon.Dashboard):
    name = "EduVMStore"
    slug = "eduvmstore_dashboard"
    panels = ()  # Die beiden existierenden Panels
    panel_groups = ('admin', 'eduvmstore', 'tutorial_group')
    default_panel = 'eduvmstore'  # Standardmäßig das Admin-Panel anzeigen

# Dashboard registrieren
horizon.register(MyNewDashboard)
