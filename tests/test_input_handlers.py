import pytest
from utils import input_handlers

# def test_format_input_data():
#     prefecture,city_name = input_handlers.format_input_data("東京都豊島区")
#     assert prefecture== "東京"
#     assert city_name == "豊島区"

@pytest.mark.parametrize("input_location,expected",[
    ('東京都豊島区',('東京','豊島区')),
    ('北海道札幌市',('北海道','札幌市')),
    ('北海道札',('北海道','札'))#select_city_nameでエラーを拾う
])
def test_split_address_normal(input_location,expected):
    assert input_handlers.split_address(input_location) == expected


@pytest.mark.parametrize("input_location",[
    '',
    '札幌市',#都道府県名なし
    '東京都',#市区町村名なし
    '東京',
    '東京都　豊島区'
])
def test_split_address_invalid_raises(input_location):
    with pytest.raises(ValueError):
        input_handlers.split_address(input_location)


@pytest.mark.parametrize("input_location,expected",[
    ('東京都府中市',('東京','府中市')),#市町村名に「府」
    ('京都府京都市',('京都','京都市')),#都道府県名に「都」「府」
])
def test_split_address_boundary(input_location,expected):
    assert input_handlers.split_address(input_location)== expected