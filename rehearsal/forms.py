from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from production.models import Production
from .models import Rehearsal, Scene


class RhslForm(forms.ModelForm):
    '''稽古の追加・更新フォーム
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
            raise forms.ValidationError(
                '終了時刻は開始時刻より遅くしてください。')
        return end_time


class ScnForm(forms.ModelForm):
    '''シーンの追加・更新フォーム
    '''
    class Meta:
        model = Scene
        fields = ('name', 'sortkey', 'length', 'length_auto', 'progress',
            'priority', 'note')