# Generated by Django 5.1.2 on 2024-10-19 16:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0006_remove_cartitems_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitems',
            name='cart',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='order.cart', verbose_name='მომხმარებელი'),
            preserve_default=False,
        ),
    ]