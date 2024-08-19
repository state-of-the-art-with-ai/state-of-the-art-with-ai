from state_of_the_art.utils.base_table import BaseTable


class TestTable(BaseTable):
    table_name = "test_table"
    schema = {
        "col_1": {"type": str},
        "col_2": {"type": str},
    }


tt = TestTable()


def test_reset_table():
    tt.add(col_1=111, col_2=222)
    assert tt.len() > 0
    tt.reset(dry_run=False)
    assert tt.len() == 0
    tt.add(col_1=111, col_2=222)
    assert tt.len() == 1


def test_update_or_create():
    tt.reset()
    tt.add(col_1=111, col_2=222)
    tt.add(col_1=222, col_2=333)
    assert tt.len() == 2

    # first create
    tt.update_or_create(
        by_key="col_1", by_value=333, new_values={"col_1": 333, "col_2": 444}
    )

    assert tt.len() == 3
    # now upodates
    tt.update_or_create(
        by_key="col_1", by_value=333, new_values={"col_1": 444, "col_2": 555}
    )
    assert tt.len() == 3
    df = tt.read(recent_first=True)

    assert len(df[df["col_1"] == 444].index) == 1
