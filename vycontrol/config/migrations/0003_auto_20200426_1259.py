# Generated by Django 2.0.3 on 2020-04-26 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20200426_0450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instance',
            name='https',
            field=models.BooleanField(),
        ),
    ]
