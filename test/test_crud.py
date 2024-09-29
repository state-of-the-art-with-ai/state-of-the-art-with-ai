from state_of_the_art.tables.base_table import BaseTable


class TestTable(BaseTable):
    table_name = "test_table"
    schema = {
        "name": {"type": str},
        "description": {"type": str},
    }


def test_topic_crud():
    topics = TestTable()
    original_size = topics.len()
    topics.add(name="foo", description="bar")
    topics.add(name="baz", description="bar")
    new_size = topics.len()
    assert new_size == (original_size + 2)

    topics.delete_by(column="name", value="foo")
    new_size = topics.len()

    assert new_size == (original_size + 1)

    TestTable().delete_by(column="name", value="baz")
