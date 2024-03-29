# Generated by Django 2.2.1 on 2019-06-06 07:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flv_id', models.CharField(max_length=36)),
                ('name', models.CharField(max_length=20)),
                ('ram', models.FloatField()),
                ('vcpu', models.IntegerField()),
                ('disk', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('flv', models.CharField(max_length=20)),
                ('allocated', models.BooleanField()),
                ('ip', models.CharField(max_length=15)),
                ('repo', models.URLField()),
                ('status', models.CharField(max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
