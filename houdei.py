###完成版
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

#--- 入力処理部分 ---
def get_user_input():
  S=input('地域を入力 例）東京都豊島区 ')
  row_path=input('excelファイルパスを入力').strip().replace('"','')
  return S,row_path

#--- 入力された文字を整形 ---
def format_input_data(S):
  try:
    match=re.search(r'北海道(.*)',S)
    match2=re.search(r'京都府(.*)',S)##都府両方入っていてエラーがでるため
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

#-- Excelシート準備 ---
def create_excelsheet(row_path,siku):
  try: 
    wb_path =Path(row_path)
    wb =openpyxl.load_workbook(wb_path)
    copy_sheet =wb.copy_worksheet(wb['テンプレート※コピーして名前を都市名に変更して使用'])
    copy_sheet.title =siku
    sheet_name = copy_sheet.title#シート名が重複した場合に対応例）豊島区、豊島区1
    wb.active=copy_sheet
    wb.save(wb_path)
    return wb_path,sheet_name
  except PermissionError:
    print('excelファイルを閉じてください。')
    sys.exit(1)

#---  サイトへ接続　---
def get_site():#サイトへ
  options = Options()
  options.add_experimental_option("detach", True)
  driver = webdriver.Chrome(options=options)
  driver.get("" \
  "https://www.wam.go.jp/sfkohyoout/COP000100E0000.do")
  return driver

#--- 地域を選択するブラウザ操作 ---
def select_todou(driver,todou):
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
  
  #市区町村
def select_siku(driver,siku):
  try:
    siku_locator = (By.XPATH,f"//a[@title='{siku}']")
    siku_a =WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(siku_locator))
    siku_a.click()
  except TimeoutException:
    print('市区町村名が正しくありません。')
    driver.close()
    sys.exit(1)

#--- クリック可能になるまで待機、要素を取得してクリック ---
def wait_and_click(driver,locator):
  element =WebDriverWait(driver,20).until(
    EC.element_to_be_clickable(locator)
  )
  element.click()

#--- 画面が完全に切り替わるまで待機 ---
def kirikae(driver,locator,text):
  WebDriverWait(driver,30).until(
    EC.text_to_be_present_in_element(locator,text)
  )

#--- すべての要素が表示されるまで待機 ---
def all_element(driver,locator):
  elements =WebDriverWait(driver,20).until(
        EC.visibility_of_all_elements_located(locator)
      )
  return elements

#--- jsでしか操作できない部分のクリック ---
def js_click(driver,locator):
  element =WebDriverWait(driver,30).until(
      EC.presence_of_element_located(locator)
  )
  driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });",element)
  driver.execute_script("arguments[0].click();",element)

#--- リンクを新しいタブで開き、そちらに切り替える ---
def open_link_in_newtab(driver,element):
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

#--- 現在のタブを閉じて、元のタブに戻る ---
def to_originaltab(driver,original_tab):
      driver.close()
      driver.switch_to.window(original_tab)

#--- 法人情報抽出 ---
def get_data_houjin(driver,data_houdei):
      houjin = driver.find_element(By.XPATH,"//tr[td[text()='法人等の名称']]/td[2]")
      data_houdei['法人名']=houjin.text

#--- 事業所情報抽出 ---
def get_data_jigyousyo(driver,data_houdei):
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

 #--- サービス一覧から放課後等デイサービスを選択 ---
def select_service(driver):
       #クリック可能な要素を取得してクリック
      servece_locator =(By.ID,"service")
      wait_and_click(driver,servece_locator)

      #チェックボックスの要素を取得してクリック
      houkago_locator =(By.ID,"SRVC65")
      js_click(driver,houkago_locator)

      #画面が完全に切り替わってから要素取得
      title =(By.ID,"selectedServices")
      text= "放課後等デイサービス"
      kirikae(driver,title,text)

#--- 表示方法を一覧から選択に変更 ---
def change_display_to_list(driver):
  itiran_locator =(By.ID,'list')
  try:#条件に一致する事業所が見つからない場合
    wait_and_click(driver,itiran_locator)  
  except TimeoutException :
    return False
  return True

#--- 各ページのデータ取得 ---
def extract_data_from_page(driver,list_houdei):
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

#--- 次のページへ移動 ---
def go_next_page(driver):
  nextpage_locator =(By.ID,'COP000101E22')
  wait_and_click(driver,nextpage_locator)


#--- 転記するデータを抽出する動作 ---
def get_data(driver):
  #サービス一覧から放課後等デイサービスを選択 
  select_service(driver)
  # 表示方法を一覧から選択に変更 
  if change_display_to_list(driver)==False:
     return
  #一覧ページから各事業所選択
  list_houdei =[]
  totalpage =int(driver.find_element(By.ID,'totalpage').text)
  for j in range(1,totalpage+1):
    #ページが完全に切り替わってから要素を取得
    pageElement =(By.ID,'currentpage')
    text2=str(j)
    kirikae(driver,pageElement,text2)
    #各ページのデータ取得
    extract_data_from_page(driver,list_houdei)
    #スクロールして次のページへ
    if j<(totalpage) :
      go_next_page(driver)
  return list_houdei


