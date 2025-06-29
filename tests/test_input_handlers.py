from utils import input_handlers

def test_format_input_data():
    todou,siku = input_handlers.format_input_data("東京都豊島区")
    assert todou== "東京"
    assert siku == "豊島区"