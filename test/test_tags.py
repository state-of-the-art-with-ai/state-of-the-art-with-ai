

from state_of_the_art.tables.tags_table import TagsTable


def test_tags():
    user_id = '16db56fe-18d0-41fe-b56c-4b703e79a170'
    tags_table = TagsTable(auth_callable=lambda: user_id)
    tags_table.add_tag_to_paper("http://arxiv.org/abs/2410.02749", "tag1")
    df = tags_table.read()
    df = df[df['paper_id'] == "http://arxiv.org/abs/2410.02749"]
    assert 'tag1' in df.iloc[0].tags
    assert user_id == df.iloc[0].user_uuid
