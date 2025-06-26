import pandas as pd
import openpyxl
import sys 
from pathlib import Path

def create_excelsheet(row_path:str,siku:str) -> tuple[str,str]:
  """
  Excelシートのテンプレートをコピーしてシート名をsikuにする

  Parameters:
    row_path (str): ユーザーが入力したExcelのパス
    siku (str): 市区町村名

  Returns:
    tuple[str,str]: 加工したExcelのパスとシート名

  Note:
    既存のシート名が入力された場合Excelが自動的にsheet_name,sheet_name1,sheet_name2と
    割り当てるため、copy_sheet.titleにsikuを代入した後
    sheet_nameにcopy_sheet.titleを代入することで、実際に割り当てられたsheet_nameを取得している。
  """
  try: 
    wb_path =Path(row_path)
    wb =openpyxl.load_workbook(wb_path)
    copy_sheet =wb.copy_worksheet(wb['テンプレート※コピーして名前を都市名に変更して使用'])
    copy_sheet.title =siku
    sheet_name = copy_sheet.title#シート名が重複した場合に対応（例：豊島区、豊島区1）
    wb.active=copy_sheet
    wb.save(wb_path)
    return wb_path,sheet_name
  except PermissionError:
    print('excelファイルを閉じてください。')
    sys.exit(1)

def  write_to_excel(wb_path:str,df_houdei:pd.DataFrame,sheet_name:str) -> None:
  """
  取得した施設情報データを既存のExcelファイルの指定シートに書き込む
  
  Parameters:
    wb_path (str) : 加工済みExcelファイルのパス（create_excelsheet()で生成）
    df_houdei (pd.DataFrame) : 施設情報を格納したデータフレーム
    sheet_name (str) : 書き込み対象のシート名（変数siku）

  Returns: None
  
  Note:
    Excelファイルはopenpyxlを使用して追記している。
    データは行１、列Ａから書き込みヘッダーとインデックスは書きこまない。
  """
  with pd.ExcelWriter(wb_path,engine="openpyxl",mode="a",if_sheet_exists="overlay") as writer:
    df_houdei.to_excel(writer,sheet_name=sheet_name,startrow=1,startcol=0,header=False,index=False)

