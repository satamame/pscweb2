from django.urls import path
from . import views

app_name = 'rehearsal'
urlpatterns = [
    
    # /rhsl/1/ -> Rehearsal Top for Production #1
    path('<int:prod_id>/', views.RhslTop.as_view(), name='rhsl_top'),

    # /rhsl/rhsl_list/1/ -> Rehearsal List for Production #1
    path('rhsl_list/<int:prod_id>/', views.RhslList.as_view(),
        name='rhsl_list'),
    
    # /rhsl/rhsl_create/1/ -> Rehearsal Create for Production #1
    path('rhsl_create/<int:prod_id>/', views.RhslCreate.as_view(),
        name='rhsl_create'),
    
    # /rhsl/rhsl_update/1/ -> Rehearsal #1 Update
    path('rhsl_update/<int:pk>/', views.RhslUpdate.as_view(),
        name='rhsl_update'),
    
    # /rhsl/rhsl_detail/1/ -> Rehearsal #1 Detail
    path('rhsl_detail/<int:pk>/', views.RhslDetail.as_view(),
        name='rhsl_detail'),

    # /rhsl/scn_list/1/ -> Scene List for Production #1
    path('scn_list/<int:prod_id>/', views.ScnList.as_view(), name='scn_list'),
]
