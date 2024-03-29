# Generated by Django 3.1.4 on 2021-02-22 21:40

from django.db import migrations
import django.db.models.deletion
import mptt.fields
import project.apps.categories.models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0002_auto_20210220_1422'),
        ('blog', '0005_auto_20210222_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=mptt.fields.TreeForeignKey(default=project.apps.categories.models.Category.get_default_pk, on_delete=django.db.models.deletion.SET_DEFAULT, to='categories.category'),
        ),
    ]
