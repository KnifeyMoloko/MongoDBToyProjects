from nba_py import team
from pprint import pprint
from datetime import datetime
from constants import nba_teams, season, logger_root_config
import logging
from logging import config as log_config
from pathlib import Path

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
path = Path('.') / 'logs'
path.mkdir(parents=True, exist_ok=True)
log_config.dictConfig(logger_root_config)
logger = logging.getLogger(__name__)  # name the logger with the module name


def get_team_logs(team_id, season, nba_py_team_object):
    logging.info("Trying to get log.")
    output_json = nba_py_team_object(team_id, season).json
    logging.info("Got log. Returning output.")
    return output_json



team_logs = []
"""
mil_logs = get_team_logs(1610612749, season, team.TeamGameLogs)
team_logs.append(mil_logs)
tor_logs = get_team_logs(1610612761, season, team.TeamGameLogs)
team_logs.append(tor_logs)
atl_logs = get_team_logs(1610612737, season, team.TeamGameLogs)
team_logs.append(atl_logs)
"""
team_ids = []
for tm in nba_teams:
    team_ids.append(str(tm["_id"]))


for id in team_ids:
    team_logs.append(get_team_logs(id, season, team.TeamGameLogs))
    print(len(team_logs))

print(len(team_logs))
for item in team_logs:
    pprint(item)
"""
bos_logs = get_team_logs(1610612738, season, team.TeamGameLogs)
cle_logs = get_team_logs(1610612739, season, team.TeamGameLogs)
nop_logs = get_team_logs(1610612740, season, team.TeamGameLogs)
chi_logs = get_team_logs(1610612741, season, team.TeamGameLogs)
dal_logs = get_team_logs(1610612742, season, team.TeamGameLogs)
den_logs = get_team_logs(1610612743, season, team.TeamGameLogs)
gsw_logs = get_team_logs(1610612744, season, team.TeamGameLogs)
hou_logs = get_team_logs(1610612745, season, team.TeamGameLogs)
lac_logs = get_team_logs(1610612746, season, team.TeamGameLogs)
lal_logs = get_team_logs(1610612747, season, team.TeamGameLogs)
mia_logs = get_team_logs(1610612748, season, team.TeamGameLogs)
min_logs = get_team_logs(1610612750, season, team.TeamGameLogs)
bkn_logs = get_team_logs(1610612751, season, team.TeamGameLogs)
nyk_logs = get_team_logs(1610612752, season, team.TeamGameLogs)
orl_logs = get_team_logs(1610612753, season, team.TeamGameLogs)
ind_logs = get_team_logs(1610612754, season, team.TeamGameLogs)
phi_logs = get_team_logs(1610612755, season, team.TeamGameLogs)
phx_logs = get_team_logs(1610612756, season, team.TeamGameLogs)
por_logs = get_team_logs(1610612757, season, team.TeamGameLogs)
sac_logs = get_team_logs(1610612758, season, team.TeamGameLogs)
sas_logs = get_team_logs(1610612759, season, team.TeamGameLogs)
okc_logs = get_team_logs(1610612760, season, team.TeamGameLogs)
uta_logs = get_team_logs(1610612762, season, team.TeamGameLogs)
mem_logs = get_team_logs(1610612763, season, team.TeamGameLogs)
was_logs = get_team_logs(1610612764, season, team.TeamGameLogs)
det_logs = get_team_logs(1610612765, season, team.TeamGameLogs)
cha_logs = get_team_logs(1610612766, season, team.TeamGameLogs)
"""


#pprint(team.TeamGameLogs(nba_teams[1]['_id'], '2017-18'))
