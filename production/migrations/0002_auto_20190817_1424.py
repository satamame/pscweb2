# Generated by Django 2.2.4 on 2019-08-17 05:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('production', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='production',
            options={'verbose_name': '公演', 'verbose_name_plural': '公演'},
        ),
        migrations.CreateModel(
            name='ProdUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_owner', models.BooleanField(default=False, verbose_name='所有権')),
                ('is_editor', models.BooleanField(default=False, verbose_name='編集権')),
                ('prod_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='production.Production', verbose_name='公演')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザ')),
            ],
            options={
                'verbose_name': '公演ユーザ',
                'verbose_name_plural': '公演ユーザ',
            },
        ),
    ]