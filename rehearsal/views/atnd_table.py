import json
from operator import attrgetter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied
from rehearsal.models import Rehearsal, Actor, Attendance
from .func import *


class AtndTable(LoginRequiredMixin, TemplateView):
    '''出欠表のビュー
    '''
    template_name = 'rehearsal/attendance_table.html'
    
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
        rehearsals = Rehearsal.objects.filter(production__pk=prod_id)\
            .order_by('date', 'start_time')
        rhsl_list = [{
            'place': str(rhsl.place),
            'date': rhsl.date.strftime('%Y-%m-%d'),
            'start_time': rhsl.start_time.strftime('%H:%M'),
            'end_time': rhsl.end_time.strftime('%H:%M')
        } for rhsl in rehearsals]
        context['rhsls'] = json.dumps(rhsl_list)
        
        # 役者リスト
        actors = Actor.objects.filter(production__pk=prod_id)\
            .order_by('name')
        actr_list = [{
            'name': actr.name,
            'short_name': actr.get_short_name()
        } for actr in actors]
        context['actrs'] = json.dumps(actr_list)
        
        # 役者ごとの出欠の、稽古リストに対応するリスト
        attendances = Attendance.objects.filter(actor__production__pk=prod_id)
        actrs_rhsl_atnds = []
        for actor in actors:
            # その役者の出欠
            actor_atnds = [atnd for atnd in attendances if atnd.actor == actor]
            rhsl_attnds = []
            for rehearsal in rehearsals:
                # その稽古の出欠
                slots = sorted(
                    [atnd for atnd in actor_atnds if atnd.rehearsal == rehearsal],
                    key=attrgetter('from_time')
                )
                atnds = []
                for slot in slots:
                    atnds.append(
                        # 全日の場合
                        '*' if slot.is_allday
                        # 欠席の場合
                        else '-' if slot.is_absent
                        # さもなくば時間帯
                        else slot.from_time.strftime('%H:%M') + '-'
                            + slot.to_time.strftime('%H:%M')
                    )
                rhsl_attnds.append(atnds)
            actrs_rhsl_atnds.append(rhsl_attnds)
        context['actr_atnds'] = json.dumps(actrs_rhsl_atnds)
        
        return context

