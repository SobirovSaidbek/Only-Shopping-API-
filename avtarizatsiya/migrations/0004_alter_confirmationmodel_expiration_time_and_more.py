# Generated by Django 4.2.14 on 2024-07-12 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avtarizatsiya', '0003_alter_confirmationmodel_verify_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmationmodel',
            name='expiration_time',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='confirmationmodel',
            name='verify_type',
            field=models.CharField(choices=[('VIA_EMAIL', 'VIA_EMAIL'), ('VIA_PHONE', 'VIA_PHONE')], default='VIA_EMAIL', max_length=128),
        ),
    ]
