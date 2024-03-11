# Generated by Django 5.0.2 on 2024-03-07 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0005_loan_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loantransaction',
            name='type',
            field=models.CharField(choices=[('REPAYMENT', 'repayment'), ('LOAN_DISBURSEMENT', 'loan_disbursement')], default='', max_length=20),
        ),
        migrations.DeleteModel(
            name='LoanRepayment',
        ),
    ]
