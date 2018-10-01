

#imports
from datetime import datetime
from io import StringIO

# global variables

season = "2017-2018"
log = StringIO()  # container for logs
runtime_timestamp = datetime.today()

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

scoreboard_line_score_headers = ['GAME_DATE_EST', 'GAME_SEQUENCE', 'GAME_ID', 'TEAM_ID', 'TEAM_ABBREVIATION',
                                 'TEAM_CITY_NAME', 'TEAM_WINS_LOSSES', 'PTS_QTR1', 'PTS_QTR2', 'PTS_QTR3', 'PTS_QTR4',
                                 'PTS_OT1', 'PTS_OT2', 'PTS_OT3', 'PTS_OT4', 'PTS_OT5', 'PTS_OT6', 'PTS_OT7', 'PTS_OT8',
                                 'PTS_OT9', 'PTS_OT10', 'PTS', 'FG_PCT', 'FT_PCT', 'FG3_PCT', 'AST', 'REB', 'TOV']

scoreboard_line_score_headers_lower = ['game_date_est', 'game_sequence', 'game_id', 'team_id', 'team_abbreviation',
                                       'team_city_name', 'team_wins_losses', 'pts_qtr1', 'pts_qtr2', 'pts_qtr3',
                                       'pts_qtr4', 'pts_ot1', 'pts_ot2', 'pts_ot3', 'pts_ot4', 'pts_ot5', 'pts_ot6',
                                       'pts_ot7', 'pts_ot8', 'pts_ot9', 'pts_ot10', 'pts', 'fg_pct', 'ft_pct',
                                       'fg3_pct', 'ast', 'reb', 'tov']
