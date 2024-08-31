from state_of_the_art.tables.comments_table import Comments


def test_comment():
    comment = Comments()
    comment.add(message="foo", paper_url="bar")

    df = comment.read()
    df.iloc[0].to_dict() == {"comment": "foo", "paper_url": "bar"}
