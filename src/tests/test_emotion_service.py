import pytest

from src.i18n import load_locale
from src.services.emotion_service import EmotionService
from src.utils.exceptions import InvalidInputError


LOCALE = load_locale("th")


@pytest.fixture()
def emotion_service():
    return EmotionService()


class TestEmotionService:
    def test_analyze_sentiment_positive(self, emotion_service):
        result = emotion_service.analyze_sentiment(
            LOCALE["tests"]["messages"]["emotion_positive"]
        )
        assert result["emotion"] == "joy"
        assert result["intensity"] == 7.0

    def test_analyze_sentiment_negative(self, emotion_service):
        result = emotion_service.analyze_sentiment(
            LOCALE["tests"]["messages"]["emotion_negative"]
        )
        assert result["emotion"] == "sadness"
        assert result["intensity"] == 6.0

    def test_analyze_sentiment_neutral(self, emotion_service):
        result = emotion_service.analyze_sentiment(
            LOCALE["tests"]["messages"]["emotion_neutral"]
        )
        assert result["emotion"] == "neutral"

    def test_analyze_sentiment_empty_message(self, emotion_service):
        with pytest.raises(InvalidInputError):
            emotion_service.analyze_sentiment("")

    def test_analyze_sentiment_invalid_type(self, emotion_service):
        with pytest.raises(InvalidInputError):
            emotion_service.analyze_sentiment(None)  # type: ignore[arg-type]
