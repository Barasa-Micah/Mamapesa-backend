# Generated by Django 5.0.2 on 2024-03-01 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0012_alter_loan_interest_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='duration_months',
            field=models.IntegerField(null=True),
        ),
    ]