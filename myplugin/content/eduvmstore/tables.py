# NOTE: This file is not in use at the moment.

from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from horizon import tables


class MyFilterAction(tables.FilterAction):
    """
    Custom filter action for the ImageTable to enable search and filtering.

    :name: Unique identifier for the filter action, set to "myfilter".
    """
    name = "myfilter"


class ImageTable(tables.DataTable):
    """
    Table displaying image data with columns for key image attributes.

    :columns:
        - name: Displays the image name with a link to the details page.
        - short_description: Short description of the image.
        - size: Size of the image.
        - visibility: Visibility status of the image (e.g., public/private).
        - creator: The owner or creator of the image.
        - version: Version of the image.
    """

    name = tables.Column(
        "name",
        verbose_name=_("Image Name"),
        link=lambda record: reverse('horizon:eduvmstore_dashboard:eduvmstore:details',
                                    kwargs={'image_id': record['id']})
    )
    short_description = tables.Column("short_description", verbose_name=_("Short Description"))
    size = tables.Column("size", verbose_name=_("Size"))
    visibility = tables.Column("visibility", verbose_name=_("Visibility"))
    creator = tables.Column("owner", verbose_name=_("Creator"))
    version = tables.Column("version", verbose_name=_("Version"))

    class Meta:
        """
        Metadata options for ImageTable.

        :name: Unique table identifier, set to "images".
        :verbose_name: Display name of the table, set to "Images".
        :table_actions: Adds MyFilterAction to the table for filtering capabilities.
        :multi_select: Disables multi-select for this table, set to False.
        """
        name = "images"
        verbose_name = _("Images")
        table_actions = (MyFilterAction,)
        multi_select = False
