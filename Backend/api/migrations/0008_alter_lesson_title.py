# Generated by Django 5.0.1 on 2024-02-21 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_lesson_unique_lesson_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]