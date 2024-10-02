PANEL = 'mypanel'
PANEL_DASHBOARD = 'identity'
ADD_PANEL = 'myplugin.content.mypanel.panel.MyPanel'
ADD_INSTALLED_APPS = ['myplugin']
ADD_ANGULAR_MODULES = ['horizon.dashboard.identity.myplugin.mypanel']
AUTO_DISCOVER_STATIC_FILES = True
ADD_JS_FILES = []
ADD_HEADER_SECTIONS = ['myplugin.content.mypanel.views.HeaderView',]
