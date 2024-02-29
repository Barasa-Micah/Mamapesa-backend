# Generated by Django 5.0.2 on 2024-02-28 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0008_alter_customuser_interest_rate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='loan',
            name='overdue_rate',
            field=models.DecimalField(decimal_places=2, default=5, max_digits=5),
        ),
        migrations.AddField(
            model_name='loan',
            name='repayments',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
