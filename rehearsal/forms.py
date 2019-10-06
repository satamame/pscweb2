from django import forms
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from production.models import Production
from .models import Rehearsal, Scene, Character, Actor, Appearance, ScnComment,\
    Attendance


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


class AtndForm(forms.ModelForm):
    '''参加時間の追加・編集フォーム
    '''
    class Meta:
        model = Attendance
        fields = ('is_allday', 'is_absent', 'from_time', 'to_time')
    
    def __init__(self, *args, **kwargs):
        # view で追加したパラメタを抜き取る
        self.actor = kwargs.pop('actor')
        self.rehearsal = kwargs.pop('rehearsal')
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        
        atnds = Attendance.objects.filter(
            rehearsal=self.rehearsal, actor=self.actor)
        atnds = [atnd for atnd in atnds if atnd.id != self.instance.id]
        
        # すでに全日で登録されている場合
        atnds_allday = [atnd for atnd in atnds if atnd.is_allday]
        if len(atnds_allday) > 0:
            raise forms.ValidationError('すでに「全日」で登録されています。')
        
        # すでに欠席で登録されている場合
        atnds_absent = [atnd for atnd in atnds if atnd.is_absent]
        if len(atnds_absent) > 0:
            raise forms.ValidationError('すでに「欠席」で登録されています。')
        
        # 全日が指定されていて、他にも登録がある場合
        is_allday = cleaned_data['is_allday']
        if is_allday and atnds:
            raise forms.ValidationError('「全日」にするには他の登録を削除してください。')
        
        # 欠席が指定されていて、他にも登録がある場合
        is_absent = cleaned_data['is_absent']
        if is_absent and atnds:
            raise forms.ValidationError('「欠席」にするには他の登録を削除してください。')
        
        # 全日と欠席の両方が指定されていた場合
        if is_allday and is_absent:
            raise forms.ValidationError('「全日」「欠席」の両方を選択することは出来ません。')

        # 全日と欠席のどちらかが指定されていた場合はパス
        if is_allday or is_absent:
            return cleaned_data
        
        from_time = cleaned_data['from_time']
        to_time = cleaned_data['to_time']
        # 参加時間が入力されていること
        if not (from_time and to_time):
            raise forms.ValidationError('「全日」「欠席」でない場合、参加時間は必須です。')
        # To が From より遅いこと
        elif to_time <= from_time:
            raise forms.ValidationError('To は From より遅くしてください。')
        else:
            atnds_overlapped = [atnd for atnd in atnds
                if atnd.to_time >= from_time and atnd.from_time <= to_time]
            if atnds_overlapped:
                raise forms.ValidationError('既存の登録と重複する参加時間は指定できません。')
        
        return cleaned_data
    
    # def clean_is_absent(self):
    #     '''「全日」「欠席」の両方が選択されていないことのバリデーション
    #     '''
    #     is_allday = self.instance.is_allday
    #     is_absent = self.instance.is_absent
        
    #     if is_allday and is_absent:
    #         raise forms.ValidationError(
    #             '「全日」「欠席」の両方を選択することは出来ません。')
    #     return is_absent
    
    # def clean_from_time(self):
    #     '''「全日」「欠席」でない場合 from_time があることのバリデーション
    #     '''
    #     from_time = self.cleaned_data['from_time']
    #     # is_allday または is_absent なら None でよい
    #     is_absent = self.cleaned_data['is_absent']
    #     is_allday = self.cleaned_data['is_allday']
    #     if is_allday or is_absent:
    #         return None
        
    #     if not from_time:
    #         raise forms.ValidationError(
    #             '「全日」「欠席」でない場合、参加時間は必須です。')
        
    #     return self.cleaned_data['from_time']
    
    # def clean_to_time(self):
    #     '''to_time が from_time より遅いことのバリデーション
    #     '''
    #     print('to_time が from_time より遅いことのバリデーション')
        
    #     # is_allday または is_absent なら None でよい
    #     is_allday = self.cleaned_data['is_allday']
    #     is_absent = self.cleaned_data['is_absent']
    #     if is_allday or is_absent:
    #         return None
        
    #     to_time = self.cleaned_data['to_time']
    #     if not to_time:
    #         raise forms.ValidationError(
    #             '「全日」「欠席」でない場合、参加時間は必須です。')
        
    #     # to_time が from_time より遅くなければエラー
    #     from_time = self.cleaned_data['from_time']
    #     if to_time <= from_time:
    #         raise forms.ValidationError(
    #             'To は From より遅くしてください。')
    #     return to_time
