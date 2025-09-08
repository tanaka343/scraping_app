
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
from flask import Flask,render_template,redirect,request,send_from_directory,session,send_file,flash
import os
import io


app = Flask(__name__)
app.secret_key ='abfdie1w4e2e5'

@app.route('/')
def top():
  """
    アプリのトップページを表示する関数

    - 空の施設リストを作成する
    - index.html テンプレートを描画して返す

    Returns:
        str: レンダリングされたHTML（index.html）
  """
  facility_list=[]
  return render_template('index.html',facility_list=facility_list)

  
@app.route('/search',methods=['GET'])
def search():
  """
    施設検索を実行し、結果を表示する関数

    - ユーザーが入力した地域名（input_location）を取得
    - 入力がない場合はトップページ（index.html）に戻る
    - 直前と同じ入力なら、セッションに保存してある検索結果を再利用
    - 新しい入力なら main() を実行してスクレイピングし、DataFrameに変換
    - 例外（ValueError, TimeoutException, その他）が発生した場合はエラーを表示してトップにリダイレクト
    - 正常に結果が得られた場合は output.html に施設リストを渡して表示する

    Returns:
        str: レンダリングされたHTML（index.html または output.html）
  """
  #ユーザーが入力した地域の取得
  input_location=request.args.get('input_location')
  #入力がなければ、トップページへ移動
  if not input_location:
    return render_template('/index.html')
  
  df = None 
  if session.get('last_input')==input_location and session.get('my_dataframe'):
    json_data=session.get('my_dataframe')
    df=pd.read_json(json_data,orient='split')
  else:
    try:
      # facility_list = main(input_location)
      # num=len(facility_list)
      df = main(input_location)
      session['my_dataframe']=df.to_json(orient='split')
      session['last_input']=input_location

    except ValueError as e:
      flash(f'[入力エラー]{e}入力内容：{input_location}','error')
      return redirect('/')
    
    except TimeoutException as e:
      flash(f'[入力エラー]{e}入力内容：{input_location}','error')
      return redirect('/')
    
    except Exception as e:
      flash('予期せぬエラーが発生しました。','error')
      return redirect('/')
    
  if df is not None:
    facility_list = df.to_dict(orient='records')
    return render_template('/output.html',facility_list=facility_list,input_location=input_location)
  else:
    return redirect('/')
# base_dir = os.path.dirname(__file__)
# DOWNLOAD_DIR_PATH = os.path.join(base_dir,'自動化アプリ出力')


XLSX_MIMETYPE='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
CSV_MIMETYPE = 'text/csv'

@app.route('/download', methods=['GET','POST'])
def download():
  """
    セッション内のDataFrameをCSVまたはExcel形式でダウンロードする。

    POST:
        - session['my_dataframe'] を取得して DataFrame に変換
        - request.form['download'] で形式を判定 ("csv" or "excel")
        - BytesIO バッファに書き込み
        - send_file でダウンロード送信

    GET:
        - output.html を表示
  """
  if request.method=='POST':
    json_data = session.get('my_dataframe')
    input_location=session.get('last_input')
    df=pd.read_json(json_data,orient='split')
    download_type=request.form.get('download')
    output_buffer = io.BytesIO()

    if download_type=="csv":
      df.to_csv(output_buffer,index=False)
      downloadFileName =f'{input_location}.csv'
      
      file_mimetype = CSV_MIMETYPE
    elif download_type=="excel":
      
      downloadFileName =f'{input_location}.xlsx'
      
      file_mimetype =XLSX_MIMETYPE
      with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'{input_location}')

    
    output_buffer.seek(0)
    # session.pop('my_dataframe', None) 
  
    return send_file(output_buffer,  \
        mimetype=file_mimetype,as_attachment = True, download_name = downloadFileName)
  return render_template('/output.html')


def main(input_location):
  """
  全体の処理を実行する関数

  -地域名とExcelファイルパスをユーザーから受け取る
  -地域名を「都道府県名」と「市町村名」に分割・整形
  -ウェブ上から施設情報をスクレイピングして、辞書のリストとして返す
  -辞書のリストをpandasのデータフレームに変換
  -ユーザーが指定したExcelファイルを加工し、パスとシート名を返す
  -Excelファイルの指定シートに抽出した情報を書き込み
  
  """
  # try:
    # input_location,excel_path =get_user_input()
  prefecture,city_name =split_address(input_location)
  facility_data_list =scrape_data(input_location,prefecture,city_name)
  df = pd.DataFrame(facility_data_list) 
  # excel_path,sheet_name =copy_template_sheet(excel_path,city_name)   
  # write_to_excel(excel_path,df,sheet_name)

  print(df)
  print(f"\033[0m\033[32m\033[1m処理が正常に完了しました。\033[0m")
  return df
  # except ValueError :
  #   print('入力形式が正しくありません。')
  #   sys.exit(1)
  # except PermissionError:
  #   print('excelファイルを閉じてください。')
  #   sys.exit(1)

  # except TimeoutException as e:
  #   print(f"エラーが発生:{e}")
  #   sys.exit(1)
  # except Exception:
  #   print('予期せぬエラーが発生しました。')
  #   import traceback
  #   traceback.print_exc()

  

if __name__ == "__main__":
  #  main()
  app.run()
 
