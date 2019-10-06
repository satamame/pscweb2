from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from production.models import Production, ProdUser


class Facility(models.Model):
    '''稽古場の施設 (建物) 情報
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('施設名', max_length=50)
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
        # ex. '○○公民館,会議室1'
        return '{},{}'.format(self.facility, self.room_name)


class Rehearsal(models.Model):
    '''稽古の1コマ分のデータ
    
    2日以上にまたがる稽古は、日ごとにコマを分割する
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    place = models.ForeignKey(Place, verbose_name='稽古場',
        on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateField('日付')
    start_time = models.TimeField('開始')
    end_time = models.TimeField('終了')
    note = models.TextField('メモ', blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '稽古のコマ'
    
    def __str__(self):
        # ex. '08/30,○○公民館,会議室1'
        return '{},{}'.format(self.date.strftime('%m/%d'), self.place)


class Scene(models.Model):
    '''稽古するシーン
    
    ダブルキャスト (以上) の場合は、配役ごとに登録する
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('シーン名', max_length=50)
    sortkey = models.IntegerField('順番', default=0)
    description = models.CharField('説明', max_length=200, blank=True)
    length = models.IntegerField('長さ', default=1,
        validators=[MinValueValidator(1)])
    length_auto = models.BooleanField('長さは適当', default=True)
    progress = models.IntegerField('完成度', default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    PRIORITY_CHOICES = (
        (1, '最高'),
        (2, '高'),
        (3, '-'),
        (4, '低'),
        (5, '最低'),
    )
    priority = models.IntegerField('優先度', default=3,
        choices=PRIORITY_CHOICES)
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
    short_name = models.CharField('短縮名', max_length=5, blank=True)
    
    class Meta:
        verbose_name = verbose_name_plural = '役者'
    
    def __str__(self):
        return self.name
    
    def get_short_name(self):
        return self.short_name or self.name[:3]


class Character(models.Model):
    '''登場人物
    
    ダブルキャスト (以上) の場合は、演じる役者ごとに登録する
    '''
    production = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    name = models.CharField('役名', max_length=50)
    short_name = models.CharField('短縮名', max_length=5, blank=True)
    cast = models.ForeignKey(Actor, verbose_name='配役',
        on_delete=models.SET_NULL, blank=True, null=True)
    sortkey = models.IntegerField('順番', default=0)
    
    class Meta:
        verbose_name = verbose_name_plural = '登場人物'
    
    def __str__(self):
        # ex. '沙悟浄(三橋)'
        if self.cast:
            return '{}({})'.format(self.name, self.cast.get_short_name())
        return self.name
    
    def get_short_name(self):
        return self.short_name or self.name[:3]


class Attendance(models.Model):
    '''参加時間
    
    1コマの稽古に同じ人の参加時間が複数回あっても良い
    is_absent が True なら、同じ稽古にそれ以外のレコードをセットできない
    is_allday が True なら、同じ稽古にそれ以外のレコードをセットできない
    '''
    rehearsal = models.ForeignKey(Rehearsal, verbose_name='稽古のコマ',
        on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, verbose_name='役者',
        on_delete=models.CASCADE)
    from_time = models.TimeField('From', blank=True, null=True)
    to_time = models.TimeField('To', blank=True, null=True)
    is_allday = models.BooleanField('全日', default=False)
    is_absent = models.BooleanField('欠席', default=False)
    
    class Meta:
        verbose_name = verbose_name_plural = '参加時間'
    
    def __str__(self):
        # ex. '08/30,三橋,14:00-18:30'
        str = '{},{},'.format(self.rehearsal.date.strftime('%m/%d'),
            self.actor.get_short_name())
        if self.is_absent:
            str += '欠席'
        elif self.is_allday:
            str += '全日'
        else:
            from_time = self.from_time.strftime('%H:%M') if self.from_time else '??:??'
            to_time = self.to_time.strftime('%H:%M') if self.to_time else '??:??'
            str += '{}-{}'.format(from_time, to_time)
        return str
    
    def clean(self):
        '''admin 画面用に、モデル側でもバリデーションする
        '''
        if self.is_absent and self.is_allday:
            raise ValidationError('「全日」「欠席」の両方を選択することは出来ません。')
        if not (self.is_absent or self.is_allday):
            if not (self.from_time and self.to_time):
                raise ValidationError('「全日」「欠席」でない場合、参加時間は必須です。')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class Appearance(models.Model):
    '''出番
    
    あるシーンにある登場人物が出ていれば、このレコードを作る
    セリフ数は、出席率に重みをつけるのに使う
    '''
    scene = models.ForeignKey(Scene, verbose_name='シーン',
        on_delete=models.CASCADE)
    character = models.ForeignKey(Character, verbose_name='登場人物',
        on_delete=models.CASCADE)
    lines_num = models.IntegerField('セリフ数', default=1,
        validators=[MinValueValidator(0)])
    lines_auto = models.BooleanField('セリフ数を決めない', default=False)
    
    class Meta:
        verbose_name = verbose_name_plural = '出番'
    
    def __str__(self):
        # ex. 'シーン1,沙悟浄'
        return '{},{}'.format(self.scene, self.character)


class ScnComment(models.Model):
    '''シーンにつけるコメント
    '''
    scene = models.ForeignKey(Scene, verbose_name='シーン',
        on_delete=models.CASCADE)
    create_dt = models.DateTimeField('作成日時', auto_now_add=True)
    modify_dt = models.DateTimeField('変更日時', auto_now=True)
    comment = models.TextField('コメント')
    mod_prod_user = models.ForeignKey(ProdUser, verbose_name='記入者',
        on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = verbose_name_plural = 'シーンコメント'
    
    def __str__(self):
        # ex. 'コメント by xx at xx:xx'
        dt = timezone.localtime(self.modify_dt).strftime("%Y/%m/%d %H:%M:%S")
        return 'コメント by {} at {}'.format(self.mod_prod_user.user, dt)
