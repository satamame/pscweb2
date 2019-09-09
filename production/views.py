from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Production, ProdUser


class ProdList(LoginRequiredMixin, ListView):
    '''Production のリストビュー
    
    ログインユーザの公演のみ表示するため、モデルは ProdUser
    '''
    model = ProdUser
    template_name = 'production/production_list.html'
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        # 自分である ProdUser を取得する
        prod_users = ProdUser.objects.filter(user=self.request.user)
        return prod_users


class ProdCreate(LoginRequiredMixin, CreateView):
    '''Production の追加ビュー
    '''
    model = Production
    fields = ("name", )
    template_name_suffix = '_create'
    success_url = reverse_lazy('production:prod_list')
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存したレコードを取得する
        new_prod = form.save(commit=True)
        
        # 自分を owner として公演ユーザに追加する
        pu = ProdUser(production=new_prod, user=self.request.user,
            is_owner=True)
        pu.save()
        
        messages.success(self.request, str(form.instance) + " を作成しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)
