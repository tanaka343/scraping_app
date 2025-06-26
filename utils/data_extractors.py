from selenium import webdriver
from selenium.webdriver.common.by import By
from utils.selenium_helpers import all_element,to_originaltab,open_link_in_newtab,wait_and_click,select_service,change_display_to_list,kirikae,go_next_page,select_siku,select_todou,select_tiiki_reigai_tyouhuku,get_site

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
