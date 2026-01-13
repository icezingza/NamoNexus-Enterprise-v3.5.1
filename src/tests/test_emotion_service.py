import pytest

from src.services.emotion_service import EmotionService
from src.utils.exceptions import InvalidInputError


@pytest.fixture()
def emotion_service():
    return EmotionService()


class TestEmotionService:
    def test_analyze_sentiment_positive(self, emotion_service):
        result = emotion_service.analyze_sentiment("ฉันดีใจมาก")
        assert result["emotion"] == "joy"
        assert result["intensity"] == 7.0

    def test_analyze_sentiment_negative(self, emotion_service):
        result = emotion_service.analyze_sentiment("ฉันรู้สึกเศร้า")
        assert result["emotion"] == "sadness"
        assert result["intensity"] == 6.0

    def test_analyze_sentiment_neutral(self, emotion_service):
        result = emotion_service.analyze_sentiment("วันนี้อากาศดี")
        assert result["emotion"] == "neutral"

    def test_analyze_sentiment_empty_message(self, emotion_service):
        with pytest.raises(InvalidInputError):
            emotion_service.analyze_sentiment("")

    def test_analyze_sentiment_invalid_type(self, emotion_service):
        with pytest.raises(InvalidInputError):
            emotion_service.analyze_sentiment(None)  # type: ignore[arg-type]
