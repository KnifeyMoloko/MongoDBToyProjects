import json

import os
from nba_py import team
from pprint import pprint
from datetime import datetime
from config import nba_teams, season, logger_root_config_data_test
import logging
from logging import config as log_config
from pathlib import Path
from helpers import basic_log, get_headers, get_result_sets, get_row_set

date = datetime(2018, 2, 24)
print(date)

#game_logs = team.TeamGameLogs("1610612744","2017-18").json
team._TeamDashboard
team.TeamClutchSplits
team.TeamCommonRoster
team.TeamDetails
team.TeamGeneralSplits
team.TeamInGameSplits
team.TeamLastNGamesSplits
team.TeamLineups
team.TeamList
team.TeamOpponentSplits
team.TeamPassTracking
team.TeamPerformanceSplits
team.TeamPlayerOnOffDetail
team.TeamPlayerOnOffSummary
team.TeamPlayers
team.TeamReboundTracking
team.TeamSeasons
team.TeamShootingSplits
team.TeamShotTracking
team.TeamSummary
team.TeamVsPlayer
team.TeamYearOverYearSplits

logging.basicConfig()
output = []
path = Path('.') / 'data_test_logs'
path.mkdir(parents=True, exist_ok=True)
log_config.dictConfig(logger_root_config_data_test)
logger = logging.getLogger(__name__)  # name the logger with the module name



@basic_log
def get_team_logs():

    team_ids = []
    team_logs = []

    # collect team ids
    for tm in nba_teams:
        team_ids.append(str(tm["_id"]))

    # get team logs by looping through ids
    for id in team_ids:
        team_logs.append(team.TeamGameLogs(id, season).info())
    return team_logs


def get_team_log():
    id = nba_teams[0].get("_id")
    out = team.TeamGameLogs(id).info()
    return out


def make_class(cls=None):
    """This is 'class factory' function. It should receive a class
    inheriting from the mongoengine Document class and set the field names.
    As for the field specifications, it will unfortunately have to be done
    manually, as there is no sense in mapping out field names to field types."""
    template = get_team_log()[0]
    pprint(template)

    for name, value in template.items():
        setattr(cls, name, value)
    return cls


@make_class
class Smurf:
    pass


#output = [get_team_log()]

pprint(Smurf.__dict__)

