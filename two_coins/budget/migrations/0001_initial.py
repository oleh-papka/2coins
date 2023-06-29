# Generated by Django 4.2.2 on 2023-06-29 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30, verbose_name='Account name')),
                ('balance', models.IntegerField(blank=True, default=0, verbose_name='Balance')),
                ('initial_date', models.DateTimeField(blank=True, verbose_name='Initial date')),
                ('color', models.CharField(blank=True, default='#fcba03', max_length=7, verbose_name='Account color')),
                ('goal_balance', models.IntegerField(blank=True, default=None, null=True, verbose_name='Goal balance')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30, verbose_name='Category name')),
                ('color', models.CharField(blank=True, default='#fcba03', max_length=7, verbose_name='Category color')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=30, unique=True, verbose_name='Currency name')),
                ('ccy_type', models.CharField(choices=[('FM', 'Fiat money'), ('CX', 'Crypto currency')], default='FM', max_length=2, verbose_name='Currency type')),
                ('symbol', models.CharField(max_length=1, unique=True, verbose_name='Symbol')),
                ('abbr', models.CharField(max_length=5, unique=True, verbose_name='Abbreviation')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('txn_type', models.CharField(choices=[('-', 'Expense'), ('+', 'Income')], default='-', max_length=2, verbose_name='Transaction type')),
                ('amount', models.IntegerField(verbose_name='Amount')),
                ('description', models.CharField(blank=True, max_length=30, null=True, verbose_name='Description')),
                ('date', models.DateTimeField(blank=True, verbose_name='Transaction date')),
                ('account', models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='budget.account', verbose_name='Account')),
                ('category', models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='budget.category', verbose_name='Category')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='account',
            name='currency',
            field=models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='+', to='budget.currency'),
        ),
    ]
