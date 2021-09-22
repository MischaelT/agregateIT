# Generated by Django 3.2.5 on 2021-09-21 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.FileField(blank=True, default=None, null=True, upload_to='avatars'),
        ),
    ]
