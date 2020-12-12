from django import forms
from django.core import validators
from .models import Listing, Category


class ListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Description", widget=forms.Textarea)
    price = forms.DecimalField(label="Starting Bid", localize=False, max_digits=9, decimal_places=2)
    url = forms.URLField(label="Photo URL", required=False)
    category = forms.ChoiceField(label="Category", required=False, choices=[('', "Choose Category")]+[(category.id, category.name) for category in Category.objects.all()])


class BidForm(forms.Form):
    bid = forms.DecimalField(label=False, localize=False, max_digits=9, decimal_places=2, widget=forms.TextInput(attrs={'placeholder': 'Bid'}), validators=[validators.DecimalValidator])


class ListingModelForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ('title', 'description', 'price', 'url', 'category')
