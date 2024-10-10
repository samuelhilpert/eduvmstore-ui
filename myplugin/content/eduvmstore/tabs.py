from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from myplugin.content.eduvmstore import tables


class InstanceTab(tabs.TableTab):
    name = _("Instances Tab")
    slug = "instances_tab"
    table_classes = (tables.InstancesTable,)
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_instances_data(self):
        try:
            marker = self.request.GET.get(
                        tables.InstancesTable._meta.pagination_param, None)

            instances, self._has_more = api.nova.server_list(
                self.request,
                search_opts={'marker': marker, 'paginate': True})

            return instances
        except Exception:
            self._has_more = False
            error_message = _('Unable to get instances')
            exceptions.handle(self.request, error_message)

            return []


# New Tab for displaying images
class ImageTab(tabs.TableTab):
    name = _("Images Tab")
    slug = "images_tab"
    table_classes = (tables.ImageTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_images_data(self):
        """Fetch the images from the Glance API."""
        try:
            token_id = self.request.user.token.id
            glance_url = "http://10.0.2.15/v2/images"
            headers = {
                'X-Auth-Token': token_id,
                'Content-Type': 'application/json'
            }

            response = requests.get(glance_url, headers=headers, timeout=10)
            response.raise_for_status()
            images = response.json().get('images', [])
            self._has_more = bool(response.json().get('next', None))  # Check for pagination
            return images
        except Exception:
            self._has_more = False
            error_message = _('Unable to get images')
            exceptions.handle(self.request, error_message)

            return []


# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (InstanceTab, )  # Added the new ImageTab here
    sticky = True


