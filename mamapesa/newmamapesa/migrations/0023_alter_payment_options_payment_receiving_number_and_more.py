# Generated by Django 5.0.2 on 2024-03-11 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0022_payment_savings_item'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'ordering': ('-payment_date',)},
        ),
        migrations.AddField(
            model_name='payment',
            name='receiving_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='receiving_till',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]