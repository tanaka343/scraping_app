
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
from utils.input_handlers import get_user_input,format_input_data
from utils.data_extractors import scrape_data



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
  S,row_path =get_user_input()
  todou,siku =format_input_data(S)
  list_houdei =scrape_data(S,todou,siku)
  df_houdei = pd.DataFrame(list_houdei) 
  # wb_path,sheet_name =create_excelsheet(row_path,siku)   
  # write_to_excel(wb_path,df_houdei,sheet_name)

  print(df_houdei)
  print(f"\033[0m\033[32m\033[1m処理が正常に完了しました。\033[0m")

if __name__ == "__main__":
   main()