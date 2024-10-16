from django import forms

class AppTemplateForm(forms.Form):
    image = forms.FileField(
        label='Upload Image',
        required=True,
        widget=forms.ClearableFileInput(attrs={'accept': '.iso'})
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
    notice = forms.CharField(
        label="Notice",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    visibility = forms.ChoiceField(
        choices=[('public', 'Public'), ('private', 'Private')],
        label="Visibility",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # System Requirements
    min_ram = forms.IntegerField(
        label="Minimum RAM (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    min_disk = forms.IntegerField(
        label="Minimum Disk (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    min_cores = forms.IntegerField(
        label="Minimum Cores",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    res_per_user_ram = forms.IntegerField(
        label="Minimum RAM per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    res_per_user_disk = forms.IntegerField(
        label="Minimum Disk per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        min_value=0
    )
    res_per_user_cores = forms.IntegerField(
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

    ram = forms.IntegerField(
        label='RAM (GB)',
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    disk = forms.IntegerField(
        label='Disk (GB)',
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    cores = forms.IntegerField(
        label='Cores',
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    root_disk = forms.IntegerField(
        label='Root Disk (GB)',
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    network = forms.CharField(
        label='Network',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
