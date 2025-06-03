from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd

options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)
driver.get("" \
"https://www.wam.go.jp/sfkohyoout/COP000100E0000.do")

bottun = driver.find_element(By.ID,"pref13")
#地域の選択
actions =ActionChains(driver)
actions.scroll_to_element(bottun).perform()

actions.click(bottun).perform()
time.sleep(1)

tosimaku_locator = driver.find_element(By.ID,"town13116")
tosimaku =WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(tosimaku_locator))
actions.click(tosimaku).perform()

time.sleep(1)
#放課後デイサービス選択、一覧表示
servece_locator =(By.ID,"service")
service =WebDriverWait(driver,10).until(
    EC.element_to_be_clickable(servece_locator)
)
actions.click(service).perform()
time.sleep(1)

houkago_locator =(By.ID,"SRVC65")
service1 =WebDriverWait(driver,30).until(
    EC.presence_of_element_located(houkago_locator)
)

driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });",service1)
check =driver.find_element(By.CSS_SELECTOR,"#SRVC65")
actions.click(check).perform()
#一覧ページへ
itiran=driver.find_element(By.ID,'list')
driver.execute_script("arguments[0].scrollIntoView({block:'center'});",itiran)
actions.click(itiran).perform()

#一覧からurlまでスクロールここからループ
list_houdei =[]
totalpage =int(driver.find_element(By.ID,'totalpage').text)
for j in range(totalpage):
  itiranlength=len(driver.find_elements(By.XPATH,"//div[@class='detaillinkforeach']"))
  for i in range(itiranlength): 
    data_houdei ={}
    itiranList =driver.find_elements(By.XPATH,"//div[@class='detaillinkforeach']/a")
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});",itiranList[i])
    #前タブ情報取得
    original_tab =driver.current_window_handle
    initial_tabs =driver.window_handles
    #urlを新しいタブで開く
    driver.execute_script("window.open(arguments[0].href,'_blank');",itiranList[i])
    time.sleep(1)
    #後タブを取得
    current_tabs =driver.window_handles
    #新しいタブの取得移動
    set_initial_tabs = set(initial_tabs)
    set_current_tabs = set(current_tabs)
    new_set= set_current_tabs-set_initial_tabs
    new_tab = new_set.pop()
    driver.switch_to.window(new_tab)
    #beautifulsoupで情報取得
    html =driver.page_source#html取得
    soup =BeautifulSoup(html,'html.parser')
    houjin =soup.find_all('td',{'class':'tb04_td_up'})
    data_houdei['法人名']=(houjin[3].text)#法人名
    #事業所クリック
    jigyousyo =driver.find_element(By.ID,'tab2_title')
    driver.execute_script('arguments[0].scrollIntoView({block:"center"});',jigyousyo)
    jigyousyo.click()
    time.sleep(1)
    jig_name=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の名称']]/td[2]")
    jig_tel=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電話番号']]/td[2]")
    jig_mail=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電子メールアドレス']]/td[2]")
    jig_url=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 ホームページ']]/td[2]")
    data_houdei['事業所名']=(jig_name.text)
    data_houdei['メール']=(jig_mail.text)
    data_houdei['電話']=(jig_tel.text)
    data_houdei['ホームページ']=(jig_url.text)
    list_houdei.append(data_houdei)
    #タブを閉じて、元のタブに戻る
    driver.close()
    driver.switch_to.window(original_tab)
  df_houdei = pd.DataFrame(list_houdei)
  #スクロールして次のページへ
  if j<(totalpage-1) :
    nextpage=driver.find_element(By.ID,'COP000101E22')
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});",nextpage)
    nextpage.click()
    time.sleep(1)

print(df_houdei)
# actions.key_down(Keys.CONTROL).perform()
# actions.click(list1[2]).perform()
# driver.execute_script("window.open", list1[2])
# actions.key_up(Keys.CONTROL).perform()
