import json
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
from .forms import RhslForm, ScnApprForm, ChrApprForm


def accessing_prod_user(view, prod_id=None):
    '''アクセス情報から対応する ProdUser を取得する
    
    Parameters
    ----------
    view : View
        アクセス情報の取得元の View
    prod_id : int
        URLconf に prod_id が無い場合に指定する
    '''
    if not prod_id:
        prod_id=view.kwargs['prod_id']
    prod_users = ProdUser.objects.filter(
        production__pk=prod_id, user=view.request.user)
    if len(prod_users) < 1:
        return None
    return prod_users[0]


def test_edit_permission(view, prod_id=None):
    '''編集権を検査する
    
    Returns
    -------
    prod_user : ProdUser
        編集権を持っているアクセス中の ProdUser
    '''
    # アクセス情報から公演ユーザを取得する
    prod_user = accessing_prod_user(view, prod_id=prod_id)
    if not prod_user:
        raise PermissionDenied
    
    # 所有権または編集権を持っていなければアクセス拒否
    if not (prod_user.is_owner or prod_user.is_editor):
        raise PermissionDenied
    
    return prod_user


class ProdBaseListView(LoginRequiredMixin, ListView):
    '''アクセス権を検査する ListView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の ProdUser を view の属性として持っておく
        # テンプレートで追加ボタンの有無を決めるため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # 戻るボタン, 追加ボタン用の prod_id をセット
        context['prod_id'] = self.kwargs['prod_id']
        
        return context


class ProdBaseCreateView(LoginRequiredMixin, CreateView):
    '''アクセス権を検査する CreateView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 編集権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_edit_permission(self)
        
        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = prod_user.production
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 編集権を検査してアクセス中の公演ユーザを取得する
        prod_user = test_edit_permission(self)
        
        # production を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.production = prod_user.production
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとするレコードの production をセット
        instance = form.save(commit=False)
        instance.production = self.production
        
        messages.success(self.request, str(instance) + " を追加しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)


class ProdBaseUpdateView(LoginRequiredMixin, UpdateView):
    '''アクセス権を検査する UpdateView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = self.get_object().production
        
        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ProdBaseDetailView(LoginRequiredMixin, DetailView):
    '''アクセス権を検査する DetailView の Base class
    '''
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報から公演ユーザを取得する
        prod_id = self.get_object().production.id
        prod_user = accessing_prod_user(self, prod_id=prod_id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の ProdUser を view の属性として持っておく
        # テンプレートで編集ボタンの有無を決めるため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)


class ProdBaseDeleteView(LoginRequiredMixin, DeleteView):
    '''アクセス権を検査する DeleteView の Base class
    '''
    template_name_suffix = '_delete'

    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 編集権を検査する
        test_edit_permission(self, self.get_object().production.id)
        
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
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
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
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
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
        prod_id = self.object.production.id
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
    fields = ('name', 'sortkey', 'length', 'length_auto', 'progress',
        'priority', 'note')
    
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
    fields = ('name', 'sortkey', 'length', 'length_auto', 'progress',
        'priority', 'note')
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
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
        scene = self.get_object()
        apprs = Appearance.objects.filter(scene=scene)\
            .order_by('character__sortkey')
        context['apprs'] = apprs
        
        # このシーンのコメントのリスト (作成日の新しい順)
        cmts = ScnComment.objects.filter(scene=scene)\
            .order_by('-create_dt')
        context['cmts'] = cmts
        
        return context


class ScnDelete(ProdBaseDeleteView):
    '''Scene の削除ビュー
    '''
    model = Scene
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
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
    fields = ('name', 'short_name', 'sortkey', 'cast')
    
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
    fields = ('name', 'short_name', 'sortkey', 'cast')
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
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
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
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
        prod_id = self.object.production.id
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
    fields = ('name', 'short_name')
    
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
    fields = ('name', 'short_name')
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        prod_id = self.object.production.id
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
        prod_id = self.object.production.id
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
        # scene と production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.scene = self.get_scene_from_request()
        self.production = self.scene.production
        
        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
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
        
        # フォーム側でバリデーションに使うので scene を渡す
        kwargs['scene'] = self.scene
        
        return kwargs
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # scene を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.scene = self.get_scene_from_request()
        
        # 編集権を検査する
        test_edit_permission(self, self.scene.production.id)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとする appearance の scene をセット
        new_appr = form.save(commit=False)
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
        '''追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)
    
    def get_scene_from_request(self):
        '''リクエストから scene を取得して返す
        
        scene がなければ 404 エラーを投げる
        '''
        scenes = Scene.objects.filter(pk=self.kwargs['scn_id'])
        if len(scenes) < 1:
            raise Http404
        
        return scenes[0]


