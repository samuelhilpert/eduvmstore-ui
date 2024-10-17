from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from scss.extension.compass.helpers import headers

from myplugin.content.eduvmstore import tables

# New Tab for displaying images
class ImageTab(tabs.TableTab):
    name = _("Images Tab")
    slug = "images_tab"
    table_classes = (tables.ImageTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def has_more_data(self, table):
        return self._has_more

    # Extended function for fetching external API data
    def fetch_external_image_data(self):
        """Fetch the image data from the external API."""
        try:
            # Replace with your actual URL
            response = requests.get("http://localhost:8000/api/app-templates/")
            if response.status_code == 200:
                return response.json()  # Assuming the API returns a JSON response
            else:
                return []
        except requests.exceptions.RequestException as e:
            # Handle errors in the request
            print(f"Error fetching external data: {e}")
            return []

    def get_images_data(self):
        """Fetch the images from Glance API and combine with external API data."""
        try:
            filters = {}
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            # Fetch images from Glance
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # The images are in the 'images' key, adjust to handle this structure
            glance_images = images.get('images', [])

            # Fetch external API data
            external_images = fetch_external_image_data()

            # Create a dictionary from external images based on image_id
            external_image_dict = {image['image_id']: image for image in external_images}

            # Merge data from Glance and external API
            merged_images = []
            for image in glance_images:
                image_id = image['id']
                if image_id in external_image_dict:
                    external_data = external_image_dict[image_id]
                    # Prioritize the external name
                    image['name'] = external_data.get('name', image['name'])
                    image['short_description'] = external_data.get('short_description', 'No description')
                    image['version'] = external_data.get('version', 'N/A')
                else:
                    # Set default values if no match found
                    image['short_description'] = "No description"
                    image['version'] = "N/A"

                merged_images.append(image)

            self._has_more = has_more_data
            return merged_images

        except Exception as e:
            self._has_more = False
            error_message = _('Unable to retrieve images: %s') % str(e)
            exceptions.handle(self.request, error_message)
            return []

# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (ImageTab, )  # Added the new ImageTab here
    sticky = True


