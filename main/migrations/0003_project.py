# Generated migration for Project model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_post'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('category', models.CharField(choices=[('design', 'Design'), ('development', 'Development'), ('music', 'Music'), ('photography', 'Photography'), ('writing', 'Writing'), ('other', 'Other')], max_length=50)),
                ('budget', models.CharField(help_text='e.g., $500-$1000', max_length=100)),
                ('timeline', models.CharField(help_text='e.g., 2-4 weeks', max_length=100)),
                ('requirements', models.TextField(help_text='Detailed project requirements')),
                ('tags', models.CharField(blank=True, default='', help_text='Comma-separated tags', max_length=200)),
                ('is_open', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
