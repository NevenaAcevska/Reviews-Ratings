# Generated by Django 4.1 on 2024-04-06 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reviewa', '0008_remove_user__store_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='store',
            field=models.ManyToManyField(related_name='stores', to='Reviewa.business'),
        ),
    ]