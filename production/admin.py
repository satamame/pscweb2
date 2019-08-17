from django.contrib import admin
from .models import Production, ProdUser
from .forms import ProdUserAdminForm


class ProdUserAdmin(admin.ModelAdmin):
    '''管理サイトで公演ユーザを表示する時の設定
    '''
    list_display = ('__str__', 'prod_id', 'user_id', 'is_owner', 'is_editor')
    list_filter = ('prod_id',)
    form = ProdUserAdminForm


admin.site.register(Production)
admin.site.register(ProdUser, ProdUserAdmin)
