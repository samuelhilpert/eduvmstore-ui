from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from openstack_dashboard.api import keystone
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
        """Fetch the images from the Glance API and convert owner ID to name."""
        try:
            filters = {}  # Add any filters if needed
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            # Use glance.image_list_detailed from Horizon API
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # Function to convert user or project ID to name
            def get_keystone_entity_name(entity_id):
                keystone_url = self.request.user.endpoint
                headers = {
                    'X-Auth-Token': self.request.user.token.id,
                    'Content-Type': 'application/json'
                }

                # Try to treat the ID as a user ID
                user_url = f"{keystone_url}/v3/users/{entity_id}"
                user_response = requests.get(user_url, headers=headers)

                if user_response.status_code == 200:
                    user_data = user_response.json()
                    return user_data['user']['name']

                # Try to treat the ID as a project ID
                project_url = f"{keystone_url}/v3/projects/{entity_id}"
                project_response = requests.get(project_url, headers=headers)

                if project_response.status_code == 200:
                    project_data = project_response.json()
                    return project_data['project']['name']

                # Raise an error if neither a user nor a project is found
                raise exceptions.NotFound(f"ID {entity_id} is neither a valid user nor a project.")

            # Convert owner ID to name for each image
            image_data = []
            for image in images:
                try:
                    owner_name = get_keystone_entity_name(image.owner)
                except exceptions.NotFound:
                    owner_name = _("Unknown")

                image_data.append({
                    'id': image.id,
                    'name': image.name,
                    'owner_name': owner_name,
                    'size': image.size,
                    'status': image.status,
                    'created_at': image.created_at,
                })

            self._has_more = has_more_data
            return image_data

        except Exception as e:
            self._has_more = False
            error_message = _('Unable to retrieve images: %s') % str(e)
            exceptions.handle(self.request, error_message)
            return []


# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (ImageTab, InstanceTab)  # Added the new ImageTab here
    sticky = True


