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
    success_url = reverse_lazy('production:prod_list')

    def get_context_data(self, **kwargs):
        ''' prod_form.html に渡す context
        '''
        context = super().get_context_data(**kwargs)
        context['form_title'] = '新規公演'
        context['submit_label'] = '作成'
        return context

    def form_valid(self, form):
        ''' バリデーションを通った時
        '''
        messages.success(self.request, form.instance.name + " を保存しました")
        return super().form_valid(form)

    def form_invalid(self, form):
        ''' バリデーションに失敗した時
        '''
        messages.warning(self.request, "保存できませんでした")
        return super().form_invalid(form)
