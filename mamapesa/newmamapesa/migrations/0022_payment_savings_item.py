# Generated by Django 5.0.2 on 2024-03-10 20:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0021_alter_customer_id_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='savings_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='newmamapesa.savingsitem'),
        ),
    ]