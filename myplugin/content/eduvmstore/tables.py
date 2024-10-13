from django.urls import reverse

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
  
    name = tables.Column(
        "name",
        verbose_name=_("Image Name"),
        link=lambda record: reverse('horizon:eduvmstore_dashboard:eduvmstore:details',
                                    kwargs={'image_id': record.id})
        # Correct URL with named arguments
    )
   description = tables.Column("short_description", verbose_name=_("Short Description"))
    min_size = tables.Column("size", verbose_name=_("Size"))
    visibility = tables.Column("visibility", verbose_name=_("Visibility"))
    creator = tables.Column("owner", verbose_name=_("Creator"))
    version = tables.Column("version", verbose_name=_("Version"))


    class Meta:
        name = "images"
        verbose_name = _("Images")
        table_actions = (MyFilterAction,)
        multi_select = False  # Disable multi-select if not needed
