
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import openpyxl
import re
import sys 
from pathlib import Path
from selenium.webdriver.remote.webelement import WebElement

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
  try:
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
  except ValueError:
      print('入力形式が正しくありません。')
      sys.exit(1)

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

def get_site() -> webdriver.Chrome:
  """chromeドライバーを開き対象ページを開く"""
  options = Options()
  options.add_experimental_option("detach", True)
  driver = webdriver.Chrome(options=options)
  driver.get("" \
  "https://www.wam.go.jp/sfkohyoout/COP000100E0000.do")
  return driver

def select_todou(driver:webdriver.Chrome,todou:str) -> None:
  """都道府県の選択操作を行う"""
  try:
    todou_locator = (By.XPATH,f"//a[text()='{todou}']")
    todou_a =WebDriverWait(driver,10).until(
      EC.element_to_be_clickable(todou_locator)
    )
    todou_a.click()
  except TimeoutException:
    print('都道府県名が正しくありません。')
    driver.close()
    sys.exit(1)
  
def select_siku(driver:webdriver.Chrome,siku:str) -> None:
  """市町村の選択操作を行う"""
  try:
    siku_locator = (By.XPATH,f"//a[@title='{siku}']")
    siku_a =WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(siku_locator))
    siku_a.click()
  except TimeoutException:
    print('市区町村名が正しくありません。')
    driver.close()
    sys.exit(1)

def wait_and_click(driver:webdriver.Chrome,locator:str) -> None:
  """クリック可能になるまで待機、要素を取得してクリック"""
  element =WebDriverWait(driver,20).until(
    EC.element_to_be_clickable(locator)
  )
  element.click()

def kirikae(driver:webdriver.Chrome,locator:tuple[str,str],text:str) -> None:
  """
  画面が完全に切り替わるまで待機する

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    locator (tuple[str,str]): Byクラスとセレクタ文字列のタプル (例: (By.CLASS_NAME, 'my-class'))
    text (str): 画面切り替え後に表示される文字列

  Returns: None

  Note:
    画面が完全に切り替わる前に要素を取得してしまうことを防ぐために、
    画面切り替え後にブラウザ上に表示されるはずのテキストが現れるまで待機する。
  """
  WebDriverWait(driver,30).until(
    EC.text_to_be_present_in_element(locator,text)
  )

def all_element(driver:webdriver.Chrome,locator:tuple[str,str]) -> list[WebElement]:
  """すべての要素が表示されるまで待機して要素を取得"""
  elements =WebDriverWait(driver,20).until(
        EC.visibility_of_all_elements_located(locator)
      )
  return elements

def js_click(driver:webdriver.Chrome,locator:tuple[str,str]) -> None:
  """ 
  jsでしか操作できない部分をクリック

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    locator (tuple[str,str]): Byクラスとセレクタ文字列のタプル (例: (By.CLASS_NAME, 'my-class'))

  Returns: None

  Note:
    ドロップダウンメニュー内のチェックボックスをクリックする動作がSeleniumのブラウザ操作では実行できなかったため、
    javascriptで直接クリックしています。
  """
  element =WebDriverWait(driver,30).until(
      EC.presence_of_element_located(locator)
  )
  driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });",element)
  driver.execute_script("arguments[0].click();",element)

def open_link_in_newtab(driver:webdriver.Chrome,element:WebElement) -> str:
  """リンクを新しいタブで開き、そちらに切り替える"""    
  #前タブ情報取得
  original_tab =driver.current_window_handle
  initial_tabs =driver.window_handles
  #urlを新しいタブで開く
  driver.execute_script("window.open(arguments[0].href,'_blank');",element)

  #後タブを取得
  current_tabs =driver.window_handles
  #新しいタブの取得移動
  set_initial_tabs = set(initial_tabs)
  set_current_tabs = set(current_tabs)
  new_set= set_current_tabs-set_initial_tabs
  new_tab = new_set.pop()
  driver.switch_to.window(new_tab)
  return original_tab

