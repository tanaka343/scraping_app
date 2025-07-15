import re


def get_user_input() -> tuple[str,str]: 
  """ユーザーから地域とフォルダパスを取得する"""
  input_location=input('地域を入力 （例：東京都豊島区）')
  excel_path =input('excelファイルパスを入力').strip().replace('"','')
  return input_location,excel_path


def split_address(input_location) -> tuple[str,str]:
  """
  都道府県名と市区町村名を取得する

  Parameters:
    input_location (str): ユーザーが入力した地域名

  Returns:
    tuple[str,str]: 都道府県名と市区町村名のタプル
          例:
            - '東京都豊島区' -> ('東京','豊島区')
            - '北海道札幌市' -> ('北海道','札幌市')
            - '京都府京都市' -> ('京都','京都市')

  Note:
    北海道は、都道府県名の接尾辞を除外しない文字列を取得したいため、
    京都府は、都道府県名に複数の接尾辞（例: 都・府）が含まれるため、
    正規表現 split ではなく個別に処理しています。
    例: '京都府京都市' は re.split(r'都|府|県', ...) を使うと分割数が不正になりエラーが出ます。
  """
 
  match=re.match(r'北海道(.*)',input_location)
  match2=re.match(r'京都府(.*)',input_location)
  if match:
    prefecture='北海道'
    city_name= match.group(1)
  elif match2:
    prefecture='京都'
    city_name=match2.group(1)
  else:
    locations=re.split(r'都|府|県',input_location,maxsplit=1,flags=0)
    if len(locations)<2 or locations[1]=='' or re.match("　",locations[1]):
      raise ValueError("都道府県と市区町村を分割できません。")
    prefecture,city_name=locations
  return prefecture,city_name
