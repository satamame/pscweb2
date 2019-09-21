from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from production.models import Production, ProdUser
from .models import Rehearsal, Scene, Place, Facility, Character, Actor,\
    Appearance, ScnComment
from .forms import RhslForm, ScnForm, ChrForm, ActrForm, ScnApprForm,\
    ChrApprForm, ApprUpdateForm


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


class ProdBaseListView(LoginRequiredMixin, ListView):
    '''アクセス権を検査する ListView の Base class
    '''
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
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        context['prod_id'] = self.kwargs['prod_id']
        return context


class ProdBaseCreateView(LoginRequiredMixin, CreateView):
    '''アクセス権を検査する CreateView の Base class
    '''
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
        instance = form.save(commit=False)
        
        # 追加するレコードの production として、取っておいた属性をセット
        instance.production = self.production
        
        messages.success(self.request, str(instance) + " を追加しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        ''' 追加に失敗した時
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


class ProdBaseUpdateView(LoginRequiredMixin, UpdateView):
    '''アクセス権を検査する UpdateView の Base class
    '''
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
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        ''' 更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ProdBaseDetailView(LoginRequiredMixin, DetailView):
    '''アクセス権を検査する DetailView の Base class
    '''
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


class ProdBaseDeleteView(LoginRequiredMixin, DeleteView):
    '''アクセス権を検査する DeleteView の Base class
    '''
    template_name_suffix = '_delete'

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
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class RhslTop(LoginRequiredMixin, TemplateView):
    '''Rehearsal のトップページ
    '''
    template_name = 'rehearsal/top.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けたハンドラ
        '''
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # production を view の属性として持っておく
        self.production = prod_user.production
        
        return super().get(request, *args, **kwargs)


class RhslList(ProdBaseListView):
    '''Rehearsal のリストビュー

    Template 名: rehearsal_list (default)
    '''
    model = Rehearsal
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Rehearsal.objects.filter(production__pk=prod_id)\
            .order_by('date', 'start_time')


class RhslCreate(ProdBaseCreateView):
    '''Rehearsal の追加ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        # super で production はセットされる
        context = super().get_context_data(**kwargs)
        
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
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class RhslUpdate(ProdBaseUpdateView):
    '''Rehearsal の更新ビュー
    '''
    model = Rehearsal
    form_class = RhslForm
    
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
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class RhslDetail(ProdBaseDetailView):
    '''Rehearsal の詳細ビュー
    '''
    model = Rehearsal


class RhslDelete(ProdBaseDeleteView):
    '''Rehearsal の削除ビュー
    '''
    model = Rehearsal
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:rhsl_list', kwargs={'prod_id': prod_id})
        return url


class ScnList(ProdBaseListView):
    '''Scene のリストビュー

    Template 名: scene_list (default)
    '''
    model = Scene
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Scene.objects.filter(production__pk=prod_id)\
            .order_by('sortkey',)


class ScnCreate(ProdBaseCreateView):
    '''Scene の追加ビュー
    '''
    model = Scene
    form_class = ScnForm
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:scn_list', kwargs={'prod_id': prod_id})
        return url


class ScnUpdate(ProdBaseUpdateView):
    '''Scene の更新ビュー
    '''
    model = Scene
    form_class = ScnForm
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # オブジェクトから取った production をセット (表示用)
        production = self.get_object().production
        context['production'] = production
        
        return context
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:scn_list', kwargs={'prod_id': prod_id})
        return url


class ScnDetail(ProdBaseDetailView):
    '''Scene の詳細ビュー
    '''
    model = Scene
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # このシーンの出番のリスト
        apprs = Appearance.objects.filter(scene=self.get_object())\
            .order_by('character__sortkey')
        context['apprs'] = apprs
        
        # このシーンのコメントのリスト
        cmmts = ScnComment.objects.filter(scene=self.get_object())\
            .order_by('-create_dt')
        context['cmmts'] = cmmts
        
        return context


class ScnDelete(ProdBaseDeleteView):
    '''Scene の削除ビュー
    '''
    model = Scene
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:scn_list', kwargs={'prod_id': prod_id})
        return url


class ChrList(ProdBaseListView):
    '''Character のリストビュー

    Template 名: character_list (default)
    '''
    model = Character
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Character.objects.filter(production__pk=prod_id)\
            .order_by('sortkey',)


class ChrCreate(ProdBaseCreateView):
    '''Character の追加ビュー
    '''
    model = Character
    form_class = ChrForm
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        # super で production はセットされる
        context = super().get_context_data(**kwargs)
        
        # その公演の役者のみ表示するようにする
        actors = Actor.objects.filter(production=self.production)
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(a.id, str(a)) for a in actors])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['cast'].choices = choices
        
        return context
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:chr_list', kwargs={'prod_id': prod_id})
        return url


class ChrUpdate(ProdBaseUpdateView):
    '''Character の更新ビュー
    '''
    model = Character
    form_class = ChrForm
    
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
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:chr_list', kwargs={'prod_id': prod_id})
        return url


class ChrDetail(ProdBaseDetailView):
    '''Character の詳細ビュー
    '''
    model = Character
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)

        # この登場人物の出番のリスト
        apprs = Appearance.objects.filter(character=self.get_object())\
            .order_by('scene__sortkey')
        context['apprs'] = apprs
        
        return context


class ChrDelete(ProdBaseDeleteView):
    '''Character の削除ビュー
    '''
    model = Character
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:chr_list', kwargs={'prod_id': prod_id})
        return url


class ActrList(ProdBaseListView):
    '''Actor のリストビュー

    Template 名: actor_list (default)
    '''
    model = Actor
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_id=self.kwargs['prod_id']
        
        return Actor.objects.filter(production__pk=prod_id)\
            .order_by('name',)


class ActrCreate(ProdBaseCreateView):
    '''Actor の追加ビュー
    '''
    model = Actor
    form_class = ActrForm
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        prod_id = self.production.id
        url = reverse_lazy('rehearsal:actr_list', kwargs={'prod_id': prod_id})
        return url


class ActrUpdate(ProdBaseUpdateView):
    '''Actor の更新ビュー
    '''
    model = Actor
    form_class = ActrForm
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # オブジェクトから取った production をセット (表示用)
        production = self.get_object().production
        context['production'] = production
        
        return context
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:actr_list', kwargs={'prod_id': prod_id})
        return url


class ActrDetail(ProdBaseDetailView):
    '''Actor の詳細ビュー
    '''
    model = Actor


class ActrDelete(ProdBaseDeleteView):
    '''Actor の削除ビュー
    '''
    model = Actor
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.get_object().production.id
        url = reverse_lazy('rehearsal:actr_list', kwargs={'prod_id': prod_id})
        return url


class ScnApprCreate(LoginRequiredMixin, CreateView):
    '''シーン詳細から Appearance を追加する時のビュー

    Template 名: appearance_form (default)
    '''
    model = Appearance
    form_class = ScnApprForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production, scene を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures_from_request()
        except:
            raise
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # その公演の登場人物のみ表示するようにする
        characters = Character.objects.filter(
            production=self.scene.production).order_by('sortkey')
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(c.id, str(c)) for c in characters])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['character'].choices = choices
        
        return context
    
    def get_form_kwargs(self):
        '''フォームに渡す情報を改変する
        '''
        kwargs = super().get_form_kwargs()
        kwargs['scene'] = self.scene
        return kwargs
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production, scene を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures_from_request()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存しようとするレコードを取得する
        new_appr = form.save(commit=False)
        
        # 追加する appearance の scene として、取っておいた属性をセット
        new_appr.scene = self.scene
        
        messages.success(self.request, str(new_appr) + " を追加しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        scn_id = self.scene.id
        url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        return url
    
    def form_invalid(self, form):
        ''' 追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)
    
    def get_fixtures_from_request(self):
        '''リクエストから production, scene を取得し保持する
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # アクセス情報から production, scene を取得し、持っておく
        scenes = Scene.objects.filter(pk=self.kwargs['scn_id'])
        if len(scenes) < 1:
            raise Http404
        self.scene = scenes[0]
        self.production = self.scene.production
        
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied


class ChrApprCreate(LoginRequiredMixin, CreateView):
    '''登場人物詳細から Appearance を追加する時のビュー

    Template 名: appearance_form (default)
    '''
    model = Appearance
    form_class = ChrApprForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production, character を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures_from_request()
        except:
            raise
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # その公演のシーンのみ表示するようにする
        scenes = Scene.objects.filter(
            production=self.character.production).order_by('sortkey')
        # 選択肢を作成
        choices = [('', '---------')]
        choices.extend([(s.id, str(s)) for s in scenes])
        # Form にセット (選択肢以外の値はエラーにしてくれる)
        context['form'].fields['scene'].choices = choices
        
        return context
    
    def get_form_kwargs(self):
        '''フォームに渡す情報を改変する
        '''
        kwargs = super().get_form_kwargs()
        kwargs['character'] = self.character
        return kwargs
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production, character を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures_from_request()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        # 保存しようとするレコードを取得する
        new_appr = form.save(commit=False)
        
        # 追加する appearance の character として、取っておいた属性をセット
        new_appr.character = self.character
        
        messages.success(self.request, str(new_appr) + " を追加しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        chr_id = self.character.id
        url = reverse_lazy('rehearsal:chr_detail', kwargs={'pk': chr_id})
        return url
    
    def form_invalid(self, form):
        ''' 追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)
    
    def get_fixtures_from_request(self):
        '''リクエストから production, character を取得し保持する
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # アクセス情報から production, scene を取得し、持っておく
        characters = Character.objects.filter(pk=self.kwargs['chr_id'])
        if len(characters) < 1:
            raise Http404
        self.character = characters[0]
        self.production = self.character.production
        
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied


class ApprUpdate(LoginRequiredMixin, UpdateView):
    '''Appearance を更新する時のビュー

    Template 名: appearance_form (default)
    '''
    model = Appearance
    form_class = ApprUpdateForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production, scene, character を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures()
        except:
            raise
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production, scene, character を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance)
            + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        pageFrom = self.kwargs['from']
        
        if pageFrom == 'scn':
            scn_id = self.scene.id
            url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        elif pageFrom == 'chr':
            chr_id = self.character.id
            url = reverse_lazy('rehearsal:chr_detail', kwargs={'pk': chr_id})
        else:
            prod_id = self.production.id
            url = reverse_lazy('rehearsal:rhsl_top', kwargs={'prod_id': prod_id})
        
        return url
    
    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)

    def get_fixtures(self):
        '''オブジェクトから production, scene, character を取得し保持する
        
        アクセス権がなければ PermissionDenied を返す
        '''
        # リクエストから from パラメタを取得し page_from として保持する
        self.page_from = self.kwargs['from']

        # オブジェクトから production, scene, character を取得し、持っておく
        self.scene = self.get_object().scene
        self.production = self.scene.production
        self.character = self.get_object().character
        
        # アクセス情報から公演ユーザを取得しパーミッション検査する
        prod_id = self.scene.production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied


class ApprDelete(LoginRequiredMixin, DeleteView):
    '''Appearance の削除ビュー
    '''
    model = Appearance
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production, page_from を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures()
        except:
            raise
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # production, page_from を view の属性として持っておく
        # パーミッションも検査される
        try:
            self.get_fixtures()
        except:
            raise
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        if self.page_from == 'scn':
            scn_id = self.object.scene.id
            url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        elif self.page_from == 'chr':
            chr_id = self.object.character.id
            url = reverse_lazy('rehearsal:chr_detail', kwargs={'pk': chr_id})
        else:
            prod_id = self.object.scene.production.id
            url = reverse_lazy('rehearsal:rhsl_top', kwargs={'prod_id': prod_id})
        
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result
    
    def get_fixtures(self):
        '''production, page_from を view の属性として持っておく
        '''
        self.page_from = self.kwargs['from']
        self.production = self.get_object().scene.production
        
        # オブジェクトから公演ユーザを取得しパーミッション検査する
        prod_id = self.production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権または編集権を持っていなければアクセス権エラー
        if not (prod_user.is_owner or prod_user.is_editor):
            raise PermissionDenied
