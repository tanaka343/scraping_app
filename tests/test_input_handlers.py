from utils import input_handlers

def test_format_input_data():
    prefecture,city_name = input_handlers.format_input_data("東京都豊島区")
    assert prefecture== "東京"
    assert city_name == "豊島区"