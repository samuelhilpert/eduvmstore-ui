from django import forms

class AppTemplateForm(forms.Form):
    image = forms.ChoiceField(
        choices=[],  # Die Optionen sollten mit Glance-Bildern gefüllt werden
        label="Choose Image",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
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
        widget=forms.Textarea(attrs={'rows': 3, 'style': 'height:60px;'}),
    )
    notice = forms.CharField(
        label="Notice",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
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
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    min_disk = forms.IntegerField(
        label="Minimum Disk (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    min_cores = forms.IntegerField(
        label="Minimum Cores",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    res_per_user_ram = forms.IntegerField(
        label="Minimum RAM per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    res_per_user_disk = forms.IntegerField(
        label="Minimum Disk per User (GB)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    res_per_user_cores = forms.IntegerField(
        label="Minimum Cores per User",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
