# Generated by Django 5.0.4 on 2024-12-08 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking_service', '0003_remove_playerqueue_skill_level_match_result_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerqueue',
            name='player_id',
            field=models.CharField(max_length=255),
        ),
    ]
