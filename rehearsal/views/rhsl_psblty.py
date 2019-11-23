import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from rehearsal.models import Rehearsal, Actor, Attendance, Character, Scene, Appearance
from .view_func import *


class RhslPossibility(LoginRequiredMixin, TemplateView):
    '''稽古可能性のビュー
    '''
    template_name = 'rehearsal/rehearsal_possibility.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # 戻るボタン用に、prod_id を渡す
        prod_id = self.kwargs['prod_id']
        context['prod_id'] = prod_id
        
        # 稽古リスト
        rehearsals = Rehearsal.objects.filter(production__pk=prod_id)
        rhsl_list = [{
            'id': rhsl.id,
            'place': str(rhsl.place),
            'date': rhsl.date.strftime('%Y-%m-%d'),
            'start_time': rhsl.start_time.strftime('%H:%M'),
            'end_time': rhsl.end_time.strftime('%H:%M')
        } for rhsl in rehearsals]
        context['rhsls'] = json.dumps(rhsl_list)
        
        return context
