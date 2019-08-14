from django.db import models

class Production(models.Model):
    name = models.CharField('公演名', max_length=50)

    def __str__(self):
        return self.name
