from openstack_dashboard.dashboards import dashboard

class EduVMStoreDashboard(dashboard.Dashboard):
    name = "edu_dashboard"
    slug = "edu_dashboard"
    panels = ('eduvmstore',)  # Add your panel here.
    default_panel = 'eduvmstore'

dashboard.EduVMStoreDashboard.register(EduVMStoreDashboard)