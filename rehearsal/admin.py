from django.contrib import admin
from .models import Facility, Place, Rehearsal, Scene, Actor, Character,\
    Attendance, Appearance, ScnComment


class AppearanceInline(admin.TabularInline):
    '''シーンの編集画面に出番のリストを表示するための設定
    '''
    model = Appearance
    extra = 0


class ScnCommentInline(admin.StackedInline):
    '''シーンの編集画面にコメントのリストを表示するための設定
    '''
    model = ScnComment
    extra = 0


class SceneAdmin(admin.ModelAdmin):
    inlines = [AppearanceInline, ScnCommentInline]


class ScnCommentAdmin(admin.ModelAdmin):
    '''管理サイトでシーンコメントを表示する時の設定
    '''
    list_display = ('scene', 'create_dt', 'modify_dt', 'comment')
    list_filter = ('scene',)


admin.site.register(Facility)
admin.site.register(Place)
admin.site.register(Rehearsal)
admin.site.register(Scene, SceneAdmin)
admin.site.register(Actor)
admin.site.register(Character)
admin.site.register(Attendance)
admin.site.register(Appearance)
admin.site.register(ScnComment, ScnCommentAdmin)
