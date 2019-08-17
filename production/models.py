from django.conf import settings
from django.db import models

class Production(models.Model):
    name = models.CharField('公演名', max_length=50)

    class Meta:
        verbose_name = verbose_name_plural = "公演"
        
    def __str__(self):
        return self.name


class ProdUser(models.Model):
    prod_id = models.ForeignKey(Production, verbose_name='公演',
        on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name='ユーザ', on_delete=models.CASCADE)
    is_owner = models.BooleanField('所有権', default=False)
    is_editor = models.BooleanField('編集権', default=False)

    class Meta:
        verbose_name = verbose_name_plural = "公演ユーザ"
        
    def __str__(self):
        return '{}@{}'.format(self.user_id, self.prod_id)
