from django.urls import path
from . import views

app_name = 'rehearsal'
urlpatterns = [
    # ----------------------------------------------------------------
    # トップ
    
    # /rhsl/1/ -> Rehearsal Top for Production #1
    path('<int:prod_id>/', views.RhslTop.as_view(), name='rhsl_top'),
    
    # ----------------------------------------------------------------
    # 稽古
    
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
    
    # /rhsl/rhsl_absence/1/ -> Asence list for Rehearsal #1
    path('rhsl_absence/<int:pk>/', views.RhslAbsence.as_view(),
        name='rhsl_absence'),
    
    # ----------------------------------------------------------------
    # 稽古場
    
    # /rhsl/plc_list/1/ -> Place List for Production #1
    path('plc_list/<int:prod_id>/', views.PlcList.as_view(),
        name='plc_list'),
    # /rhsl/plc_create/1/ -> Place Create for Facility #1
    path('plc_create/<int:fclt_id>/', views.PlcCreate.as_view(),
        name='plc_create'),
    # /rhsl/plc_update/1/ -> Place #1 Update
    path('plc_update/<int:pk>/', views.PlcUpdate.as_view(),
        name='plc_update'),
    # /rhsl/plc_delete/1/ -> Place #1 Delete
    path('plc_delete/<int:pk>/', views.PlcDelete.as_view(),
        name='plc_delete'),
    
    # ----------------------------------------------------------------
    # 稽古場の施設
    
    # /rhsl/fclt_create/1/ -> Facility Create for Production #1
    path('fclt_create/<int:prod_id>/', views.FcltCreate.as_view(),
        name='fclt_create'),
    # /rhsl/fclt_update/1/ -> Facility #1 Update
    path('fclt_update/<int:pk>/', views.FcltUpdate.as_view(),
        name='fclt_update'),
    # /rhsl/fclt_delete/1/ -> Facility #1 Delete
    path('fclt_delete/<int:pk>/', views.FcltDelete.as_view(),
        name='fclt_delete'),
    
    # ----------------------------------------------------------------
    # シーン
    
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

    # ----------------------------------------------------------------
    # 登場人物
    
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

    # ----------------------------------------------------------------
    # 役者
    
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

    # ----------------------------------------------------------------
    # 出番
    
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

    # ----------------------------------------------------------------
    # シーンコメント
    
    # /rhsl/scn_cmt_create/1/ -> ScnComment Create for Scene #1
    path('scn_cmt_create/<int:scn_id>/', views.ScnCmtCreate.as_view(),
        name='scn_cmt_create'),
    # /rhsl/scn_cmt_update/1/ -> ScnComment #1 Update
    path('scn_cmt_update/<int:pk>/', views.ScnCmtUpdate.as_view(),
        name='scn_cmt_update'),
    # /rhsl/scn_cmt_delete/1/ -> ScnComment #1 Delete
    path('scn_cmt_delete/<int:pk>/', views.ScnCmtDelete.as_view(),
        name='scn_cmt_delete'),
    
    # ----------------------------------------------------------------
    # 参加時間
    
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
    
    # ----------------------------------------------------------------
    # 香盤表
    
    # /rhsl/appr_table/1/ -> Appearance table for Production #1
    path('appr_table/<int:prod_id>/', views.ApprTable.as_view(),
        name='appr_table'),

    # ----------------------------------------------------------------
    # 出欠表

    # /rhsl/atnd_table/1/ -> Attendance table for Production #1
    path('atnd_table/<int:prod_id>/', views.AtndTable.as_view(),
        name='atnd_table'),

    # ----------------------------------------------------------------
    # 出欠グラフ (稽古ごとの出欠表)

    # /rhsl/atnd_graph/1/ -> Attendance graph for Rehearsal #1
    path('atnd_graph/<int:rhsl_id>/', views.AtndGraph.as_view(),
        name='atnd_graph'),

    # ----------------------------------------------------------------
    # 出欠変更履歴

    # /rhsl/atnd_change_list/1/ -> Attendance change list for Production #1
    path('atnd_change_list/<int:prod_id>/', views.AtndChangeList.as_view(),
        name='atnd_change_list'),
]
