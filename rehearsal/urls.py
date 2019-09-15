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
    # /rhsl/scn_create/1/ -> Scene Create for Production #1
    path('scn_create/<int:prod_id>/', views.ScnCreate.as_view(),
        name='scn_create'),
    # /rhsl/scn_update/1/ -> Scene #1 Update
    path('scn_update/<int:pk>/', views.ScnUpdate.as_view(),
        name='scn_update'),
    # /rhsl/scn_detail/1/ -> Scene #1 Detail
    path('scn_detail/<int:pk>/', views.ScnDetail.as_view(),
        name='scn_detail'),

    # /rhsl/chr_list/1/ -> Character List for Production #1
    path('chr_list/<int:prod_id>/', views.ChrList.as_view(), name='chr_list'),
    # /rhsl/chr_create/1/ -> Character Create for Production #1
    path('chr_create/<int:prod_id>/', views.ChrCreate.as_view(),
        name='chr_create'),
    # /rhsl/chr_update/1/ -> Character #1 Update
    path('chr_update/<int:pk>/', views.ChrUpdate.as_view(),
        name='chr_update'),
    # /rhsl/chr_detail/1/ -> Character #1 Detail
    path('chr_detail/<int:pk>/', views.ChrDetail.as_view(),
        name='chr_detail'),
]
