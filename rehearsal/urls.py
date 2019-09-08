from django.urls import path
from . import views

app_name = 'rehearsal'
urlpatterns = [
    # /rhsl/1/ -> Rehearsal List for Production 1
    path('<int:prod_id>/', views.RhslList.as_view(), name='rhsl_list'),
    # /rhsl/1/rhsl_create/ -> Rehearsal Create for Production 1
    path('<int:prod_id>/rhsl_create/', views.RhslCreate.as_view(), name='rhsl_create'),
    # /rhsl/1/scn_list/ -> Scene List for Production 1
    path('<int:prod_id>/scn_list/', views.ScnList.as_view(), name='scn_list'),
]
