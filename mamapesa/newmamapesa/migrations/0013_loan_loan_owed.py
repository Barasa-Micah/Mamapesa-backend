# Generated by Django 5.0.2 on 2024-03-01 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0012_loan_amount_disbursed'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='loan_owed',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
