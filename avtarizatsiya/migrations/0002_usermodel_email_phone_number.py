# Generated by Django 4.2.14 on 2024-07-12 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avtarizatsiya', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermodel',
            name='email_phone_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
