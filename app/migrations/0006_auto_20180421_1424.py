# Generated by Django 2.0.4 on 2018-04-21 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_member_total_point'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solution',
            name='submission_date',
        ),
        migrations.AddField(
            model_name='contestpoint',
            name='submission_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]