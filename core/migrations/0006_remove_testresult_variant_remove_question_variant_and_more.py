# Generated by Django 5.2 on 2025-05-12 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_answer_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testresult',
            name='variant',
        ),
        migrations.RemoveField(
            model_name='question',
            name='variant',
        ),
        migrations.RemoveField(
            model_name='test',
            name='has_variants',
        ),
        migrations.DeleteModel(
            name='TestVariant',
        ),
    ]
