import django.db.models.deletion
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_string', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'query',
                'verbose_name_plural': 'queries',
            },
        ),
        migrations.CreateModel(
            name='SearchPromotion',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_link_url', models.URLField(blank=True, help_text='Alternatively, use an external link for this promotion', verbose_name='External link URL')),
                ('external_link_text', models.CharField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, help_text='Applies to internal page or external link', verbose_name='description')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('page', models.ForeignKey(blank=True, help_text='Choose an internal page for this promotion', null=True, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.page', verbose_name='page')),
                ('query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='editors_picks', to='wagtailsearchpromotions.query')),
            ],
            options={
                'verbose_name': 'search promotion',
                'ordering': ('sort_order',),
            },
        ),
        migrations.CreateModel(
            name='QueryDailyHits',
            fields=[
                ('id', django_mongodb_backend.fields.ObjectIdAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('hits', models.IntegerField(default=0)),
                ('query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_hits', to='wagtailsearchpromotions.query')),
            ],
            options={
                'verbose_name': 'Query Daily Hits',
                'verbose_name_plural': 'Query Daily Hits',
                'unique_together': {('query', 'date')},
            },
        ),
    ]
