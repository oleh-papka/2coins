# Generated by Django 5.0.6 on 2024-09-11 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_alter_account_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='initial_balance',
            field=models.DecimalField(blank=True, decimal_places=8, default=0, max_digits=20, null=True, verbose_name='Initial balance'),
        ),
        migrations.AlterField(
            model_name='account',
            name='target_balance',
            field=models.DecimalField(blank=True, decimal_places=8, default=0, max_digits=20, null=True, verbose_name='Target balance'),
        ),
    ]
