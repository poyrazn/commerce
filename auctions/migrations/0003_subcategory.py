# Generated by Django 3.1.3 on 2020-12-02 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20201130_1919'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategory', to='auctions.category')),
            ],
        ),
    ]
