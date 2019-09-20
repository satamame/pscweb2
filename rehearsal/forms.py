from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from production.models import Production
from .models import Rehearsal, Scene, Character, Actor, Appearance


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


class ChrForm(forms.ModelForm):
    '''登場人物の追加・更新フォーム
    '''
    class Meta:
        model = Character
        fields = ('name', 'short_name', 'sortkey', 'cast')


class ActrForm(forms.ModelForm):
    '''役者の追加・更新フォーム
    '''
    class Meta:
        model = Actor
        fields = ('name', 'short_name')


class ScnApprForm(forms.ModelForm):
    '''シーンへの出番の追加フォーム
    '''
    class Meta:
        model = Appearance
        fields = ('character', 'lines_num', 'lines_auto')
    
    def __init__(self, *args, **kwargs):
        # view で追加したパラメタを抜き取る
        self.scene = kwargs.pop('scene')
        super().__init__(*args, **kwargs)
    
    def clean_character(self):
        '''同じ登場人物を追加していないことのバリデーション
        '''
        character = self.cleaned_data['character']
        dupe = Appearance.objects.filter(scene=self.scene, character=character)
        if len(dupe) > 0:
            raise forms.ValidationError(
                'その人物はすでに登場しています。')
        return character


class ChrApprForm(forms.ModelForm):
    '''登場人物への出番の追加フォーム
    '''
    class Meta:
        model = Appearance
        fields = ('scene', 'lines_num', 'lines_auto')
    
    def __init__(self, *args, **kwargs):
        # view で追加したパラメタを抜き取る
        self.character = kwargs.pop('character')
        super().__init__(*args, **kwargs)
    
    def clean_scene(self):
        '''同じシーンを追加していないことのバリデーション
        '''
        scene = self.cleaned_data['scene']
        dupe = Appearance.objects.filter(scene=scene, character=self.character)
        if len(dupe) > 0:
            raise forms.ValidationError(
                'そのシーンにはすでに登場しています。')
        return scene


class ApprUpdateForm(forms.ModelForm):
    '''出番の更新フォーム
    '''
    class Meta:
        model = Appearance
        fields = ('lines_num', 'lines_auto')
