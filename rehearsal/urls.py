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
    # /rhsl/rhsl_delete/1/ -> Rehearsal #1 Delete
    path('rhsl_delete/<int:pk>/', views.RhslDelete.as_view(),
        name='rhsl_delete'),
    
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
    # /rhsl/scn_delete/1/ -> Scene #1 Delete
    path('scn_delete/<int:pk>/', views.ScnDelete.as_view(),
        name='scn_delete'),

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
    # /rhsl/chr_delete/1/ -> Character #1 Delete
    path('chr_delete/<int:pk>/', views.ChrDelete.as_view(),
        name='chr_delete'),

    # /rhsl/actr_list/1/ -> Actor List for Production #1
    path('actr_list/<int:prod_id>/', views.ActrList.as_view(), name='actr_list'),
    # /rhsl/actr_create/1/ -> Actor Create for Production #1
    path('actr_create/<int:prod_id>/', views.ActrCreate.as_view(),
        name='actr_create'),
    # /rhsl/actr_update/1/ -> Actor #1 Update
    path('actr_update/<int:pk>/', views.ActrUpdate.as_view(),
        name='actr_update'),
    # /rhsl/actr_detail/1/ -> Actor #1 Detail
    path('actr_detail/<int:pk>/', views.ActrDetail.as_view(),
        name='actr_detail'),
    # /rhsl/actr_delete/1/ -> Actor #1 Delete
    path('actr_delete/<int:pk>/', views.ActrDelete.as_view(),
        name='actr_delete'),

    # /rhsl/scn_appr_create/1/ -> Appearance Create for Scene #1
    path('scn_appr_create/<int:scn_id>/', views.ScnApprCreate.as_view(),
        name='scn_appr_create'),
    # /rhsl/chr_appr_create/1/ -> Appearance Create for Character #1
    path('chr_appr_create/<int:chr_id>/', views.ChrApprCreate.as_view(),
        name='chr_appr_create'),
    # /rhsl/appr_update/1/{scn|chr}/ -> Appearance #1 Update
    path('appr_update/<int:pk>/<str:from>/', views.ApprUpdate.as_view(),
        name='appr_update'),
    # /rhsl/appr_delete/1/{scn|chr}/ -> Appearance #1 Delete
    path('appr_delete/<int:pk>/<str:from>/', views.ApprDelete.as_view(),
        name='appr_delete'),

    # /rhsl/scn_cmt_create/1/ -> ScnComment Create for Scene #1
    path('scn_cmt_create/<int:scn_id>/', views.ScnCmtCreate.as_view(),
        name='scn_cmt_create'),
    # /rhsl/scn_cmt_update/1/ -> ScnComment #1 Update
    path('scn_cmt_update/<int:pk>/', views.ScnCmtUpdate.as_view(),
        name='scn_cmt_update'),
    # /rhsl/scn_cmt_delete/1/ -> ScnComment #1 Delete
    path('scn_cmt_delete/<int:pk>/', views.ScnCmtDelete.as_view(),
        name='scn_cmt_delete'),
    
    # /rhsl/atnd_create/1/2/{actr|rhsl}/
    #   -> Attendance Create for Actor #2 in Rehearsal #1
    path('atnd_create/<int:rhsl_id>/<int:actr_id>/<str:from>/',
        views.AtndCreate.as_view(), name='atnd_create'),
    # /rhsl/atnd_update/1/{actr|rhsl}/ -> Attendance #1 Update
    path('atnd_update/<int:pk>/<str:from>/', views.AtndUpdate.as_view(),
        name='atnd_update'),
    # /rhsl/atnd_delete/1/{actr|rhsl}/ -> Attendance #1 Delete
    path('atnd_delete/<int:pk>/<str:from>/', views.AtndDelete.as_view(),
        name='atnd_delete'),
    
    # /rhsl/appr_table/1/ -> Appearance table for Production #1
    path('appr_table/<int:prod_id>/', views.ApprTable.as_view(),
        name='appr_table'),
]
