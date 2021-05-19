import pymongo
import requests
from bs4 import BeautifulSoup
import os
import time
import random

client = pymongo.MongoClient()
db = client['project']
collection = db['Itn']


userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'
headers ={
    'User-Agent':userAgent
}
ss = requests.session()
url = 'https://food.ltn.com.tw/category'
res = ss.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

#主類別
CategoryID = soup.select('h2[id="hook3"]')[0]('a')[0]['href']
CategoryName = soup.select('h2[id="hook3"]')[0]('a')[0].text

#子類別(菜系風格 全部)
SubCategorys = soup.select('ul.sortfood.kind')[0]('a') #sortfood.kind有好幾個 但只選第1個


for SubCategory in SubCategorys:
    SubCategoryName = SubCategory.text
    SubCategoryID = SubCategory['href'].split('/')[1]
    print(SubCategoryID)

    page = 1
    #每個風格的第一頁所有文章
    while True:
        Sub_url = 'https://food.ltn.com.tw/'+SubCategory['href']+ f'/{page}'
        Sub_res = ss.get(Sub_url, headers=headers)
        Sub_soup = BeautifulSoup(Sub_res.text, 'html.parser')

        Recipes = Sub_soup.select('div.recipelist.boxTitle.sort')[0]('a')
        for Recipe in Recipes:
            RecipeUrl = 'https://food.ltn.com.tw/'+ Recipe['href']
            # print(RecipeUrl)
            Recipe_res = ss.get(RecipeUrl, headers=headers)
            Recipe_soup = BeautifulSoup(Recipe_res.text, 'html.parser')

            ######(多道)
            try:

                if Recipe_soup.select('div.recipebox') == "":

                    RecipeID = RecipeUrl.split('/')[-1]
                    RecipeName = Recipe_soup.select('h1')[0].text
                    Author = Recipe_soup.select('span.author')[0].text.strip().split('／')[1]
                    print(RecipeName,Author)

                    # 介紹文：有時會放在P標籤的第一個或第2個或第3個位置，不固定
                    Introduction = Recipe_soup.select('div.text.cookbook.boxTitle')[0]('p')[0].text
                    for i, _ in enumerate(Recipe_soup.select('div.text.cookbook.boxTitle')[0]('p')):
                        if Introduction == "":
                            Introduction = Recipe_soup.select('div.text.cookbook.boxTitle')[0]('p')[i + 1].text
                    print(Introduction)

                    # dishName = Recipe_soup.select('h4')[0].text
                    # print(dishName)

                    # 食譜.食材：一篇文章裡可能會有不只一個食譜
                    for i, dishName in enumerate(Recipe_soup.select('h4')):
                        dishName = dishName.text
                        # print(dishName)
                        c = int(len(Recipe_soup.select('ul.material')) / len(Recipe_soup.select('h4')))  # 一道菜裡 材料分幾格
                        # print(c)
                        Ingredient = []
                        for a in range(c):
                            if i == 0:
                                dishs = Recipe_soup.select('ul.material')[a]
                            elif i == 1:
                                dishs = Recipe_soup.select('ul.material')[a + c]
                            elif i == 2:
                                dishs = Recipe_soup.select('ul.material')[a + (2 * c)]
                            # print(dishs)

                            eachStep = []
                            for x in dishs('li'):
                                eachStep.append(x.text)
                            # print(eachStep)

                            Ingredient.append({eachStep[0]: eachStep[1:]})
                            # print(Ingredient)

                        IngredientDict = {dishName: Ingredient}
                        print(IngredientDict)

                        # 步驟： 每天文章裡 可能不只一種食譜，每個食譜裡又有好幾個步驟
                        CookingSteps = []
                        Steps = Recipe_soup.select('div.step')
                        for Step in Steps[i]('p'):
                            CookingSteps.append(Step.text)
                        print(CookingSteps)

                        # 存圖片
                        folderName = f'Itn/{SubCategoryID}'
                        if not os.path.exists(folderName):
                            os.makedirs(folderName)

                        Imgs = Recipe_soup.select('span.ph_i')
                        try:
                            ImgUrl = Imgs[i]('img')[0]['src']
                            resImg = ss.get(ImgUrl, headers=headers)
                            imgContent = resImg.content

                            with open(folderName + '/' + RecipeID + str(i) + '.jpg', 'wb') as f:  # 寫入二進制
                                f.write(imgContent)
                        except IndexError:
                            pass

                        # ----將食譜轉換成JSON格式----
                        RecipeInformation = {
                            'Recipeid': RecipeID + str(i),  # 食譜ID
                            'CategoryName': CategoryName,  # 主類別名稱
                            'SubCategoryID': SubCategoryID,  # 子類別ID
                            'SubCategoryName': SubCategoryName,  # 子類別名稱
                            'RecipeName': RecipeName,  # 食譜標題名稱
                            'Introduction': Introduction,  # 食譜介紹
                            'Author': Author,  # 作者
                            'Ingredient': IngredientDict,  # 所需食材及各食材份量
                            'CookingSteps': CookingSteps,  # 烹飪方法
                            'RecipeURL': RecipeUrl
                        }
                        print(RecipeInformation)
                        collection.insert_one(RecipeInformation)
                        print('=========')

                        time.sleep(2)




                #######(一道)
                else:
                    RecipeID = RecipeUrl.split('/')[-1]
                    RecipeName = Recipe_soup.select('h1')[0].text
                    Author = Recipe_soup.select('span.author')[0].text.strip().split('／')[1]
                    print(RecipeName, Author)

                    # 介紹文：有時會放在P標籤的第一個或第2個位置
                    Introduction = Recipe_soup.select('div.text.cookbook.boxTitle')[0]('p')[0].text
                    if Introduction == "":
                        Introduction = Recipe_soup.select('div.text.cookbook.boxTitle')[0]('p')[1].text
                    print(Introduction)

                    # 食材：一篇文章裡可能會有不只一個分類
                    Ingredients = Recipe_soup.select('dl.recipe')
                    Ingredient = []
                    for x in Ingredients:
                        x = x.text.strip().split('\n')
                        # print(x)
                        # print('=========')
                        Ingredient.append({x[0]: x[1:]})

                    print(Ingredient)

                    # 步驟：
                    CookingSteps = []
                    for Steps in Recipe_soup.select('div.word'):
                        for Step in Steps('p'):
                            CookingSteps.append(Step.text)
                    print(CookingSteps)

                    # 存圖片
                    folderName = f'Itn/{SubCategoryID}'
                    if not os.path.exists(folderName):
                        os.makedirs(folderName)


                    try:
                        Imgs = Recipe_soup.select('a.image-popup-vertical-fit')
                        ImgUrl = Imgs[0]["href"]
                        resImg = ss.get(ImgUrl, headers=headers)
                        imgContent = resImg.content
                        with open(folderName + '/' + RecipeID + '.jpg', 'wb') as f:  # 寫入二進制
                            f.write(imgContent)


                    except IndexError:
                        pass


                    # ----將食譜轉換成JSON格式----
                    RecipeInformation = {
                        'Recipeid': RecipeID,  # 食譜ID
                        'CategoryName': CategoryName,  # 主類別名稱
                        'SubCategoryID': SubCategoryID,  # 子類別ID
                        'SubCategoryName': SubCategoryName,  # 子類別名稱
                        'RecipeName': RecipeName,  # 食譜標題名稱
                        'Introduction':Introduction, #食譜介紹
                        'Author': Author,  # 作者
                        'Ingredient': Ingredient,  # 所需食材及各食材份量
                        'CookingSteps': CookingSteps,  # 烹飪方法
                        'RecipeURL': RecipeUrl
                    }
                    print(RecipeInformation)
                    collection.insert_one(RecipeInformation)

                    print('============')
                    time.sleep(2)

            except:
                pass

        print('===========================================================================')
        print('now page: {}'.format(page))
        if len(Recipes) < 15:
            break
        else:
            page += 1
            try:
                Sub_url = 'https://food.ltn.com.tw/' + SubCategory['href'] + f'/{page}'
                Sub_res = ss.get(Sub_url, headers=headers)
                Sub_soup = BeautifulSoup(Sub_res.text, 'html.parser')
                Recipes = Sub_soup.select('div.recipelist.boxTitle.sort')[0]('a')
            except:
                break
    time.sleep(3)
    print('final page: {}'.format(page))

client.close()

