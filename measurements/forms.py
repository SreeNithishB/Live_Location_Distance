from django import forms
from .models import Measurement

class MeasurementModelForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('destination', )
        widgets = {
            'destination': forms.TextInput(attrs={'placeholder': 'city/state/country'}),
        }
