# Generated by Django 5.0.4 on 2025-01-07 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_type', models.CharField(choices=[('F', 'Final'), ('S', 'Semi-Final'), ('Q', 'Quarter-Final')], max_length=1)),
                ('number_of_players', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('location', models.CharField(blank=True, max_length=30, null=True)),
                ('score', models.IntegerField(default=0)),
                ('victories', models.IntegerField(default=0)),
                ('oauth_tokens', models.JSONField(blank=True, null=True)),
                ('tournaments', models.ManyToManyField(blank=True, related_name='players', to='data.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_1_points', models.IntegerField(default=0)),
                ('player_2_points', models.IntegerField(default=0)),
                ('match_time', models.DateTimeField()),
                ('tournament', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches', to='data.tournament')),
                ('player_1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_1_matches', to='data.user')),
                ('player_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='player_2_matches', to='data.user')),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='matches_won', to='data.user')),
            ],
        ),
    ]
