from django.urls import path
from . import views

app_name = 'production'
urlpatterns = [
    
    # /prod/ -> Production List
    path('', views.ProdList.as_view(), name='prod_list'),
    
    # /prod/prod_create/ -> Production Create
    path('prod_create/', views.ProdCreate.as_view(), name='prod_create'),
]
