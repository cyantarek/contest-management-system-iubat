# Generated by Django 2.0.4 on 2018-04-21 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20180421_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='contests',
            field=models.ManyToManyField(blank=True, null=True, through='app.ContestPoint', to='app.Contest'),
        ),
    ]
