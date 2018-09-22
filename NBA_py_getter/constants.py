

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