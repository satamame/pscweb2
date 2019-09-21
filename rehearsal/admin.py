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


class RehearsalAdmin(admin.ModelAdmin):
    '''管理サイトで稽古のコマを表示する時の設定
    '''
    list_display = ('__str__', 'production', 'date', 'start_time', 'end_time', 'place')
    list_filter = ('production',)


class ApperanceAdmin(admin.ModelAdmin):
    '''管理サイトで出番を表示する時の設定
    '''
    list_display = ('pk', 'production_name', 'scene', 'character')
    list_filter = ('scene__production',)
    
    def production_name(self, obj):
        return str(obj.scene.production)


admin.site.register(Facility)
admin.site.register(Place)
admin.site.register(Rehearsal, RehearsalAdmin)
admin.site.register(Scene, SceneAdmin)
admin.site.register(Actor)
admin.site.register(Character)
admin.site.register(Attendance)
admin.site.register(Appearance, ApperanceAdmin)
admin.site.register(ScnComment, ScnCommentAdmin)
