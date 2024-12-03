# Generated by Django 5.0.10.dev20241112012728 on 2024-12-03 20:32

import django_mongodb.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Embed',
            fields=[
                ('id', django_mongodb.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
                ('max_width', models.SmallIntegerField(blank=True, null=True)),
                ('hash', models.CharField(db_index=True, max_length=32, unique=True)),
                ('type', models.CharField(choices=[('video', 'Video'), ('photo', 'Photo'), ('link', 'Link'), ('rich', 'Rich')], max_length=10)),
                ('html', models.TextField(blank=True)),
                ('title', models.TextField(blank=True)),
                ('author_name', models.TextField(blank=True)),
                ('provider_name', models.TextField(blank=True)),
                ('thumbnail_url', models.TextField(blank=True)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('cache_until', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
            options={
                'verbose_name': 'embed',
                'verbose_name_plural': 'embeds',
            },
        ),
    ]