# Generated by Django 5.0.6 on 2024-08-05 15:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='Currency name')),
                ('currency_type', models.CharField(choices=[('F', 'Fiat money'), ('C', 'Crypto currency')], default='F', max_length=1, verbose_name='Currency type')),
                ('symbol', models.CharField(max_length=2, unique=True, verbose_name='Symbol')),
                ('abbr', models.CharField(max_length=5, unique=True, verbose_name='Abbreviation')),
            ],
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(blank=True, default='#fcba03', max_length=7, verbose_name='Color')),
                ('icon', models.CharField(blank=True, help_text='Icon name from FontAwesome', max_length=30, null=True, verbose_name='Icon')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30, verbose_name='Category name')),
                ('category_type', models.CharField(choices=[('-', 'Expense'), ('+', 'Income')], default='-', max_length=1, verbose_name='Category type')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
                ('style', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.style')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account_type', models.CharField(choices=[('d', 'Default account'), ('s', 'Savings account')], default='d', max_length=1, verbose_name='Account type')),
                ('name', models.CharField(max_length=30, verbose_name='Account name')),
                ('balance', models.FloatField(blank=True, default=0, verbose_name='Account balance')),
                ('description', models.CharField(blank=True, max_length=30, null=True, verbose_name='Description')),
                ('initial_balance', models.FloatField(blank=True, default=0, verbose_name='Initial balance')),
                ('target_balance', models.FloatField(blank=True, default=0, null=True, verbose_name='Target balance')),
                ('deadline', models.DateField(blank=True, default=None, null=True, verbose_name='Deadline date')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='profiles.profile')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='budget.currency')),
                ('style', models.OneToOneField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='budget.style')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('-', 'Expense'), ('+', 'Income')], default='-', max_length=1, verbose_name='Transaction type')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('amount_converted', models.FloatField(blank=True, null=True, verbose_name="Amount in account's currency")),
                ('description', models.CharField(blank=True, max_length=50, null=True, verbose_name='Description')),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Date/time')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.account', verbose_name='Account')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.category', verbose_name='Category')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='budget.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_from', models.FloatField(verbose_name='Amount transferring from account')),
                ('amount_to', models.FloatField(blank=True, verbose_name='Amount transferring to account')),
                ('description', models.CharField(blank=True, max_length=50, null=True, verbose_name='Description')),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Date/time')),
                ('account_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_out', to='budget.account', verbose_name='From Account')),
                ('account_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers_in', to='budget.account', verbose_name='To Account')),
            ],
        ),
    ]
