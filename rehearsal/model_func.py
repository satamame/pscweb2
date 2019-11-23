def time_slots(rehearsal, scene):
    '''稽古とシーンを指定して、出欠のタイムスロットを得る
    '''
    # このシーンに出ている登場人物
    chrs = [appr.character for appr in scene.appearance_set.objects.all()]
    # Actor.objects.filter(production__pk=prod_id).order_by('name'))
    
    print(chrs)
    
    # この稽古の、全役者の in/out 時刻のリスト
    time_borders = []
    
