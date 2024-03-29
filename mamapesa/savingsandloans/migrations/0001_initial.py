# Generated by Django 5.0.2 on 2024-03-15 11:55

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Currencies',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('loan_count', models.IntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('in_stock', models.BooleanField(default=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='item_images/')),
            ],
            options={
                'db_table': 'Items',
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(max_length=20)),
                ('id_number', models.CharField(max_length=8)),
                ('county', models.CharField(blank=True, max_length=100, null=True)),
                ('loan_owed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('loan_limit', models.DecimalField(decimal_places=2, default=8000, max_digits=10)),
                ('trust_score', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Customer',
            },
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount_disbursed', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('deduction_rate', models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ('loan_duration', models.IntegerField(default=90)),
                ('application_date', models.DateField(default=django.utils.timezone.now)),
                ('approval_date', models.DateField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('repaid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_disbursed', models.BooleanField(default=False)),
                ('default_days', models.IntegerField(default=0)),
                ('default_rate', models.DecimalField(decimal_places=2, default=5, max_digits=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Loans',
                'ordering': ['-due_date'],
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(blank=True)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='payment_icons/')),
                ('active', models.BooleanField(default=True)),
                ('payment_gateway', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('currency', models.ManyToManyField(related_name='payment_methods', to='savingsandloans.currency')),
            ],
            options={
                'db_table': 'Payment_Methods',
            },
        ),
        migrations.CreateModel(
            name='Savings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_saved', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='savings_account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Savings_Accounts',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SavingsItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('amount_saved', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('achieved', models.BooleanField(default=False)),
                ('in_progress', models.BooleanField(default=True)),
                ('saving_period', models.IntegerField(default=90)),
                ('is_suspended', models.BooleanField(default=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savings_items', to='savingsandloans.item')),
                ('savings', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='savings_items', to='savingsandloans.savings')),
            ],
            options={
                'db_table': 'Savings_Items',
                'ordering': ['due_date'],
                'unique_together': {('savings', 'item')},
            },
        ),
        migrations.AddField(
            model_name='savings',
            name='items',
            field=models.ManyToManyField(related_name='savings', through='savingsandloans.SavingsItem', to='savingsandloans.item'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('type', models.CharField(choices=[('LOAN_DISBURSEMENT', 'Loan Disbursement'), ('LOAN-REPAYMENT', 'Loan Repayment'), ('SAVINGS_DEPOSIT', 'Savings Deposit'), ('SUPPLIER_WITHDRAWAL', 'Supplier Withdrawal'), ('LOAN_SERVICE_CHARGE', 'Loan Service Charge')], max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_ref', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'pending'), ('COMPLETED', 'completed'), ('FAILED', 'failed')], default='pending', max_length=50)),
                ('payment_date', models.DateTimeField(auto_now_add=True)),
                ('receiving_till', models.CharField(blank=True, max_length=15, null=True)),
                ('receiving_number', models.CharField(blank=True, max_length=15, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='savingsandloans.customer')),
                ('loan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='savingsandloans.loan')),
                ('payment_method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='savingsandloans.paymentmethod')),
                ('savings', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='savingsandloans.savings')),
                ('savings_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='savingsandloans.savingsitem')),
            ],
            options={
                'db_table': 'Payments',
                'ordering': ('-payment_date',),
            },
        ),
    ]
