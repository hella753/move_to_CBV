# Generated by Django 5.1.2 on 2024-10-19 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_product_country_product_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='related_products',
            field=models.ManyToManyField(blank=True, null=True, to='store.product', verbose_name='მსგავსი პროდუქტები'),
        ),
    ]