class ChrApprCreate(LoginRequiredMixin, CreateView):
    '''登場人物詳細から Appearance を追加する時のビュー

    Template 名: appearance_form (default)
    '''
    model = Appearance
    form_class = ChrApprForm
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # character と production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.character = self.get_character_from_request()
        self.production = self.character.production
        
        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
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
        
        # フォーム側でバリデーションに使うので character を渡す
        kwargs['character'] = self.character
        
        return kwargs
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # character を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.character = self.get_character_from_request()
        
        # 編集権を検査する
        test_edit_permission(self, self.character.production.id)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとする appearance の character をセット
        new_appr = form.save(commit=False)
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
        '''追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)
    
    def get_character_from_request(self):
        '''リクエストから character を取得して返す
        
        character がなければ 404 エラーを投げる
        '''
        characters = Character.objects.filter(pk=self.kwargs['chr_id'])
        if len(characters) < 1:
            raise Http404
        
        return characters[0]


class ApprUpdate(LoginRequiredMixin, UpdateView):
    '''Appearance を更新する時のビュー

    Template 名: appearance_form (default)
    '''
    model = Appearance
    fields = ('lines_num', 'lines_auto')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # page_from を view の属性として持っておく
        # テンプレートでリンクの URL を決めるため
        self.page_from = self.kwargs['from']
        
        # scene, character, production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.scene = self.get_object().scene
        self.character = self.get_object().character
        self.production = self.scene.production
        
        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 編集権を検査する
        test_edit_permission(self, self.get_object().scene.production.id)
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance)
            + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        page_from = self.kwargs['from']
        
        if page_from == 'scn':
            scn_id = self.object.scene.id
            url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        elif page_from == 'chr':
            chr_id = self.object.character.id
            url = reverse_lazy('rehearsal:chr_detail', kwargs={'pk': chr_id})
        else:
            prod_id = self.object.scene.production.id
            url = reverse_lazy('rehearsal:rhsl_top', kwargs={'prod_id': prod_id})
        
        return url
    
    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class ApprDelete(LoginRequiredMixin, DeleteView):
    '''Appearance の削除ビュー
    '''
    model = Appearance
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # page_from を view の属性として持っておく
        # テンプレートでリンクの URL を決めるため
        self.page_from = self.kwargs['from']

        # production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.production = self.get_object().scene.production

        # 編集権を検査する
        test_edit_permission(self, self.production.id)
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 編集権を検査する
        test_edit_permission(self, self.get_object().scene.production.id)
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        page_from = self.kwargs['from']
        
        if page_from == 'scn':
            scn_id = self.object.scene.id
            url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        elif page_from == 'chr':
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


class ScnCmtCreate(LoginRequiredMixin, CreateView):
    '''シーン詳細から ScnComment を追加する時のビュー

    Template 名: scn_comment_form (default)
    '''
    model = ScnComment
    fields = ('comment',)
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # scene と production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.scene = self.get_scene_from_request()
        self.production = self.scene.production
        
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        # 編集権は不要
        prod_user = accessing_prod_user(self, self.production.id)
        if not prod_user:
            raise PermissionDenied
        
        # アクセス中の ProdUser を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.prod_user = prod_user
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # scene を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.scene = self.get_scene_from_request()
        
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        # 編集権は不要
        prod_user = accessing_prod_user(self, self.scene.production.id)
        if not prod_user:
            raise PermissionDenied
        
        # prod_user を view の属性として持っておく
        # 保存時にインスタンスにセットするため
        self.prod_user = prod_user
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとする ScnComment の scene, mod_prod_user をセット
        new_cmt = form.save(commit=False)
        new_cmt.scene = self.scene
        new_cmt.mod_prod_user = self.prod_user
        new_cmt.save()
        
        messages.success(self.request, str(new_cmt) + " を追加しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        scn_id = self.scene.id
        url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        return url
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "追加できませんでした。")
        return super().form_invalid(form)
    
    def get_scene_from_request(self):
        '''リクエストから scene を取得して返す
        
        scene がなければ 404 エラーを投げる
        '''
        scenes = Scene.objects.filter(pk=self.kwargs['scn_id'])
        if len(scenes) < 1:
            raise Http404
        
        return scenes[0]


class ScnCmtUpdate(LoginRequiredMixin, UpdateView):
    '''シーン詳細から ScnComment を更新する時のビュー

    Template 名: scn_comment_form (default)
    '''
    model = ScnComment
    fields = ('comment',)
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # コメントの編集権を検査してアクセス中の公演ユーザを取得する
        # テンプレートで固定要素として表示するため
        self.prod_user = self.test_cmt_permission()
        
        # scene と production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.scene = self.get_object().scene
        self.production = self.scene.production
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # コメントの編集権を検査してアクセス中の公演ユーザを取得する
        # 保存時にインスタンスにセットするため
        self.prod_user = self.test_cmt_permission()
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 追加しようとする ScnComment の mod_prod_user をセット
        new_cmt = form.save(commit=False)
        new_cmt.mod_prod_user = self.prod_user
        new_cmt.save()
        
        messages.success(self.request, str(new_cmt) + " を更新しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        scn_id = self.object.scene.id
        url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        return url
    
    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)
    
    def test_cmt_permission(self):
        '''コメントの編集権を検査する
        '''
        scn_cmt = self.get_object()
        
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self, scn_cmt.scene.production.id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権も編集権なく、記入者でもない場合はアクセス拒否
        if not(prod_user.is_owner or prod_user.is_editor
                or prod_user == scn_cmt.mod_prod_user):
            raise PermissionDenied
        
        return prod_user


class ScnCmtDelete(LoginRequiredMixin, DeleteView):
    '''ScnComment の削除ビュー
    '''
    model = ScnComment
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # コメントの編集権を検査してアクセス中の公演ユーザを取得する
        # テンプレートで固定要素として表示するため
        self.prod_user = self.test_cmt_permission()
        
        # scene と production を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.scene = self.get_object().scene
        self.production = self.scene.production
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # コメントの編集権を検査する
        self.test_cmt_permission()
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        scn_id = self.object.scene.id
        url = reverse_lazy('rehearsal:scn_detail', kwargs={'pk': scn_id})
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result
    
    def test_cmt_permission(self):
        '''コメントの編集権を検査する
        '''
        scn_cmt = self.get_object()
        
        # アクセス情報から公演ユーザを取得しアクセス権を検査する
        prod_user = accessing_prod_user(self, scn_cmt.scene.production.id)
        if not prod_user:
            raise PermissionDenied
        
        # 所有権も編集権なく、記入者でもない場合はアクセス拒否
        if not(prod_user.is_owner or prod_user.is_editor
                or prod_user == scn_cmt.mod_prod_user):
            raise PermissionDenied
        
        return prod_user


class ApprTable(LoginRequiredMixin, TemplateView):
    '''香盤表のビュー
    '''
    template_name = 'rehearsal/appearance_table.html'
    
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
        
        # シーン名リスト
        scenes = Scene.objects.filter(production__pk=prod_id)\
            .order_by('sortkey')
        context['scenes'] = json.dumps([scn.name for scn in scenes])
        
        # 登場人物名リスト
        characters = Character.objects.filter(production__pk=prod_id)\
            .order_by('sortkey')
        context['characters'] = json.dumps([chr.short_name for chr in characters])
        
        # 役者名リスト
        actors = Actor.objects.filter(production__pk=prod_id)
        context['cast'] = json.dumps([actr.short_name for actr in actors])
        
        # 登場人物の出番 (セリフ数) のリスト
        scenes_chr_apprs = []
        for scene in scenes:
            # とりあえず人数分のリストを作る
            chr_apprs = []
            for character in characters:
                apprs = Appearance.objects.filter(
                    scene=scene, character=character)
                if len(apprs) > 0:
                    chr_apprs.append(apprs[0])
                else:
                    # 出番のないところには None を入れておく
                    chr_apprs.append(None)
            
            # 出番のある人だけのリスト
            valid_apprs = [appr for appr in chr_apprs if appr]
            appr_count = len(valid_apprs)
            # セリフ数が「自動」でない人だけのリスト
            line_num_apprs = [appr for appr in valid_apprs if not appr.lines_auto]
            # シーン内のセリフ数の合計
            lines_sum = sum([appr.lines_num for appr in line_num_apprs])
            # セリフ数が自動でない人がいればセリフ数の平均を取っておく
            if len(line_num_apprs) > 0:
                mean = lines_sum / len(line_num_apprs)
            else:
                mean = 1
            
            # このシーンのセリフ数のリスト
            scn_apprs = []
            for appr in chr_apprs:
                if appr:
                    # セリフ数が自動なら平均値を入れる
                    if appr.lines_auto:
                        scn_apprs.append(mean)
                    else:
                        scn_apprs.append(appr.lines_num)
                else:
                    # 出番がないなら0を入れる
                    scn_apprs.append(0)
            
            scenes_chr_apprs.append(scn_apprs)
        context['chr_apprs'] = json.dumps(scenes_chr_apprs)
        
        # 役者の出番 (セリフ数) のリスト
        cast_for_chrs = []
        for character in characters:
            # 各登場人物のキャストが、actors の何番目にあるかのリスト
            try:
                actr_idx = list(actors).index(character.cast)
            except ValueError:
                # なければ -1
                actr_idx = -1
            cast_for_chrs.append(actr_idx)
        
        scenes_cast_apprs = []
        for chr_apprs in scenes_chr_apprs:
            actr_apprs = []
            for actr_idx, actr in enumerate(actors):
                lines_num = 0
                # 登場人物の各キャストについて
                for chr_idx, cast in enumerate(cast_for_chrs):
                    # インデックスが等しければ、その登場人物のセリフ数を足す
                    if cast == actr_idx:
                        lines_num += chr_apprs[chr_idx]
                actr_apprs.append(lines_num)
            scenes_cast_apprs.append(actr_apprs)
        context['cast_apprs'] = json.dumps(scenes_cast_apprs)
        
        return context
