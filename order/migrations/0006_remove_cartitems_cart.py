# Generated by Django 5.1.2 on 2024-10-19 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0005_remove_cart_items_remove_cartitems_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitems',
            name='cart',
        ),
    ]