# Generated by Django 4.0.5 on 2022-07-24 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cook_for_kids', '0008_remove_notday_kid_kid_notday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='kid',
            name='notday',
        ),
        migrations.AddField(
            model_name='notday',
            name='kid',
            field=models.ManyToManyField(related_name='notdaykids', to='cook_for_kids.kid'),
        ),
    ]
