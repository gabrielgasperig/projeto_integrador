from django import forms
from .models import Hardware, Software, Subscription

class HardwareForm(forms.ModelForm):
    class Meta:
        model = Hardware
        fields = '__all__'

class SoftwareForm(forms.ModelForm):
    class Meta:
        model = Software
        fields = '__all__'

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = '__all__'
