from selenium.webdriver import Chrome
import os
from urllib import request
import time

names = ['茄子','青江菜','紅蘿蔔','番茄','四季豆']

for name in names:
    driver = Chrome('./chromedriver')
    url ='https://www.shutterstock.com/zh-Hant/'
    driver.get(url)

    driver.find_element_by_tag_name('input').send_keys(name)
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="content"]/div[2]/div/div[1]/div/form/div/div/div/div[1]/button').click()
    time.sleep(6)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].outerHTML")

    #取得圖片網址
    picsURL = []
    a = html.split('<script type="application/ld+json" data-react-helmet="true">')[1].split('</script>')[0].split('{')
    for i in a[1:]:
        # print(i.split('","url')[0][1:].split(':"')[-1])
        picsURL.append(i.split('","url')[0][1:].split(':"')[-1])
    print(picsURL)


    #圖片存檔
    imgFolder = f'蔬菜圖片/{name}/'
    if not os.path.exists(imgFolder):
        os.makedirs(imgFolder)

    for i, picURL in enumerate(picsURL):
        url = picURL
        imgPath = imgFolder + f'{i}' + '.jpg'
        request.urlretrieve(url, imgPath)

    driver.close()