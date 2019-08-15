from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from production.models import Production

class ProdList(ListView):

    model = Production


class ProdCreate(CreateView):

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
