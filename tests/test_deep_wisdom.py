from namo_nexus.cog.deep_wisdom import DeepWisdom
from src.i18n import load_locale


LOCALE = load_locale("th")

def test_deep_wisdom_initialization():
    dw = DeepWisdom()
    assert dw._principles == LOCALE["tests"]["deep_wisdom_principles"]

def test_get_relevant_principles():
    dw = DeepWisdom()
    message = "I feel sad"
    context = {}
    principles = dw.get_relevant_principles(message, context)
    assert principles == LOCALE["tests"]["deep_wisdom_default"]
