# Generated by Django 5.0.2 on 2024-02-29 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newmamapesa', '0008_alter_savingsitem_due_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='savingsitem',
            name='saving_period',
            field=models.IntegerField(default=90),
        ),
        migrations.AlterField(
            model_name='savingsitem',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
