import datetime

from s2_analytics.collect.object_collector import GameObjectCollector
from s2_analytics.filters import PLAYLIST_CTF, BALANCED
from s2_analytics.importer import import_games
from s2_analytics.tools import process_games
from tests.game_builder import GameBuilderFactory
from tests.project_root import get_project_root

TEST_DB = "/tmp/s2_ranked_test.sql"
TIME_LIMIT_SECONDS = 2


def test_import_cant_be_too_long():
    start = datetime.datetime.now().timestamp()
    collector = GameObjectCollector()
    import_games(get_project_root() + "/logs_ranked/", period_days=30, processors=[collector], game_filters=[PLAYLIST_CTF])
    end = datetime.datetime.now().timestamp()

    assert len(collector.games) > 100
    assert end - start < TIME_LIMIT_SECONDS


def test_filtering_games_by_properties():
    games = GameBuilderFactory(teams={"Red": ["A"], "Blue": ["B"]}) \
        .add_game(match_quality=0.9, game_start_time=123) \
        .add_round() \
        .add_cap(player="A") \
        .build() \
        .add_game(match_quality=0.8, game_start_time=124) \
        .add_round() \
        .add_cap(player="A") \
        .build() \
        .finish()

    collector = GameObjectCollector()
    process_games(games, [collector])
    assert len(collector.games) == 2

    collector = GameObjectCollector()
    process_games(games, [collector], [lambda g: g.match_quality > 0.85])
    assert len(collector.games) == 1
    assert collector.games[0].details.match_quality == 0.9


class TestFiltering:
    def setup_method(self):
        self.collector = GameObjectCollector()

    def test_generates_overview_of_data_set(self):
        teams = {"Red": ["A"], "Blue": ["B"]}
        games = GameBuilderFactory(teams=teams) \
            .add_game(game_start_time=10, teams_win_probability={"Red": 0.45, "Blue": 0.55}) \
            .build() \
            .add_game(game_start_time=20, teams_win_probability={"Red": 0.39, "Blue": 0.61}) \
            .build() \
            .finish()

        process_games(games, [self.collector], game_filters=[BALANCED])

        assert len(self.collector.games) == 1
        assert self.collector.games[0].details.team_win_probabilities["Red"] == 0.45
