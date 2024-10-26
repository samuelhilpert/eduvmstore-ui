from django import forms

class AppTemplateForm(forms.Form):
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
    fixed_ram_gb = forms.IntegerField(
        label="Minimum RAM (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    fixed_disk_gb = forms.IntegerField(
        label="Minimum Disk (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    fixed_cores = forms.IntegerField(
        label="Minimum Cores",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    per_user_ram_gb = forms.IntegerField(
        label="Minimum RAM per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    per_user_disk_gb = forms.IntegerField(
        label="Minimum Disk per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    per_user_cores = forms.IntegerField(
        label="Minimum Cores per User",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )


class InstanceForm(forms.Form):
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
