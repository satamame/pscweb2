from django import forms
from .models import ProdUser


class ProdUserAdminForm(forms.ModelForm):
    '''管理サイトで公演ユーザを編集する時のフォーム
    '''
    class Meta:
        model = ProdUser
        fields = '__all__'

    def clean_user_id(self):
        '''ユーザのバリデーション
        '''
        prod_id = self.cleaned_data['prod_id']
        user_id = self.cleaned_data['user_id']
        dupe = ProdUser.objects.filter(prod_id=prod_id, user_id=user_id)
        if len(dupe) > 0:
            raise forms.ValidationError("{} はすでに {} のユーザです。"
                .format(user_id, prod_id))
        return user_id
