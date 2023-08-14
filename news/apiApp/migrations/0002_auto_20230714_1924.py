# Generated by Django 3.2.19 on 2023-07-14 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='source_id',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='source_name',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='urlToImage',
            field=models.URLField(null=True),
        ),
    ]
