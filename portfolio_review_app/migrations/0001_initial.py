# Generated by Django 5.0.6 on 2024-07-07 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('site_url', models.CharField(max_length=9991)),
                ('site_image_url', models.CharField(max_length=9991)),
                ('feedback', models.CharField(default=None, max_length=99991, null=True)),
                ('user_rating', models.CharField(blank=True, choices=[('great', 'Great'), ('poor', 'Poor')], default=None, max_length=5, null=True)),
            ],
        ),
    ]