def to_originaltab(driver:webdriver.Chrome,original_tab:str) -> None:
  """現在のタブを閉じて、元のタブに戻る"""
  driver.close()
  driver.switch_to.window(original_tab)

def get_data_houjin(driver:webdriver.Chrome,data_houdei:dict[str,str]) -> dict[str,str]:
  """
  法人名を抽出して引数の辞書に追加して返す
  
  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    data_houdei (dict[str,str]): 各施設情報を格納する辞書
    
  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    data_houdei (dict[str,str]): 引数data_houdeiに取得した法人名を追加した辞書 (例: {'法人名':'株式会社ぴあサポート'})
  """
  houjin = driver.find_element(By.XPATH,"//tr[td[text()='法人等の名称']]/td[2]")
  data_houdei['法人名']=houjin.text

def get_data_jigyousyo(driver:webdriver.Chrome,data_houdei:dict[str,str]) -> dict[str,str]:
  """
  事業所の名称、電話番号、メールアドレス、ホームページを抽出して引数の辞書に追加して返す

   Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    data_houdei (dict[str,str]): 各施設情報を格納する辞書
    
  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    data_houdei (dict[str,str]): 引数data_houdeiに取得した事業所情報を追加した辞書
    (例: {'法人名':'株式会社ぴあサポート','事業所名':'オリーブ','メール':'pia-olive@gui.ne.jp','電話':'072-275-9466','ホームページ':'http://www.pia-olive'})
  """
  jigyousyo_data_locator =(By.CLASS_NAME, 'content_employee')
  all_element(driver,jigyousyo_data_locator)

  jig_name=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の名称']]/td[2]")
  jig_tel=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電話番号']]/td[2]")
  jig_mail=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電子メールアドレス']]/td[2]")
  jig_url=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 ホームページ']]/td[2]")
  data_houdei['事業所名']=(jig_name.text)
  data_houdei['メール']=(jig_mail.text)
  data_houdei['電話']=(jig_tel.text)
  data_houdei['ホームページ']=(jig_url.text)

def select_service(driver:webdriver.Chrome) -> None:
  """サービス一覧から放課後等デイサービスを選択するブラウザ操作"""
  
  servece_locator =(By.ID,"service")
  wait_and_click(driver,servece_locator)

  #チェックボックスの要素を取得してクリック
  houkago_locator =(By.ID,"SRVC65")
  js_click(driver,houkago_locator)

  #画面が完全に切り替わるまで待機
  title =(By.ID,"selectedServices")
  text= "放課後等デイサービス"
  kirikae(driver,title,text)

def change_display_to_list(driver:webdriver.Chrome) -> bool:
  """
  表示形式を「一覧から選択」に変更するブラウザ操作

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    
  Returns: 
    bool : 処理成功でTrue、表示件数0件でFalse

  Note:
    施設の検索結果が0件の時は、itiran_locatorが見つからずTimeoutExceptionエラーが発生するため
    その場合はFalseを返してget_data()の条件分岐で処理を抜ける。
  """
  itiran_locator =(By.ID,'list')
  try:
    wait_and_click(driver,itiran_locator)  
  except TimeoutException :
    return False
  return True

def extract_data_from_page(driver:webdriver.Chrome,list_houdei:list[dict[str,str]]) -> list[dict[str,str]]:
  """
  施設一覧ページ1ページ分の施設情報をスクレイピングし、引数のリストに辞書形式で追加して返す

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    list_houdei (list[dict[str,str]]) : 各施設情報を格納する辞書のリスト

  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    list_houdei (list[dict[str,str]]) :引数list_houdeiに取得した情報を追加したリスト

  Note:
    
    -施設一覧ページのすべての施設が表示されるまで待機し、全施設リンク要素を取得
    -各施設リンクを新しいタブで開き、施設情報を取得
    -取得後は元のタブに戻り、各施設を順に読み込み
   
  """
  itiranElements =(By.XPATH,"//div[@class='detaillinkforeach']/a")
  itiranList =all_element(driver,itiranElements)
  
  for targetElement in itiranList:
    data_houdei ={} 
    
    #事業所の選択
    driver.execute_script("arguments[0].scrollIntoView(true);", targetElement)
    #新しいタブで開き切り替える
    original_tab =open_link_in_newtab(driver,targetElement)

    #法人名取得
    get_data_houjin(driver,data_houdei)
    #事業所情報ページへ移動
    jigyousyo_locator =(By.ID,'tab2_title')
    wait_and_click(driver,jigyousyo_locator)
    
    #事業所情報抽出
    get_data_jigyousyo(driver,data_houdei)

    list_houdei.append(data_houdei)
    to_originaltab(driver,original_tab)


