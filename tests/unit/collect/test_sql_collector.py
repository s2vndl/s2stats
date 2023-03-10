from os.path import dirname, abspath

from s2_analytics.collect.sqlite_collector import SqliteCollector
from s2_analytics.importer import import_games
from tests.project_root import get_project_root

TEST_DB = "/tmp/s2_ranked_test.sql"

TIME_LIMIT_SECONDS = 2


def test_building_sqlite_db():
    collector = SqliteCollector("file::memory:").init()
    import_games(get_project_root() + "/fixtures", period_days=99999,
                 processors=[collector])
    con = collector.connection
    assert 1 == con.cursor().execute("select count(*) from game").fetchone()[0]
    assert 2 == con.cursor().execute("select count(*) from round").fetchone()[0]
    assert 3 == con.cursor().execute("select count(*) from event_kill").fetchone()[0]
    assert 2 == con.cursor().execute("select count(*) from event_cap").fetchone()[0]
