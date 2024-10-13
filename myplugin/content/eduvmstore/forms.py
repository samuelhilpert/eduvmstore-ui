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
