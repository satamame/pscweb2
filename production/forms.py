from django import forms
from .models import ProdUser


class ProdUserAdminForm(forms.ModelForm):
    '''管理サイトで公演ユーザを編集する時のフォーム
    '''
    class Meta:
        model = ProdUser
        fields = ('production', 'user', 'is_owner', 'is_editor')

    def clean_user(self):
        '''ユーザのバリデーション
        '''
        # user を検証しているという事は、追加フォームである
        user = self.cleaned_data['user']
        
        # prod_id が入力されていなければ、そっちの検証に任せる
        if 'production' not in self.cleaned_data:
            return user
        
        # 同じ production, user のレコードがあるか検索
        production = self.cleaned_data['production']
        dupe = ProdUser.objects.filter(production=production, user=user)
        
        # 追加なので、同じ production, user のレコードが見つかったら重複
        if len(dupe) > 0:
            raise forms.ValidationError("{} はすでに {} のユーザです。"
                .format(user, production))
        return user