# #--- 転記するデータを抽出する動作 ---
# def get_data(driver):
# #--- サービスを選択欄で放課後デイサービスにチェックを入れるブラウザ操作 ---
#   #クリック可能な要素を取得してクリック
#   servece_locator =(By.ID,"service")
#   service =WebDriverWait(driver,20).until(
#       EC.element_to_be_clickable(servece_locator)
#   )
#   service.click()

#   #チェックボックスの要素を取得してクリック
#   houkago_locator =(By.ID,"SRVC65")
#   service1 =WebDriverWait(driver,30).until(
#       EC.presence_of_element_located(houkago_locator)
#   )
#   driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });",service1)##jsで直接dom操作しないと動かない
#   driver.execute_script("arguments[0].click();",service1)

#   #画面が完全に切り替わってから要素取得
#   title =(By.ID,"selectedServices")
#   WebDriverWait(driver,30).until(
#     EC.text_to_be_present_in_element(title,"放課後等デイサービス")
#   )
# #--- 表示方法を一覧から選択に変更 ---
#   itiran_locator =(By.ID,'list')
#   try:#条件に一致する事業所が見つからない場合
#     itiran=WebDriverWait(driver,20).until(
#       EC.element_to_be_clickable(itiran_locator)#wait_and_click()
#     )
#     itiran.click()
#   except TimeoutException :
#     return
  
#   #--- 一覧
#   list_houdei =[]
#   totalpage =int(driver.find_element(By.ID,'totalpage').text)
#   for j in range(1,totalpage+1):
#     #ページが完全に切り替わってから要素を取得
#     pageElement =(By.ID,'currentpage')
#     WebDriverWait(driver,30).until(
#       EC.text_to_be_present_in_element(pageElement,str(j))#kirikae
#     )
#     itiranElements =(By.XPATH,"//div[@class='detaillinkforeach']/a")
#     itiranList =WebDriverWait(driver,20).until(
#         EC.visibility_of_all_elements_located(itiranElements)
#       )
#     itiranlength =len(itiranList)
#     for i in range(itiranlength):
#       data_houdei ={} 
#       targetElement =itiranList[i]
#       WebDriverWait(driver,20).until(
#         EC.element_to_be_clickable(targetElement)#wait_and_click()
#       )
#       #前タブ情報取得
#       original_tab =driver.current_window_handle
#       initial_tabs =driver.window_handles
#       #urlを新しいタブで開く
#       driver.execute_script("window.open(arguments[0].href,'_blank');",targetElement)

#       #後タブを取得
#       current_tabs =driver.window_handles
#       #新しいタブの取得移動
#       set_initial_tabs = set(initial_tabs)
#       set_current_tabs = set(current_tabs)
#       new_set= set_current_tabs-set_initial_tabs
#       new_tab = new_set.pop()
#       driver.switch_to.window(new_tab)

#       #法人名取得
#       houjin = driver.find_element(By.XPATH,"//tr[td[text()='法人等の名称']]/td[2]")
#       data_houdei['法人名']=houjin.text
#       #事業所クリック
#       jigyousyo_locator =(By.ID,'tab2_title')
#       jigyousyo =WebDriverWait(driver,20).until(
#         EC.element_to_be_clickable(jigyousyo_locator)#wait_and_click()
#       )
#       jigyousyo.click()
#       #事業所情報抽出
#       WebDriverWait(driver, 10).until(
#           EC.visibility_of_all_elements_located((By.CLASS_NAME, 'content_employee'))
#       )

#       jig_name=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の名称']]/td[2]")
#       jig_tel=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電話番号']]/td[2]")
#       jig_mail=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電子メールアドレス']]/td[2]")
#       jig_url=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 ホームページ']]/td[2]")
#       data_houdei['事業所名']=(jig_name.text)
#       data_houdei['メール']=(jig_mail.text)
#       data_houdei['電話']=(jig_tel.text)
#       data_houdei['ホームページ']=(jig_url.text)
#       list_houdei.append(data_houdei)

#       #タブを閉じて、元のタブに戻る
#       driver.close()
#       driver.switch_to.window(original_tab)
#     #スクロールして次のページへ
#     if j<(totalpage) :
#       nextpage_locator =(By.ID,'COP000101E22')
#       nextpage =WebDriverWait(driver,20).until(
#         EC.element_to_be_clickable(nextpage_locator)#wait_and_click()
#       )
#       nextpage.click()
     
#   return list_houdei

#--- エクセル書き込み処理 ---
def  write_to_excel(wb_path,df_houdei,sheet_name):
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

tyouhuku=['神奈川県相模原市','大阪府堺市']

#--- 同じ県内で区の名前が重複している2番目の地域の処理 ---
def select_tiiki_reigai_tyouhuku(driver,todou,siku,ku):
  select_todou(driver,todou)
  siku_locator = (By.XPATH,f"//tr[th[text()='{siku}']]/following-sibling::tr/td/a[@title='{ku}']")
  siku_a =WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(siku_locator))
  siku_a.click()

#--- スクレイピング部分 ---
def scrape_data(S,todou,siku):
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

#--- 実行 ---
def main():
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