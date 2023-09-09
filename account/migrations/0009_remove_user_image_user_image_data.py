# Generated by Django 4.2.3 on 2023-09-09 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_alter_user_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image',
            field=models.ImageField(upload_to="user",null = True),
        ),
        migrations.AddField(
            model_name='user',
            name='image_data',
            field=models.CharField(max_length=3000, null=True),
        ),
    ]
