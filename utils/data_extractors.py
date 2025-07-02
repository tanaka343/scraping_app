from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.selenium_helpers import wait_until_visible,to_originaltab,open_link_in_newtab,wait_and_click,select_houkago_service,change_display_to_list,wait_for_transition,go_next_page,select_city_name,select_prefecture,select_tiiki_exception_locations_duplicate_name_locations


#--- 例外処理地域リスト---
exception_locations={
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
duplicate_name_locations=['神奈川県相模原市','大阪府堺市']



def extract_houjin_name(driver:webdriver.Chrome,facility_data:dict[str,str]) -> dict[str,str]:
  """
  法人名を抽出して引数の辞書に追加して返す
  
  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    facility_data (dict[str,str]): 各施設情報を格納する辞書
    
  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    facility_data (dict[str,str]): 引数facility_dataに取得した法人名を追加した辞書 (例: {'法人名':'株式会社ぴあサポート'})
  """
  houjin_name = driver.find_element(By.XPATH,"//tr[td[text()='法人等の名称']]/td[2]")
  facility_data['法人名']=houjin_name.text


def extract_jigyousho_info(driver:webdriver.Chrome,facility_data:dict[str,str]) -> dict[str,str]:
  """
  事業所の名称、電話番号、メールアドレス、ホームページを抽出して引数の辞書に追加して返す

   Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    facility_data (dict[str,str]): 各施設情報を格納する辞書
    
  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    facility_data (dict[str,str]): 引数facility_dataに取得した事業所情報を追加した辞書
    (例: {'法人名':'株式会社ぴあサポート','事業所名':'オリーブ','メール':'pia-olive@gui.ne.jp','電話':'072-275-9466','ホームページ':'http://www.pia-olive'})
  """
  jigyousyo_locator =(By.CLASS_NAME, 'content_employee')
  wait_until_visible(driver,jigyousyo_locator)

  jigyousyo_name=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の名称']]/td[2]")
  jigyousyo_phone=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電話番号']]/td[2]")
  jigyousyo_email=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 電子メールアドレス']]/td[2]")
  jigyousyo_website=driver.find_element(By.XPATH,"//tr[td/font[text()='事業所の連絡先 ホームページ']]/td[2]")
  facility_data['事業所名']=(jigyousyo_name.text)
  facility_data['メール']=(jigyousyo_email.text)
  facility_data['電話']=(jigyousyo_phone.text)
  facility_data['ホームページ']=(jigyousyo_website.text)


def collect_facility_data(driver:webdriver.Chrome,facility_data_list:list[dict[str,str]]) -> list[dict[str,str]]:
  """
  施設一覧ページ1ページ分の施設情報をスクレイピングし、引数のリストに辞書形式で追加して返す

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    facility_data_list (list[dict[str,str]]) : 各施設情報を格納する辞書のリスト

  Returns: ※この関数は辞書を更新するのみで戻り値はなし
    facility_data_list (list[dict[str,str]]) :引数facility_data_listに取得した情報を追加したリスト

  Note:
    
    -施設一覧ページのすべての施設が表示されるまで待機し、全施設リンク要素を取得
    -各施設リンクを新しいタブで開き、施設情報を取得
    -取得後は元のタブに戻り、各施設を順に読み込み
   
  """
  facility_links_locator =(By.XPATH,"//div[@class='detaillinkforeach']/a")
  facility_links =wait_until_visible(driver,facility_links_locator)
  
  for facility_link in facility_links:
    facility_data ={} 
    
    #施設リンクの選択
    driver.execute_script("arguments[0].scrollIntoView(true);", facility_link)
    #新しいタブで開き切り替える
    original_tab =open_link_in_newtab(driver,facility_link)

    #法人名取得
    extract_houjin_name(driver,facility_data)
    #事業所情報ページへ移動
    jigyousyo_locator =(By.ID,'tab2_title')
    wait_and_click(driver,jigyousyo_locator)
    
    #事業所情報取得
    extract_jigyousho_info(driver,facility_data)

    facility_data_list.append(facility_data)
    to_originaltab(driver,original_tab)


def collect_all_facility_data(driver:webdriver.Chrome) -> list[dict[str,str]]:
  """
  複数ページにまたがる施設情報をスクレイピングし、辞書形式のリストとしてまとめて返す

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト

  Returns:
    facility_data_list (list[dict[str,str]]) : 各施設情報を格納した辞書のリスト
    ※施設情報が0件の場合は空のリストを返す。
     
  Note:
    -サービス一覧から放課後デイサービスを選択
    -表示形式を「一覧から選択」に変更※0件の場合スキップ
    -総ページ数を取得し、各ページを順に読み込み
    -ページが切り替わってから、施設情報を抽出
  """
  select_houkago_service(driver)
  if change_display_to_list(driver)==False:
     return []
  facility_data_list =[]
  totalpage =int(driver.find_element(By.ID,'totalpage').text)
  for j in range(1,totalpage+1):
    pageElement =(By.ID,'currentpage')
    text2=str(j)
    wait_for_transition(driver,pageElement,text2)
    collect_facility_data(driver,facility_data_list)
    if j<(totalpage) :
      go_next_page(driver)
  return facility_data_list


def scrape_data(driver:webdriver.Chrome,input_location:str,prefecture:str,city_name:str) -> list[dict[str,str]]:
  """
  指定された地域に対してスクレイピングを実行し、辞書形式のリストとしてまとめて返す

  Parameters:
    driver (webdriver.Chrome): SeleniumのWebDriver.Chromeオブジェクト
    input_location (str): ユーザーが入力した地域名
    prefecture (str) : 都道府県名
    city_name (str) : 市町村名

  Returns: 
    facility_data_list (list[dict[str,str]]) : 各施設情報を格納した辞書のリスト

  Note:
    通常、都道府県 → 市町村 を選択するが、

    例外A）一部政令指定都市などは、都道府県 → 区（市町村項目内）を選択する構造になっている。

    例外B）さらに、同一都道府県内に同名の区が複数存在する場合に単に区の名前で検索すると最初に見つかった方が選択されてしまう。
    そのため、市町村名:city_nameと、区の名前:kuの両方でリンクを特定し選択する。

    例外A・Bの場合は、スクレイピング対象が多くseleniumの動作が安定稼働しないため、
    区ごとに都度ブラウザを起動・終了している。
  """
  facility_data_list=[]
  if input_location in exception_locations:
    for ku in exception_locations[input_location]:
      if input_location in duplicate_name_locations:
        select_tiiki_exception_locations_duplicate_name_locations(driver,prefecture,city_name,ku)  
      else:
        select_prefecture(driver,prefecture)
        select_city_name(driver,ku)

      ku_data = collect_all_facility_data(driver)
      facility_data_list += ku_data
      driver.quit()
  else:
    select_prefecture(driver,prefecture)
    select_city_name(driver,city_name)
    facility_data_list = collect_all_facility_data(driver)
    driver.quit() 
  return facility_data_list
