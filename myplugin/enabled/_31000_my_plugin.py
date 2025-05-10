# Todo: File names are not really telling what this is. (my_panel, my_second_panel, my_new_dashboard)
#  mb "eduvmstore_panel" "eduvmstore_admin_panel"
# Todo: Same goes for myplugin (i am unsure if we can easily rename this)
PANEL = 'eduvmstore'
PANEL_DASHBOARD = 'eduvmstore_dashboard'
ADD_PANEL = 'myplugin.content.eduvmstore.panel.MyPanel'
ADD_INSTALLED_APPS = ['myplugin']
# ADD_ANGULAR_MODULES = ['horizon.dashboard.eduvmstore_dashboard.myplugin.eduvmstore']
AUTO_DISCOVER_STATIC_FILES = True
ADD_JS_FILES = []
ADD_HEADER_SECTIONS = ['myplugin.content.eduvmstore.views.HeaderView', ]
