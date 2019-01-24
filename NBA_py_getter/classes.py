# container for class declarations
from datetime import datetime

import mongoengine as mongoengine

import data_templates


class Snapshot(mongoengine.Document):
    created = mongoengine.DateTimeField(default=datetime.now)
    team_id = mongoengine.ObjectIdField()
    team_dashboard = None
    common_team_roster_players_headers = mongoengine.ListField(
        data_templates.common_team_roster_player_headers)
    common_team_roster_players = mongoengine.ListField(mongoengine.EmbeddedDocument(TeamRosterPlayer))
    common_team_roster_coach_headers = mongoengine.ListField(
        data_templates.common_team_roster_coach_headers)


class TeamRosterPlayer(mongoengine.EmbeddedDocument):
    """
    'TeamID',
    'SEASON',
    'LeagueID',
    'PLAYER',
    'NUM',
    'POSITION',
    'HEIGHT',
    'WEIGHT',
    'BIRTH_DATE',
    'AGE',
    'EXP',
    'SCHOOL',
    'PLAYER_ID'
    """
    player = mongoengine.StringField(required=True)
    player_id = mongoengine.ObjectIdField(required=True)
