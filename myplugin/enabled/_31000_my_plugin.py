PANEL = 'eduvmstore'
PANEL_DASHBOARD = 'identity'
ADD_PANEL = 'myplugin.content.eduvmstore.panel.MyPanel'
ADD_INSTALLED_APPS = ['myplugin']
ADD_ANGULAR_MODULES = ['horizon.dashboard.identity.myplugin.eduvmstore']
AUTO_DISCOVER_STATIC_FILES = True
ADD_JS_FILES = []
ADD_HEADER_SECTIONS = ['myplugin.content.eduvmstore.views.HeaderView',]
