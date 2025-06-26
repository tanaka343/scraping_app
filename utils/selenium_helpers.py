from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sys 
from selenium.webdriver.remote.webelement import WebElement


def get_site() -> webdriver.Chrome:
  """chromeドライバーを開き対象ページを開く"""
  options = Options()
  options.add_experimental_option("detach", True)
  driver = webdriver.Chrome(options=options)
  driver.get("" \
  "https://www.wam.go.jp/sfkohyoout/COP000100E0000.do")
  return driver

def wait_and_click(driver:webdriver.Chrome,locator:str) -> None:
  """クリック可能になるまで待機、要素を取得してクリック"""
  element =WebDriverWait(driver,20).until(
    EC.element_to_be_clickable(locator)
  )
  element.click()

def all_element(driver:webdriver.Chrome,locator:tuple[str,str]) -> list[WebElement]:
  """すべての要素が表示されるまで待機して要素を取得"""
  elements =WebDriverWait(driver,20).until(
        EC.visibility_of_all_elements_located(locator)
      )
  return elements

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

def go_next_page(driver:webdriver.Chrome) -> None:
  """次のページへ移動"""
  nextpage_locator =(By.ID,'COP000101E22')
  wait_and_click(driver,nextpage_locator)

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