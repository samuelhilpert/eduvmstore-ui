import horizon

# Neues Dashboard definieren
class MyNewDashboard(horizon.Dashboard):
    name = "EduVMStore"
    slug = "eduvmstore_dashboard"
    panels = ('admin', 'eduvmstore')  # Die beiden existierenden Panels
    panel_groups = ('tutorial_group',)
    default_panel = 'eduvmstore'  # Standardmäßig das Admin-Panel anzeigen

# Dashboard registrieren
horizon.register(MyNewDashboard)
