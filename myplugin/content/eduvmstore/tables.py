from django.utils.translation import gettext_lazy as _

from horizon import tables

# Custom filter for instances
class MyFilterAction(tables.FilterAction):
    name = "myfilter"


class InstancesTable(tables.DataTable):
    # Define table columns for instances
    name = tables.Column('name',
                         verbose_name=_("Instance Name"))
    status = tables.Column('status',
                           verbose_name=_("Status"))
    zone = tables.Column('availability_zone',
                         verbose_name=_("Availability Zone"))
    image_name = tables.Column('image',
                               verbose_name=_("Image Name"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")
        table_actions = (MyFilterAction,)
        multi_select = False  # Disable multi-select if not needed


# Image Table definition, same as you had but with small improvement on translations
class ImageTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Image Name"),
                         link="horizon:eduvmstore_dashboard:eduvmstore:details",
                         link_kwargs={"image_id": "id"})
    description = tables.Column("id", verbose_name=_("Image Id"))
    creator = tables.Column("owner", verbose_name=_("Creator"))
    min_size = tables.Column("disk_format", verbose_name=_("Disk Format"))
    version = tables.Column("visibility", verbose_name=_("Visibility"))

    class Meta:
        name = "images"
        verbose_name = _("Images")
        table_actions = (MyFilterAction,)
        multi_select = False  # Disable multi-select if not needed