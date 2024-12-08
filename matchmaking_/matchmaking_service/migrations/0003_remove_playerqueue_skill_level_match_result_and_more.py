# Generated by Django 5.0.4 on 2024-12-08 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking_service', '0002_alter_playerqueue_player_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='playerqueue',
            name='skill_level',
        ),
        migrations.AddField(
            model_name='match',
            name='result',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='MatchResult',
        ),
    ]
