from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from production.models import Production
from .models import Rehearsal


class RhslCreateForm(forms.ModelForm):
    '''新規稽古作成フォーム
    '''
    class Meta:
        model = Rehearsal
        fields = ('place', 'date', 'start_time', 'end_time', 'note')
        widgets = {
            'date': AdminDateWidget(),
        }
    
    def clean_end_time(self):
        '''end_time が start_time より遅いことのバリデーション
        '''
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']
        
        # end_time が start_time より遅くなければエラー
        if end_time <= start_time:
            raise forms.ValidationError('終了時刻は開始時刻より遅くしてください。')
        return end_time
