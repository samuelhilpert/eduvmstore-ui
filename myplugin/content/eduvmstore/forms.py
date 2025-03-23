# NOTE: AppTemplateForm in this file is not in use at the moment.
from django import forms

class AppTemplateForm(forms.Form):
    """
        Form for creating an app template, but is not in use at the moment.

        :fields:
            - image: Upload field for an image file with specific accepted formats.
            - script: Optional upload field for a script file with accepted formats.
            - name: Text input for the template name.
            - short_description: Text input for a short description of the template.
            - description: Text input for a detailed description of the template.
            - notice: Optional text input for additional notices.
            - visibility: Dropdown for setting template visibility (public or private).
            - min_ram: Optional number input for specifying minimum RAM in GB.
            - min_disk: Optional number input for specifying minimum disk space in GB.
            - min_cores: Optional number input for specifying minimum CPU cores.
            - res_per_user_ram: Optional number input for RAM allocated per user.
            - res_per_user_disk: Optional number input for disk space allocated per user.
            - res_per_user_cores: Optional number input for CPU cores allocated per user.
    """
    image = forms.FileField(
        label='Upload Image',
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': '.raw,.qcow2,.vhd,.vhdx,.vmdk,.iso,.vdi,.ova,.ami'})
    )
    image_id = forms.ChoiceField(
        choices=[],
        required=True,
        label = "Choose existing Images",
        widget = forms.Select(attrs={'class': 'form-control'})
    )

    script = forms.FileField(
        label='Upload Script',
        required=False,
        widget=forms.ClearableFileInput(attrs={'accept': '.sh,.yaml,.yml,.txt'})
    )
    name = forms.CharField(
        label="Name",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    short_description = forms.CharField(
        label="Short Description",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    instantiation_notice = forms.CharField(
        label="Notice",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    public = forms.ChoiceField(
        choices=[('public', 'Public'), ('private', 'Private')],
        label="Visibility",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    # System Requirements
    fixed_ram_gb = forms.DecimalField(
        label="Minimum RAM (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )
    fixed_disk_gb = forms.DecimalField(
        label="Minimum Disk (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )
    fixed_cores = forms.DecimalField(
        label="Minimum Cores",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )
    per_user_ram_gb = forms.DecimalField(
        label="Minimum RAM per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )
    per_user_disk_gb = forms.DecimalField(
        label="Minimum Disk per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )
    per_user_cores = forms.DecimalField(
        label="Minimum Cores per User",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0,
        decimal_places=1
    )


class InstanceForm(forms.Form):
    """
        Form for creating an instance.

        :fields:
            - instance_name: Required text input for the instance name.
            - add_user: Optional text input for adding a user with an optional password.
            - file: Optional file upload field accepting CSV and text files.
            - no_additional_user: Checkbox to indicate no additional user should be added.
            - select_flavor: Dropdown for selecting instance size (flavor).
            - ram: Display-only text field showing RAM allocation.
            - disk: Display-only text field showing disk allocation.
            - cores: Display-only text field showing CPU cores allocation.
            - root_disk: Display-only text field showing root disk size.
            - network: Required text input for specifying the network.
    """
    instance_name = forms.CharField(
        label='Instance Name',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    add_user = forms.CharField(
        label='Add User (<Username> [, <PW>])',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '<Username> [, <PW>]', 'class': 'form-control'})
    )

    file = forms.FileField(
        label='Select File',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file', 'accept': '.csv, .txt'})
    )

    no_additional_user = forms.BooleanField(
        label='No Additional User',
        required=False
    )

    select_flavor = forms.ChoiceField(
        label='Select Flavor',
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    ram = forms.CharField(
        label='RAM (GB)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    disk = forms.CharField(
        label='Disk (GB)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    cores = forms.CharField(
        label='Cores',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    root_disk = forms.CharField(
        label='Root Disk (GB)',
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    network = forms.CharField(
        label='Network',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
# TODO: might be useful for a search feature similiar to openstack images search
# class AppTemplateSearchForm(forms.Form):
#     query = forms.CharField(
#         required=False,
#         label='Search',
#         widget=forms.TextInput(attrs={'placeholder': 'Click here for filter or fulltext search'})
#     )