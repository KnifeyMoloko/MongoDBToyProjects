from nba_api.stats.endpoints import scoreboardv2 as scoreboard
import pandas as pd
import logging
from pprint import pprint


def main():
    logger = logging.getLogger(__name__)
    # game_id = '0021900017'  # taken from 'https://stats.nba.com/game/0021900017/'
    s = scoreboard.ScoreboardV2().get_normalized_json()
    pprint(s)


if __name__ == "__main__":
    main()
