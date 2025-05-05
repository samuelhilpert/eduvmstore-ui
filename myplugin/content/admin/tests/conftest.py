import sys
from unittest import mock
import django
from django.conf import settings

# Mock OpenStack/Horizon modules
sys.modules['horizon'] = mock.MagicMock()
sys.modules['horizon.tabs'] = mock.MagicMock()
sys.modules['horizon.exceptions'] = mock.MagicMock()
sys.modules['openstack_dashboard'] = mock.MagicMock()
sys.modules['openstack_dashboard.api'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.glance'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.nova'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.neutron'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.cinder'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.keystone'] = mock.MagicMock()

# Minimal Django settings konfigurieren
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test',
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
        LANGUAGE_CODE='en-us',
        TIME_ZONE='UTC',
        DEFAULT_CHARSET='utf-8',
        INSTALLED_APPS=[],
    )
    django.setup()
