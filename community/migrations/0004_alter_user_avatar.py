# Generated by Django 3.2.7 on 2022-11-05 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_alter_user_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(default='static/main/images/avatar.svg', null=True, upload_to=''),
        ),
    ]
