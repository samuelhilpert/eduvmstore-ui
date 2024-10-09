from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
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
    template_name = ("horizon/common/_detail_table.html")
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_images_data(self):
        try:
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)
            images, self._has_more = api.glance.image_list_detailed(
                self.request,
                marker=marker,
                paginate=True)
            return images
        except Exception:
            self._has_more = False
            error_message = _('Unable to get images')
            exceptions.handle(self.request, error_message)
            return []

# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (ImageTab,)  # Added the new ImageTab here
    sticky = True
