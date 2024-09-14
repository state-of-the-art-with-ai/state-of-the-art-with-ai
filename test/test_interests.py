from state_of_the_art.tables.interest_table import InterestsTable


def test_topic_crud():
    topics = InterestsTable()
    original_size = topics.len()
    topics.add(name="foo", description="bar")
    topics.add(name="baz", description="bar")
    new_size = topics.len()
    assert new_size == (original_size + 2)

    topics.delete_by(column="name", value="foo")
    new_size = topics.len()

    assert new_size == (original_size + 1)

    InterestsTable().delete_by(column="name", value="baz")
