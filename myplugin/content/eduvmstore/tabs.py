# NOTE: This file is not in use at the moment.

from django.utils.translation import gettext_lazy as _

from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from scss.extension.compass.helpers import headers

from myplugin.content.eduvmstore import tables


class ImageTab(tabs.TableTab):
    """
        A tab for displaying and managing images from the Horizon dashboard.

        :attributes:
            - name: The display name for the tab, set to "Images Tab".
            - slug: A unique identifier for this tab, set to "images_tab".
            - table_classes: Reference to the table class for displaying image data.
            - template_name: Template used to render the tab content.
            - preload: If False, the tab content is loaded only when accessed.
    """
    name = _("Images Tab")
    slug = "images_tab"
    table_classes = (tables.ImageTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def has_more_data(self, table):
        """
                Check if there is additional data available for pagination.

                :param Table table: The table object for which to check pagination.
                :return: True if there is more data to load, False otherwise.
                :rtype: bool
        """
        return self._has_more

    def fetch_external_image_data(self):
        """
                Fetch additional image data from an external API.

                :return: A list of image data dictionaries from the external API.
                :rtype: list[dict]
        """
        try:
            response = requests.get("http://localhost:8000/api/app-templates/", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"Error fetching images: {err}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

    def get_images_data(self):
        """
        Retrieve and merge images from the Glance API with data from the external API.

        :return: A list of merged image data dictionaries, including details
                 from both Glance and the database.
        :rtype: list[dict]
        """
        try:
            filters = {}
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            glance_images = images
            external_images = self.fetch_external_image_data()
            external_image_dict = {image['image_id']: image for image in external_images}
            merged_images = []
            for image in glance_images:
                image_id = image['id']
                if image_id in external_image_dict:
                    external_data = external_image_dict[image_id]
                    image['name'] = external_data.get('name', image['name'])
                    image['short_description'] = external_data.get('short_description', 'No description')
                    image['version'] = external_data.get('version', 'N/A')
                else:
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

class MypanelTabs(tabs.TabGroup):
    """
        TabGroup for organizing tabs under the "mypanel" panel in Horizon.

        :attributes:
            - slug: Unique identifier for the tab group, set to "mypanel_tabs".
            - tabs: Tuple of tabs to include in the group, currently contains ImageTab.
            - sticky: If True, the tab group remains visible when scrolling.
        """
    slug = "mypanel_tabs"
    tabs = (ImageTab, )
    sticky = True


