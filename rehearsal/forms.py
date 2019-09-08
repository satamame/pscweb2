from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from .models import Rehearsal


class RhslCreateForm(forms.ModelForm):
    '''新規稽古作成フォーム
    
    TODO: 日付とかの入力を admin みたいにしたい
    '''
    # start_time = forms.CharField()
    
    class Meta:
        model = Rehearsal
        fields = ('place', 'date', 'start_time', 'end_time')
        widgets = {
            'date': AdminDateWidget(),
        }
