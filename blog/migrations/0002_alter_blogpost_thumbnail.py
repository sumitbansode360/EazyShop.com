# Generated by Django 4.2.7 on 2024-05-30 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='thumbnail',
            field=models.ImageField(upload_to='blog/blog_img'),
        ),
    ]