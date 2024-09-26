from state_of_the_art.insight_extractor.insight_extractor import (
    convert_questions_to_openai_call,
)
from state_of_the_art.tables.questions_table import QuestionsTable


@pytest.mark.skipif(True, reason="not ready yet")
def test_convert():
    questions = QuestionsTable()
    df = questions.read()

    result = convert_questions_to_openai_call(df)
    assert result["Institution"]["type"] == "string"
    assert result["Institution"]["description"] is not None

    assert result["Resources"]["type"] == "array"
    assert result["Resources"]["items"]["type"] == "string"
    assert result["Resources"]["minItems"] is not None
    assert isinstance(result["Resources"]["minItems"], int)
    assert result["Resources"]["description"] is not None

    print(result)
