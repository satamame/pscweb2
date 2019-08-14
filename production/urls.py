from django.urls import path
from . import views

app_name = 'production'
urlpatterns = [
    # /prod/ -> Production List
    path('', views.ProdList.as_view(), name='prod_list'),
    # /prod/create/ -> Production Create
    path('create/', views.ProdCreate.as_view(), name='prod_create'),
]
