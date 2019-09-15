from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from production.models import Production, ProdUser
from .models import Rehearsal, Scene, Place, Facility, Character, Actor
from .forms import RhslForm, ScnForm, ChrForm


def accessing_prod_user(view, prod_id=None):
    '''アクセス情報から対応する ProdUser を取得する
    
    Parameters
    ----------
    view : View
    prod_id : int
        URLconf に prod_id が無い View から呼ぶ時に指定する
    '''
    if not prod_id:
        prod_id=view.kwargs['prod_id']
    prod_users = ProdUser.objects.filter(
        production__pk=prod_id, user=view.request.user)
    if len(prod_users) < 1:
        return None
    return prod_users[0]


class RhslTop(LoginRequiredMixin, TemplateView):
    '''Rehearsal のトップページ
    '''
    template_name = 'rehearsal/rehearsal_top.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # prod_id を view の属性として持っておく
        self.prod_id = prod_user.production.id
        
        return super().get(request, *args, **kwargs)


class RhslList(LoginRequiredMixin, ListView):
    '''Rehearsal のリストビュー

    Template 名: rehearsal_list (default)
    '''
    model = Rehearsal
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 新規作成の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Rehearsal.objects.filter(production__pk=prod_id)\
            .order_by('date', 'start_time')

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
        # production を view の属性として持っておく
        # パーミッションも検査される
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
        # production を view の属性として持っておく
        # パーミッションも検査される
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
        
        # 追加する rehearsal の production として、取っておいた属性をセット
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
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # アクセス情報から公演ユーザを取得する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
        
        # production を view の属性として持っておく
        self.production = prod_user.production


class RhslUpdate(LoginRequiredMixin, UpdateView):
    '''Rehearsal の更新ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
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
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class RhslDetail(LoginRequiredMixin, DetailView):
    '''Rehearsal の詳細ビュー
    '''
    model = Rehearsal

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 編集の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)


class ScnList(LoginRequiredMixin, ListView):
    '''Scene のリストビュー

    Template 名: scene_list (default)
    '''
    model = Scene

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 新規作成の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Scene.objects.filter(production__pk=prod_id)\
            .order_by('sortkey',)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        context['prod_id'] = self.kwargs['prod_id']
        return context


class ScnCreate(LoginRequiredMixin, CreateView):
    '''Scene の追加ビュー
    '''
    model = Scene
    form_class = ScnForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # パーミッションも検査される
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
        
        return context
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_prod_from_request()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存しようとするレコードを取得する
        new_scn = form.save(commit=False)
        
        # 追加する scene の production として、取っておいた属性をセット
        new_scn.production = self.production
        
        messages.success(self.request, str(form.instance)
            + " を作成しました。")
        return super().form_valid(form)

    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:scn_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)
    
    def get_prod_from_request(self):
        '''リクエストから production を取得し保持する
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # アクセス情報から公演ユーザを取得する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
        
        # production を view の属性として持っておく
        self.production = prod_user.production


class ScnUpdate(LoginRequiredMixin, UpdateView):
    '''Scene の更新ビュー
    '''
    model = Scene
    form_class = ScnForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # オブジェクトから取った production をセット (表示用)
        production = self.get_object().production
        context['production'] = production
        
        return context
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:scn_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ScnDetail(LoginRequiredMixin, DetailView):
    '''Scene の詳細ビュー
    '''
    model = Scene

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 編集の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)


class ChrList(LoginRequiredMixin, ListView):
    '''Character のリストビュー

    Template 名: character_list (default)
    '''
    model = Character

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 新規作成の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Character.objects.filter(production__pk=prod_id)\
            .order_by('sortkey',)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        context['prod_id'] = self.kwargs['prod_id']
        return context


class ChrCreate(LoginRequiredMixin, CreateView):
    '''Character の追加ビュー
    '''
    model = Character
    form_class = ChrForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # パーミッションも検査される
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
        
        # その公演の役者のみ表示するようにする
        actors = Actor.objects.filter(production=self.production)
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(a.id, str(a)) for a in actors])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['cast'].choices = choices
        
        return context
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_prod_from_request()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存しようとするレコードを取得する
        new_chr = form.save(commit=False)
        
        # 追加する character の production として、取っておいた属性をセット
        new_chr.production = self.production
        
        messages.success(self.request, str(form.instance)
            + " を作成しました。")
        return super().form_valid(form)

    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:chr_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)
    
    def get_prod_from_request(self):
        '''リクエストから production を取得し保持する
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # アクセス情報から公演ユーザを取得する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
        
        # production を view の属性として持っておく
        self.production = prod_user.production


class ChrUpdate(LoginRequiredMixin, UpdateView):
    '''Character の更新ビュー
    '''
    model = Character
    form_class = ChrForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # オブジェクトから取った production をセット (表示用)
        production = self.get_object().production
        context['production'] = production
        
        # その公演の役者のみ表示するようにする
        actors = Actor.objects.filter(production=production)
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(a.id, str(a)) for a in actors])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['cast'].choices = choices
        
        return context
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''バリデーションに成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:chr_list', kwargs={'prod_id': prod_id})
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ChrDetail(LoginRequiredMixin, DetailView):
    '''Character の詳細ビュー
    '''
    model = Character

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の prod_user を view の属性として持っておく
        # 編集の可否を知るため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
