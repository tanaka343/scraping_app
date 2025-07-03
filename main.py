
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement
from utils.input_handlers import get_user_input,split_address
from utils.data_extractors import scrape_data
from results.output import copy_template_sheet,write_to_excel
import sys 
from utils.selenium_helpers import get_site

def main():
  """
  全体の処理を実行する関数

  -地域名とExcelファイルパスをユーザーから受け取る
  -地域名を「都道府県名」と「市町村名」に分割・整形
  -ウェブ上から施設情報をスクレイピングして、辞書のリストとして返す
  -辞書のリストをpandasのデータフレームに変換
  -ユーザーが指定したExcelファイルを加工し、パスとシート名を返す
  -Excelファイルの指定シートに抽出した情報を書き込み
  
  """

  try:
    input_location,excel_path =get_user_input()
    prefecture,city_name =split_address(input_location)
    facility_data_list =scrape_data(input_location,prefecture,city_name)
    df = pd.DataFrame(facility_data_list) 
    # excel_path,sheet_name =copy_template_sheet(excel_path,city_name)   
    # write_to_excel(excel_path,df,sheet_name)

    print(df)
    print(f"\033[0m\033[32m\033[1m処理が正常に完了しました。\033[0m")

  except ValueError :
    print('入力形式が正しくありません。')
    sys.exit(1)
  except PermissionError:
    print('excelファイルを閉じてください。')
    sys.exit(1)

  except TimeoutException as e:
    print(f"エラーが発生:{e}")
    sys.exit(1)
  except Exception:
    print('予期せぬエラーが発生しました。')
    import traceback
    traceback.print_exc()

  

if __name__ == "__main__":
   main()