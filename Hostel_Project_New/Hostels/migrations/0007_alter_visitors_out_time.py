# Generated by Django 5.0.6 on 2024-10-01 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Hostels', '0006_visitors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitors',
            name='out_time',
            field=models.DateTimeField(),
        ),
    ]
