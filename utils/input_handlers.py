import re


def get_user_input() -> tuple[str,str]: 
  """ユーザーから地域とフォルダパスを取得する"""
  S=input('地域を入力 （例：東京都豊島区）')
  row_path=input('excelファイルパスを入力').strip().replace('"','')
  return S,row_path

def format_input_data(S) -> tuple[str,str]:
  """
  都道府県名と市区町村名を取得する

  Parameters:
    S (str): ユーザーが入力した地域名

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
 
  match=re.search(r'北海道(.*)',S)
  match2=re.search(r'京都府(.*)',S)
  if match:
    todou='北海道'
    siku= match.group(1)
  elif match2:
    todou='京都'
    siku=match2.group(1)
  else:
    todou,siku=re.split(r'都|府|県',S,maxsplit=2,flags=0)
  return todou,siku
