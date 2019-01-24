#imports
from datetime import datetime
from io import StringIO

# global variables

season = "2018-19"
log = StringIO()  # container for logs
runtime_timestamp = datetime.today()
mongodb_path = '/home/newton/Programming/MDB/'
postgresql_username = 'newton'
postgresql_dbname = 'newton'
postgresql_host_type = '/tmp/'
# NOTE: the db names are in a list for convenience for the price of flexibility
local_postgresql_db = ["nba1819_line_score",
                       "nba1819_series_standing",
                       "nba1819_last_meeting",
                       "nba1819_east_conference_standings_by_day",
                       "nba1819_west_conference_standings_by_day"]

remote_postgresql_db = ["line_score",
                        "series_standing",
                        "last_meeting",
                        "east_conference_standings_by_day",
                        "west_conference_standings_by_day"]


# Logger object configuration
logger_root_config = {'version': 1,
                      'disable_existing_loggers': False,
                      'loggers':
                          {
                              '':
                                  {
                                      'level': 'DEBUG',
                                      'handlers': ['file_handler', 'string_handler', 'terminal']
                                  },
                              'helpers_logger':
                                  {
                                      'level': 'DEBUG',
                                      'handlers': ['file_handler', 'string_handler', 'terminal']
                                  }
                          },
                      'formatters':
                          {
                              'default':
                                  {
                                      'format': '%(asctime)s : %(name)s : %(funcName)s : %(lineno)d '
                                                ': %(levelname)s : %(message)s'
                                  }
                          },
                      'handlers':
                          {
                              'file_handler':
                                  {
                                      'class': 'logging.FileHandler',
                                      'filename': './logs/runtimeLog' + str(runtime_timestamp),
                                      'formatter': 'default'
                                  },
                              'string_handler':
                                  {
                                      'class': 'logging.StreamHandler',
                                      'stream': log,
                                      'formatter': 'default'
                                  },
                              'terminal':
                                  {
                                      'class': 'logging.StreamHandler',
                                      'formatter': 'default'
                                  }
                          }
                      }

nba_teams = [{'team_abbreviation': 'MIL', '_id': 1610612749},
             {'team_abbreviation': 'TOR', '_id': 1610612761},
             {'team_abbreviation': 'ATL', '_id': 1610612737},
             {'team_abbreviation': 'BOS', '_id': 1610612738},
             {'team_abbreviation': 'CLE', '_id': 1610612739},
             {'team_abbreviation': 'NOP', '_id': 1610612740},
             {'team_abbreviation': 'CHI', '_id': 1610612741},
             {'team_abbreviation': 'DAL', '_id': 1610612742},
             {'team_abbreviation': 'DEN', '_id': 1610612743},
             {'team_abbreviation': 'GSW', '_id': 1610612744},
             {'team_abbreviation': 'HOU', '_id': 1610612745},
             {'team_abbreviation': 'LAC', '_id': 1610612746},
             {'team_abbreviation': 'LAL', '_id': 1610612747},
             {'team_abbreviation': 'MIA', '_id': 1610612748},
             {'team_abbreviation': 'MIN', '_id': 1610612750},
             {'team_abbreviation': 'BKN', '_id': 1610612751},
             {'team_abbreviation': 'NYK', '_id': 1610612752},
             {'team_abbreviation': 'ORL', '_id': 1610612753},
             {'team_abbreviation': 'IND', '_id': 1610612754},
             {'team_abbreviation': 'PHI', '_id': 1610612755},
             {'team_abbreviation': 'PHX', '_id': 1610612756},
             {'team_abbreviation': 'POR', '_id': 1610612757},
             {'team_abbreviation': 'SAC', '_id': 1610612758},
             {'team_abbreviation': 'SAS', '_id': 1610612759},
             {'team_abbreviation': 'OKC', '_id': 1610612760},
             {'team_abbreviation': 'UTA', '_id': 1610612762},
             {'team_abbreviation': 'MEM', '_id': 1610612763},
             {'team_abbreviation': 'WAS', '_id': 1610612764},
             {'team_abbreviation': 'DET', '_id': 1610612765},
             {'team_abbreviation': 'CHA', '_id': 1610612766}]

scoreboard_line_score_headers = ['GAME_DATE_EST', 'GAME_SEQUENCE', 'GAME_ID', 'TEAM_ID', 'TEAM_ABBREVIATION',
                                 'TEAM_CITY_NAME', 'TEAM_WINS_LOSSES', 'PTS_QTR1', 'PTS_QTR2', 'PTS_QTR3', 'PTS_QTR4',
                                 'PTS_OT1', 'PTS_OT2', 'PTS_OT3', 'PTS_OT4', 'PTS_OT5', 'PTS_OT6', 'PTS_OT7', 'PTS_OT8',
                                 'PTS_OT9', 'PTS_OT10', 'PTS', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'AST', 'REB', 'TOV']

scoreboard_line_score_headers_lower = ['game_date_est', 'game_sequence', 'game_id', 'team_id', 'team_abbreviation',
                                       'team_city_name', 'team_wins_losses', 'pts_qtr1', 'pts_qtr2', 'pts_qtr3',
                                       'pts_qtr4', 'pts_ot1', 'pts_ot2', 'pts_ot3', 'pts_ot4', 'pts_ot5', 'pts_ot6',
                                       'pts_ot7', 'pts_ot8', 'pts_ot9', 'pts_ot10', 'pts', 'fg_pct', 'ft_pct',
                                       'fg3_pct', 'ast', 'reb', 'tov']
