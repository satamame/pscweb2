from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from production.models import Production, ProdUser

class ProdList(LoginRequiredMixin, ListView):

    model = Production

    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        prod_users = ProdUser.objects.filter(user=self.request.user)
        return Production.objects.filter(
            id__in=[u.production.id for u in prod_users])

class ProdCreate(LoginRequiredMixin, CreateView):

    model = Production
    fields = ("name", )
    template_name_suffix = '_create'
    success_url = reverse_lazy('production:prod_list')

    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, form.instance.name + " を作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)
