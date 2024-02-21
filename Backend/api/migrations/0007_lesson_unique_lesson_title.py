# Generated by Django 5.0.1 on 2024-02-21 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_lesson_lesson'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(fields=('course', 'title'), name='unique_lesson_title'),
        ),
    ]
