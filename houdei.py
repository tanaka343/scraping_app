###完成版仮
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import openpyxl
import re
from selenium.common.exceptions import TimeoutException
import sys 
from pathlib import Path
#入力部分
S=input('地域を入力 例）東京都豊島区 ')
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
except ValueError:
    print('入力形式が正しくありません。')
    sys.exit(1)
#Excelテンプレートシートをコピーしてシート名を変更
try:
  row_path=input('excelファイルパスを入力').strip().replace('"','')
  wb_path=Path(row_path)
  wb=openpyxl.load_workbook(wb_path)
  copy_sheet=wb.copy_worksheet(wb['テンプレート※コピーして名前を都市名に変更して使用'])
  copy_sheet.title=siku
  sheet_name =copy_sheet.title#シート名が重複した場合に対応例）豊島区、豊島区1
  wb.active=copy_sheet
  wb.save(wb_path)
except PermissionError:
  print('excelファイルを閉じてください。')
  sys.exit(1)

def get_site():#サイトへ
  options = Options()
  options.add_experimental_option("detach", True)
  driver = webdriver.Chrome(options=options)
  driver.get("" \
  "https://www.wam.go.jp/sfkohyoout/COP000100E0000.do")
  return driver

def select_tikiki(driver,todou,siku):
  #都道府県の選択
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
  try:
    siku_locator = (By.XPATH,f"//a[@title='{siku}']")
    siku_a =WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(siku_locator))
    siku_a.click()
  except TimeoutException:
    print('市区町村名が正しくありません。')
    driver.close()
    sys.exit(1)
def get_data(driver):
  #サービスを選択
  servece_locator =(By.ID,"service")
  service =WebDriverWait(driver,20).until(
      EC.element_to_be_clickable(servece_locator)
  )
  service.click()

  # 放課後デイサービスを選択##
  houkago_locator =(By.ID,"SRVC65")
  service1 =WebDriverWait(driver,30).until(
      EC.presence_of_element_located(houkago_locator)
  )
  driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });",service1)##jsで直接dom操作しないと動かない
  driver.execute_script("arguments[0].click();",service1)
  #画面が完全に切り替わってから要素取得
  title =(By.ID,"selectedServices")
  WebDriverWait(driver,30).until(
    EC.text_to_be_present_in_element(title,"放課後等デイサービス")
  )
  #一覧ページへ
  itiran_locator =(By.ID,'list')
  try:#条件に一致する事業所が見つからない場合
    itiran=WebDriverWait(driver,20).until(
      EC.element_to_be_clickable(itiran_locator)
    )
    itiran.click()
  except TimeoutException :
    return
  #一覧からurlまでスクロールここからループ
  list_houdei =[]
  db_houdei=[]
  totalpage =int(driver.find_element(By.ID,'totalpage').text)
  for j in range(1,totalpage+1):
    #ページが完全に切り替わってから要素を取得
    pageElement =(By.ID,'currentpage')
    WebDriverWait(driver,30).until(
      EC.text_to_be_present_in_element(pageElement,str(j))
    )
    itiranElements =(By.XPATH,"//div[@class='detaillinkforeach']/a")
    itiranList =WebDriverWait(driver,20).until(
        EC.visibility_of_all_elements_located(itiranElements)
      )
    itiranlength =len(itiranList)
    for i in range(itiranlength):
      data_houdei ={} 
      targetElement =itiranList[i]
      WebDriverWait(driver,20).until(
        EC.element_to_be_clickable(targetElement)
      )
      #前タブ情報取得
      original_tab =driver.current_window_handle
      initial_tabs =driver.window_handles
      #urlを新しいタブで開く
      driver.execute_script("window.open(arguments[0].href,'_blank');",targetElement)

      #後タブを取得
      current_tabs =driver.window_handles
      #新しいタブの取得移動
      set_initial_tabs = set(initial_tabs)
      set_current_tabs = set(current_tabs)
      new_set= set_current_tabs-set_initial_tabs
      new_tab = new_set.pop()
      driver.switch_to.window(new_tab)

      #法人名取得
      houjin = driver.find_element(By.XPATH,"//tr[td[text()='法人等の名称']]/td[2]")
      data_houdei['法人名']=houjin.text
      #事業所クリック
      jigyousyo_locator =(By.ID,'tab2_title')
      jigyousyo =WebDriverWait(driver,20).until(
        EC.element_to_be_clickable(jigyousyo_locator)
      )
      jigyousyo.click()
      #事業所情報抽出
      WebDriverWait(driver, 10).until(
          EC.visibility_of_all_elements_located((By.CLASS_NAME, 'content_employee'))
      )

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
    #スクロールして次のページへ
    if j<(totalpage) :
      nextpage_locator =(By.ID,'COP000101E22')
      nextpage =WebDriverWait(driver,20).until(
        EC.element_to_be_clickable(nextpage_locator)
      )
      nextpage.click()
     
  return list_houdei
##入力：例外処理地域リスト
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

if S in reigai:
  list_houdei=[]
  for i in reigai[S]:
    siku=i
    driver =get_site()
    if S=='神奈川県相模原市':
      todou_locator = (By.XPATH,f"//a[text()='{todou}']")
      todou_a =WebDriverWait(driver,10).until(
      EC.element_to_be_clickable(todou_locator)
      )
      todou_a.click()
      
      siku_locator = (By.XPATH,f"//tr[th[text()='相模原市']]/following-sibling::tr/td/a[@title='{i}']")
      siku_a =WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(siku_locator))
      siku_a.click()
    elif S=='大阪府堺市':
      todou_locator = (By.XPATH,f"//a[text()='{todou}']")
      todou_a =WebDriverWait(driver,10).until(
      EC.element_to_be_clickable(todou_locator)
      )
      todou_a.click()
      
      siku_locator = (By.XPATH,f"//tr[th[text()='堺市']]/following-sibling::tr/td/a[@title='{i}']")
      siku_a =WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(siku_locator))
      siku_a.click()
      
    else:
      select_tikiki(driver,todou,siku)
    ku_data = get_data(driver)
    list_houdei += ku_data
    driver.quit()
else:
  driver =get_site()
  select_tikiki(driver,todou,siku)
  list_houdei = get_data(driver)
  driver.quit()

df_houdei = pd.DataFrame(list_houdei) 
    

#エクセルに転記
with pd.ExcelWriter(wb_path,engine="openpyxl",mode="a",if_sheet_exists="overlay") as writer:
  df_houdei.to_excel(writer,sheet_name=sheet_name,startrow=1,startcol=0,header=False,index=False)


print(df_houdei)
print(f"\033[0m\033[32m\033[1m処理が正常に完了しました。\033[0m")