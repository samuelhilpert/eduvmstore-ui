from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from scss.extension.compass.helpers import headers

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
        """Fetch images from Glance API and add placeholder database data."""
        try:
            # Fetch images from Glance API
            filters = {}  # Add any filters if needed
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # Placeholder data for database information
            db_data = self.get_placeholder_db_data()

            # Merge placeholder database data with Glance images
            for image in images:
                # Add placeholder data to each image
                image['description'] = db_data.get(image['id'], {}).get('description', 'No description available')
                image['short_description'] = db_data.get(image['id'], {}).get('short_description', 'N/A')
                image['version'] = db_data.get(image['id'], {}).get('version', '1.0')

            # Return images with extra database fields
            self._has_more = has_more_data
            return images

        except Exception as e:
            self._has_more = False
            error_message = _('Unable to retrieve images: %s') % str(e)
            exceptions.handle(self.request, error_message)
            return []

    def get_placeholder_db_data(self):
        """Placeholder for fetching additional data from the database."""
        # This is a placeholder. Replace with actual DB fetch logic when ready.
        return {
            "1bea47ed-f6a9-463b-b423-14b9cca9ad27": {
                "description": "This is a CirrOS test image used for minimal deployments.",
                "short_description": "CirrOS image",
                "version": "0.3.2"
            },
            "781b3762-9469-4cec-b58d-3349e5de4e9c": {
                "description": "This image includes CFN tools for orchestration tests.",
                "short_description": "Fedora CFN image",
                "version": "F17-x86_64"
            }
            # Add more hardcoded placeholders as needed
        }

# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (ImageTab, )  # Added the new ImageTab here
    sticky = True


