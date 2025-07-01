import pandas as pd
import openpyxl
import sys 
from pathlib import Path


def copy_template_sheet(excel_path:str,city_name:str) -> tuple[str,str]:
  """
  Excelシートのテンプレートをコピーしてシート名をcity_nameにする

  Parameters:
    excel_path (str): ユーザーが入力したExcelのパス
    city_name (str): 市区町村名

  Returns:
    tuple[str,str]: 加工したExcelのパスとシート名

  Note:
    既存のシート名が入力された場合Excelが自動的にsheet_name,sheet_name1,sheet_name2と
    割り当てるため、copy_sheet.titleにcity_nameを代入した後
    sheet_nameにcopy_sheet.titleを代入することで、実際に割り当てられたsheet_nameを取得している。
  """ 
  excel_path =Path(excel_path)
  workbook =openpyxl.load_workbook(excel_path)
  copy_sheet =workbook.copy_worksheet(workbook['テンプレート※コピーして名前を都市名に変更して使用'])
  copy_sheet.title =city_name
  sheet_name = copy_sheet.title#シート名が重複した場合に対応（例：豊島区、豊島区1）
  workbook.active=copy_sheet
  workbook.save(excel_path)
  return excel_path,sheet_name
  

def  write_to_excel(excel_path:str,df:pd.DataFrame,sheet_name:str) -> None:
  """
  取得した施設情報データを既存のExcelファイルの指定シートに書き込む
  
  Parameters:
    excel_path (str) : 加工済みExcelファイルのパス（create_excelsheet()で生成）
    df (pd.DataFrame) : 施設情報を格納したデータフレーム
    sheet_name (str) : 書き込み対象のシート名（変数city_name）

  Returns: None
  
  Note:
    Excelファイルはopenpyxlを使用して追記している。
    データは行１、列Ａから書き込みヘッダーとインデックスは書きこまない。
  """
  with pd.ExcelWriter(excel_path,engine="openpyxl",mode="a",if_sheet_exists="overlay") as writer:
    df.to_excel(writer,sheet_name=sheet_name,startrow=1,startcol=0,header=False,index=False)