def go_next_page(driver:webdriver.Chrome) -> None:
  """次のページへ移動"""
  nextpage_locator =(By.ID,'COP000101E22')
  wait_and_click(driver,nextpage_locator)

def get_data(driver:webdriver.Chrome) -> list[dict[str,str]]:
  """
  複数ページにまたがる施設情報をスクレイピングし、辞書形式のリストとしてまとめて返す

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト

  Returns:
    list_houdei (list[dict[str,str]]) : 各施設情報を格納した辞書のリスト
    ※施設情報が0件の場合は空のリストを返す。
     
  Note:
    -サービス一覧から放課後デイサービスを選択
    -表示形式を「一覧から選択」に変更※0件の場合スキップ
    -総ページ数を取得し、各ページを順に読み込み
    -ページが切り替わってから、施設情報を抽出
  """
  select_service(driver)
  if change_display_to_list(driver)==False:
     return []
  list_houdei =[]
  totalpage =int(driver.find_element(By.ID,'totalpage').text)
  for j in range(1,totalpage+1):
    pageElement =(By.ID,'currentpage')
    text2=str(j)
    kirikae(driver,pageElement,text2)
    extract_data_from_page(driver,list_houdei)
    if j<(totalpage) :
      go_next_page(driver)
  return list_houdei


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

#--- 例外処理地域リスト---
reigai={
  '北海道札幌市':["中央区","北区","東区","白石区","豊平区","南区","西区","厚別区","手稲区","清田区"],
  '宮城県仙台市':['青葉区', '宮城野区', '若林区', '太白区', '泉区'],
  '埼玉県さいたま市':["西区","北区","大宮区","見沼区","中央区","桜区","浦和区","南区","緑区","岩槻区"],
  '千葉県千葉市':["中央区","花見川区","稲毛区","若葉区","緑区","美浜区"],
  '神奈川県横浜市':['鶴見区', '神奈川区', '西区', '中区', '南区', '保土ケ谷区', '磯子区', '金沢区', '港北区', '戸塚区', '港南区', '旭区', '緑区', '瀬谷区', '栄区', '泉区', '青葉区', '都筑区'],
  '神奈川県川崎市':['川崎区', '幸区', '中原区', '高津区', '多摩区', '宮前区', '麻生区'],
  '神奈川県相模原市':['緑区', '中央区', '南区'],##横浜市の緑区が選択される※修正済み
  '新潟県新潟市':['北区', '東区', '中央区', '江南区', '秋葉区', '南区', '西区', '西蒲区'],
  '静岡県静岡市':['葵区', '駿河区', '清水区'],
  '静岡県浜松市':['中央区', '浜名区', '天竜区'],
  '愛知県名古屋市':['千種区', '東区', '北区', '西区', '中村区', '中区', '昭和区', '瑞穂区', '熱田区', '中川区', '港区', '南区', '守山区', '緑区', '名東区', '天白区'],
  '京都府京都市':['北区', '上京区', '左京区', '中京区', '東山区', '下京区', '南区', '右京区', '伏見区', '山科区', '西京区'],
  '大阪府大阪市': ['都島区', '福島区', '此花区', '西区', '港区', '大正区', '天王寺区', '浪速区', '西淀川区', '東淀川区', '東成区', '生野区', '旭区', '城東区', '阿倍野区', '住吉区', '東住吉区', '西成区', '淀川区', '鶴見区', '住之江区', '平野区', '北区', '中央区'],
  '大阪府堺市': ['堺区', '中区', '東区', '西区', '南区', '北区', '美原区'], #大阪市の西区が選択される※修正済み
  '兵庫県神戸市': ['東灘区', '灘区', '兵庫区', '長田区', '須磨区', '垂水区', '北区', '中央区', '西区'], 
  '広島県広島市': ['中区', '東区', '南区', '西区', '安佐南区', '安佐北区', '安芸区', '佐伯区'], 
  '岡山県岡山市': ['北区', '中区', '東区', '南区'], 
  '福岡県福岡市': ['東区', '博多区', '中央区', '南区', '西区', '城南区', '早良区'], 
  '福岡県北九州市': ['門司区', '若松区', '戸畑区', '小倉北区', '小倉南区', '八幡東区', '八幡西区'],
  '熊本県熊本市': ['中央区', '東区', '西区', '南区', '北区'], 
  
}
#--- 同じ県内で重複する区のリスト ---
tyouhuku=['神奈川県相模原市','大阪府堺市']

