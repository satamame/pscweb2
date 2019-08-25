from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from production.models import Production


class Facility(models.Model):
    '''稽古場の施設 (建物) 情報
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('名前', max_length=50)
    url = models.URLField('リンク', blank=True)
    note = models.TextField('メモ', blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '稽古場の施設'
    
    def __str__(self):
        return self.name


class Place(models.Model):
    '''稽古場 (部屋単位)
    '''
    facility = models.ForeignKey(Facility, verbose_name='施設',
        on_delete=models.CASCADE)
    room_name = models.CharField('部屋名', max_length=50)
    note = models.TextField('メモ', blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '稽古場'
    
    def __str__(self):
        # ex. 'City hall,Studio #1'
        return '{},{}'.format(self.facility, self.room_name)


class Rehearsal(models.Model):
    '''稽古の1コマ分のデータ
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    place = models.ForeignKey(Place, verbose_name='稽古場',
        on_delete=models.SET_NULL, null=True)
    date = models.DateField('日付')
    start_time = models.TimeField('開始')
    end_time = models.TimeField('終了')
    note = models.TextField('メモ', blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '稽古のコマ'
    
    def __str__(self):
        # ex. '08/30,City hall,Studio #1'
        return '{},{}'.format(self.date.strftime('%m/%d'), self.place)


class Scene(models.Model):
    '''稽古するシーン
    
    ダブルキャスト (以上) の場合は、配役ごとに登録する
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('シーン名', max_length=50)
    sortkey = models.IntegerField('ソートキー', default=0)
    length = models.IntegerField('長さ', default=1,
        validators=[MinValueValidator(1)])
    length_auto = models.BooleanField('長さを自動で決める', default=True)
    progress = models.IntegerField('完成度', default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    note = models.TextField('メモ', blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = 'シーン'
    
    def __str__(self):
        return self.name


class Actor(models.Model):
    '''役者
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('名前', max_length=50)
    short_name = models.CharField('短縮名', max_length=5, null=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '役者'
    
    def __str__(self):
        return self.name


class Character(models.Model):
    '''登場人物
    
    ダブルキャスト (以上) の場合は、演じる役者ごとに登録する
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('名前', max_length=50)
    short_name = models.CharField('短縮名', max_length=5, null=True)
    cast = models.ForeignKey(Actor, verbose_name='配役',
        on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = verbose_name_plural = '登場人物'
    
    def __str__(self):
        return '{} ({})'.format(self.name, self.cast)


class Attendance(models.Model):
    '''参加時間
    
    1コマの稽古に同じ人の参加時間が複数回あっても良い
    '''
    rehearsal = models.ForeignKey(Rehearsal, verbose_name='稽古のコマ',
        on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, verbose_name='役者',
        on_delete=models.CASCADE)
    from_time = models.TimeField('From')
    to_time = models.TimeField('To')
    
    class Meta:
        verbose_name = verbose_name_plural = '参加時間'
    
    def __str__(self):
        # ex. '08/30,望月'
        return '{},{}'.format(self.rehearsal.date.strftime('%m/%d'),
            self.actor.short_name)


class Appearance(models.Model):
    '''出番
    '''
    scene = models.ForeignKey(Scene, verbose_name='シーン',
        on_delete=models.CASCADE)
    character = models.ForeignKey(Character, verbose_name='登場人物',
        on_delete=models.CASCADE)
    lines_num = models.IntegerField('セリフ数', default=1,
        validators=[MinValueValidator(1)])
    lines_auto = models.BooleanField('セリフ数を決めない', default=False)
    
    class Meta:
        verbose_name = verbose_name_plural = '出番'
    
    def __str__(self):
        return str(self.scene)
