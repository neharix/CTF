from django.forms import ModelForm, FileField, FileInput
from .models import Xlsxes

class XlsxForm(ModelForm):
    file = FileField(widget=FileInput(), label='')
    class Meta:
        model = Xlsxes
        fields = ['file']
