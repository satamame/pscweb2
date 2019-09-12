from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from production.models import Production, ProdUser
from .models import Rehearsal, Scene, Place, Facility
from .forms import RhslForm

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
        prod_users = ProdUser.objects.filter(
            production__pk=prod_id, user=self.request.user)
        
        # 自分が含まれていなければアクセス権エラー
        if len(prod_users) < 1:
            raise PermissionDenied
        
        # 自分の prod_user をインスタンス属性として持っておく
        self.prod_user = prod_users[0]
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        return Rehearsal.objects.filter(production__pk=prod_id)

    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        context['prod_id'] = self.kwargs['prod_id']
        return context


class RhslCreate(LoginRequiredMixin, CreateView):
    '''Rehearsal の追加ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production をインスタンス属性として持っておく
        try:
            self.get_prod_from_request()
        except:
            raise
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # リクエストから取った production をセット (表示用)
        context['production'] = self.production
        
        # その公演の稽古場のみ表示するようにする
        # その公演の稽古施設
        facilities = Facility.objects.filter(production=self.production)
        # その施設を含む稽古場
        places = Place.objects.filter(facility__in=facilities)
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(p.id, str(p)) for p in places])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['place'].choices = choices
        
        return context
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production をインスタンス属性として持っておく
        try:
            self.get_prod_from_request()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存しようとするレコードを取得する
        new_rhsl = form.save(commit=False)
        
        # rehearsal の production としてインスタンス属性をセット
        new_rhsl.production = self.production
        
        messages.success(self.request, str(form.instance) + " を作成しました。")
        return super().form_valid(form)

    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)
    
    def get_prod_from_request(self):
        '''リクエストから production を取得し保持する
        
        アクセス件がなければ PermissionDenied を返す
        '''
        # prod_id から自分を含む公演ユーザを取得する
        prod_id=self.kwargs['prod_id']
        prod_users = ProdUser.objects.filter(
            production__pk=prod_id, user=self.request.user)
        
        # 自分が含まれていなければアクセス権エラー
        if len(prod_users) < 1:
            raise PermissionDenied
        
        # 所有権または編集件を持っていなければアクセス権エラー
        if not (prod_users[0].is_owner or prod_users[0].is_editor):
            raise PermissionDenied
        
        # production をインスタンス属性として持っておく
        prods = Production.objects.filter(pk=prod_id)
        if len(prods) < 1:
            raise PermissionDenied
        
        self.production = prods[0]


class RhslUpdate(LoginRequiredMixin, UpdateView):
    '''Rehearsal の更新ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 自分を含む公演ユーザを取得する
        production = self.get_object().production
        prod_users = ProdUser.objects.filter(
            production=production, user=request.user)
        
        # 自分が含まれていなければアクセス権エラー
        if len(prod_users) < 1:
            raise PermissionDenied
        
        # 所有権または編集件を持っていなければアクセス権エラー
        if not (prod_users[0].is_owner or prod_users[0].is_editor):
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # オブジェクトから取った production をセット (表示用)
        production = self.get_object().production
        context['production'] = production

        # その公演の稽古場のみ表示するようにする
        # その公演の稽古施設
        facilities = Facility.objects.filter(production=production)
        # その施設を含む稽古場
        places = Place.objects.filter(facility__in=facilities)
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(p.id, str(p)) for p in places])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['place'].choices = choices
        
        return context
    
    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class ScnList(LoginRequiredMixin, ListView):
    '''Scene のリストビュー

    TODO: アクセス権チェック、ソート、Detail へのリンク
    Template 名: scene_list (default)
    '''
    model = Scene