def select_tiiki_reigai_tyouhuku(driver:webdriver.Chrome,todou:str,siku:str,ku:str) -> None:
  """
  例外的なdom構造の地域を選択するブラウザ操作

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    todou (str) : 都道府県名
    siku (str) : 市町村名
    ku (str) : 区の名前

  Returns: None
  
  Note:
    通常、都道府県 → 市町村 を選択するが、

    一部政令指定都市などは、都道府県 → 区（市町村項目内）を選択する構造になっている。

    さらに、同一都道府県内に同名の区が複数存在する場合に単に区の名前で検索すると最初に見つかった方が選択されてしまう。
    そのため、市町村名:sikuと、区の名前:kuの両方でリンクを特定し選択する。
  """
  select_todou(driver,todou)
  siku_locator = (By.XPATH,f"//tr[th[text()='{siku}']]/following-sibling::tr/td/a[@title='{ku}']")
  siku_a =WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(siku_locator))
  siku_a.click()

def scrape_data(S:str,todou:str,siku:str) -> list[dict[str,str]]:
  """
  指定された地域に対してスクレイピングを実行し、辞書形式のリストとしてまとめて返す

  Parameters:
    S (str): ユーザーが入力した地域名
    todou (str) : 都道府県名
    siku (str) : 市町村名

  Returns: 
    list_houdei (list[dict[str,str]]) : 各施設情報を格納した辞書のリスト

  Note:
    通常、都道府県 → 市町村 を選択するが、

    例外A）一部政令指定都市などは、都道府県 → 区（市町村項目内）を選択する構造になっている。

    例外B）さらに、同一都道府県内に同名の区が複数存在する場合に単に区の名前で検索すると最初に見つかった方が選択されてしまう。
    そのため、市町村名:sikuと、区の名前:kuの両方でリンクを特定し選択する。

    例外A・Bの場合は、スクレイピング対象が多くseleniumの動作が安定稼働しないため、
    区ごとに都度ブラウザを起動・終了している。
  """
  list_houdei=[]
  if S in reigai:
    for ku in reigai[S]:
      driver =get_site()
      if S in tyouhuku:
        select_tiiki_reigai_tyouhuku(driver,todou,siku,ku)  
      else:
        select_todou(driver,todou)
        select_siku(driver,ku)

      ku_data = get_data(driver)
      list_houdei += ku_data
      driver.quit()
  else:
    driver =get_site()
    select_todou(driver,todou)
    select_siku(driver,siku)
    list_houdei = get_data(driver)
    driver.quit() 
  return list_houdei

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
  wb_path,sheet_name =create_excelsheet(row_path,siku)   
  write_to_excel(wb_path,df_houdei,sheet_name)

  print(df_houdei)
  print(f"\033[0m\033[32m\033[1m処理が正常に完了しました。\033[0m")

if __name__ == "__main__":
   main()