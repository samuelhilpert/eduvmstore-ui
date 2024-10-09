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
    image_name = tables.Column('image_name',
                               verbose_name=_("Image Name"))

    class Meta:
        name = "instances"
        verbose_name = _("Instances")


# Image Table definition, same as you had but with small improvement on translations
class ImageTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("Image Name"))
    description = tables.Column("description", verbose_name=_("Description"))
    creator = tables.Column("creator", verbose_name=_("Creator"))
    min_size = tables.Column("min_size", verbose_name=_("Min. Size (GB)"))
    version = tables.Column("version", verbose_name=_("Version"))

    class Meta:
        name = "images"
        verbose_name = _("Images")
        table_actions = (MyFilterAction,)
        multi_select = False  # Disable multi-select if not needed