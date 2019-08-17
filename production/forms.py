from django import forms
from .models import ProdUser


class ProdUserAdminForm(forms.ModelForm):
    '''管理サイトで公演ユーザを編集する時のフォーム
    '''
    class Meta:
        model = ProdUser
        fields = ('prod_id', 'user_id', 'is_owner', 'is_editor')

    def clean_user_id(self):
        '''ユーザのバリデーション
        '''
        
        # これらの値は、追加の時しか取れない (変更の時は readonly)
        prod_id = self.cleaned_data['prod_id']
        user_id = self.cleaned_data['user_id']
        dupe = ProdUser.objects.filter(prod_id=prod_id, user_id=user_id)
        
        # 追加の時、同じ prod_id と user_id のユーザが見つかったら重複
        if len(dupe) > 0:
            raise forms.ValidationError("{} はすでに {} のユーザです。"
                .format(user_id, prod_id))
        return user_id
