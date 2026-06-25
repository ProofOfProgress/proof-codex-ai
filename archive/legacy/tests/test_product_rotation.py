from unittest.mock import MagicMock

from shorts_bot.production.product_rotation import next_product_topic, product_name_from_topic


def test_product_name_from_topic():
    assert product_name_from_topic("ChatGPT Plus — honest verdict") == "ChatGPT Plus"


def test_next_product_topic_rotates():
    store = MagicMock()
    store.get_channel_state.side_effect = lambda k: "0" if k == "invideo_product_index" else None
    store.list_drafts.return_value = []

    t1 = next_product_topic(store)
    assert t1
    store.get_channel_state.side_effect = lambda k: "1" if k == "invideo_product_index" else None
    t2 = next_product_topic(store)
    assert t2
