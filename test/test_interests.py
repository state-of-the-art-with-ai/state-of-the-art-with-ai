from state_of_the_art.preferences.interest_table import Interests


def test_topic_crud():
    topics = Interests()
    original_size = topics.len()
    topics.add(name="foo", description="bar")
    topics.add(name="baz", description="bar")
    new_size = topics.len()
    assert new_size == (original_size + 2)

    topics.delete_by(column="name", value="foo")
    new_size = topics.len()

    assert new_size == (original_size + 1)

    Interests().delete_by(column="name", value="baz")
