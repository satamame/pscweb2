from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from production.models import Production, ProdUser
from .models import Rehearsal, Scene
from .forms import RhslCreateForm

class RhslList(LoginRequiredMixin, ListView):
    '''Rehearsal のリストビュー

    Template 名: rehearsal_list (default)
    '''
    model = Rehearsal
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # prod_id から公演ユーザを取得する
        prod_id=self.kwargs['prod_id']
        prod_users = ProdUser.objects.filter(production__pk=prod_id)
        
        # 自分が含まれていなければアクセス権エラー
        if self.request.user not in [u.user for u in prod_users]:
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        return Rehearsal.objects.filter(production__pk=prod_id)

    def get_context_data(self, **kwargs):
        '''テンプレートに渡すデータ
        '''
        context = super().get_context_data(**kwargs)
        context['prod_id'] = self.kwargs['prod_id']
        return context


class RhslCreate(LoginRequiredMixin, CreateView):
    '''Rehearsal の追加ビュー
    '''
    model = Rehearsal
    form_class = RhslCreateForm
    template_name_suffix = '_create'
    success_url = reverse_lazy('rehearsal:rhsl_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # prod_id から公演ユーザを取得する
        prod_id=self.kwargs['prod_id']
        prod_users = ProdUser.objects.filter(production__pk=prod_id)
        
        # 自分が含まれていなければアクセス権エラー
        if self.request.user not in [u.user for u in prod_users]:
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)


class ScnList(LoginRequiredMixin, ListView):
    '''Scene のリストビュー

    TODO: アクセス権チェック、ソート、Detail へのリンク
    Template 名: scene_list (default)
    '''
    model = Scene
