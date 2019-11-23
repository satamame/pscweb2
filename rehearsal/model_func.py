from .models import *

def time_slots_for_rehearsal(rehearsal, actors=None, scenes=None):
    '''稽古を指定して、全シーンの時間スロットのリストを得る
    '''
    
    def actor_info_in_scene(actor, scene):
        '''指定した役者の、あるシーンでの役とセリフ数をリストにして返す
        
        Returns
        -------
        [
            {
                actor: actor,
                apearances: [{
                    character: character,
                    lines_num: lines_num
                }]
            }
        ]
        '''
        # この役者が演じている役
        chrs = actor.character_set.all()
        
        # それらの役の、このシーンでの出番
        apprs = []
        for chr in chrs:
            apprs.extend(list(chr.appearance_set.filter(scene=scene)))
        
        return {
            'actor': actor,
            'appearances': [{
                'character': appr.character,
                'lines_num': Appearance.average_lines_num(apprs)
                    if appr.lines_auto else appr.lines_num
            } for appr in apprs]
        }
    
    # ここからメインルーチン
    prod_id = rehearsal.production.id
    
    if not actors:
        actors = Actor.objects.filter(production__pk=prod_id)
    
    if not scenes:
        scenes = Scene.objects.filter(production__pk=prod_id)
    
    # この稽古の、全役者の in/out 時刻のリスト
    time_borders = []
    for actr in actors:
        atnds = actr.attendance_set.filter(rehearsal=rehearsal)
        for atnd in atnds:
            # 欠席なら除外
            if atnd.is_absent:
                continue
            # in 時刻 - 稽古の開始時刻～終了時刻に収まるよう補正する
            from_time = rehearsal.start_time if atnd.is_allday\
                else min(max(atnd.from_time, rehearsal.start_time),
                    rehearsal.end_time)
            time_borders.append({
                'time': from_time,
                'actor': actr,
                'move': 'in'
            })
            # out 時刻 - 稽古の開始時刻～終了時刻に収まるよう補正する
            to_time = rehearsal.end_time if atnd.is_allday\
                else min(max(atnd.to_time, rehearsal.start_time),
                    rehearsal.end_time)
            time_borders.append({
                'time': to_time,
                'actor': actr,
                'move': 'out'
             })
    
    # シーンごとの時間スロット
    scns_time_slots = []
    for scene in scenes:
        # このシーンの出番のリスト
        scn_apprs = [appr for appr in scene.appearance_set.all()]
        # このシーンの役者のリスト
        scn_actrs = [appr.character.cast for appr in scn_apprs]
        # 重複を削除
        scn_actrs = list(set(scn_actrs))
        
        # このシーンに出ている役者の時間スロットの境界のリスト
        scn_time_borders = [
            border for border in time_borders
            if border['actor'] in scn_actrs]
        
        # scn_time_borders から、このシーンの時間スロットを作る
        # time でソート (in -> out の順序は保たれる)
        scn_time_borders = sorted(scn_time_borders, key=lambda x:x['time'])
        
        time = rehearsal.start_time
        slots = []
        attendee = set()
        for border in scn_time_borders:
            # 次の時間ならスロット追加
            if border['time'] > time:
                slots.append({
                    'from_time': time,
                    'to_time': border['time'],
                    'attendee': [actor_info_in_scene(actr, scene) for actr in attendee]
                })
                # 次のスロット開始
                time = border['time']
            
            if border['move'] == 'in':
                attendee.add(border['actor'])
            if border['move'] == 'out':
                attendee.discard(border['actor'])
        
        # 稽古の終了時刻に達していなかったらスロット追加
        if rehearsal.end_time > time:
            slots.append({
                'from_time': time,
                'to_time': rehearsal.end_time,
                'attendee': [actor_info_in_scene(actr, scene) for actr in attendee]
            })
        
        # シーンごとのデータとしてリストに追加
        scns_time_slots.append({
            'scene_id': scene.id,
            'scene': scene,
            # 'chrs_num': chrs_num,
            'time_slots': slots
        })
    
    return scns_time_slots
