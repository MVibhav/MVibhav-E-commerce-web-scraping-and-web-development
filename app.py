from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import re
from datetime import datetime
import csv
import time
from flask import Flask, render_template, request, send_file, redirect, session

# from flask_session import Session

app = Flask(__name__)
# ses = Session()
begin_time = datetime.now()


@app.route('/')
def initial():
    return render_template('index.html')


@app.route('/home')
def home():
    website_name = request.args['id']
    display_website_name = website_name + ' Scraper'
    session['web_name'] = website_name
    if website_name == 'Green Roads':
        options = Options()
        ua = UserAgent()
        useragent = ua.random
        options.add_argument(f'user-agent={useragent}')
        options.add_argument("--window-size=1920,1080")
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://greenroadsworld.com/')
        driver.maximize_window()
        driver.find_element(By.CLASS_NAME, 'cookies-notification_button').click()
        try:
            driver.implicitly_wait(10)
            driver.find_element_by_id('bx-element-1329999-rjTUZdl').click()
        except:
            pass

        actions = ActionChains(driver)
        shop = driver.find_element_by_xpath('/html/body/div[4]/div[1]/header/div[1]/div/div[3]/nav/div/div[1]/span')
        driver.implicitly_wait(5)
        actions.move_to_element(shop).click(shop).perform()
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_names = bs.find_all('span', class_='nav-catalog_link-border', limit=8)

        product_categories = []

        for i in category_names:
            product_categories.append(i.text.strip())

        return render_template('index2.html', product_categories=product_categories,
                               display_website_name=display_website_name)

    elif website_name == 'Lazarus Naturals':
        options = Options()
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://www.lazarusnaturals.com/')

        actions = ActionChains(driver)
        shop = driver.find_element_by_xpath(
            '/html/body/div[2]/header/div/div[2]/div/div[1]/div/div/div/nav/ul[1]/li[1]/a/span[2]')
        actions.move_to_element(shop).perform()
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_names = bs.find_all('a', class_='ui-corner-all', limit=11)

        product_categories = []

        for i in category_names[2:]:
            product_categories.append(i.text.strip())

        return render_template('index2.html', product_categories=product_categories,
                               display_website_name=display_website_name)


    elif website_name == 'CBDfx':
        categories = []
        options = Options()
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://cbdfx.com/')
        for i in range(1, 8):
            str1 = 'cbd-'
            a = driver.find_element_by_xpath(
                '/html/body/div[1]/div[2]/div[1]/div/div/div/div/div/ul/li[' + str(i) + ']/a').text
            if (a == 'CAPSULES'):
                str1 = str1 + 'hemp-' + a.lower()
                print(str1)
                categories.append(str1)
                continue

            if (a == 'OIL TINCTURES'):
                str1 = str1 + a.lower()[4:-1]
                categories.append(str1)
                continue
            if (a == 'PETS'):
                str1 = str1 + 'for-' + a.lower()
                categories.append(str1)
                continue

            str1 = str1 + a.lower()
            categories.append(str1)

        return render_template('index2.html', product_categories=categories, display_website_name=display_website_name)

    elif website_name == 'CBDistillery':
        options = Options()
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://www.thecbdistillery.com/?hbt')
        driver.maximize_window()
        driver.implicitly_wait(20)
        try:
            driver.find_element_by_xpath('//*[@id="bx-element-1341733-EAhHBh6"]/button').click()
        except:
            pass
        try:
            driver.find_element_by_xpath('//*[@id="bx-element-1341734-UydskiE"]/button').click()
        except:
            pass

        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_names = bs.find_all('span', class_='navPages-label')[1:7]
        product_names = []
        split_names = []
        for i in category_names:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_names.append(j)

        for k in split_names:
            if k != '':
                product_names.append(k)

        return render_template('index2.html', product_categories=product_names,
                               display_website_name=display_website_name)

    elif website_name == 'Diamond CBD':
        PATH = "chromedriver.exe"
        categories = []
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(PATH)
        driver.get('https://www.diamondcbd.com/')
        driver.maximize_window()
        driver.find_element_by_xpath('//*[@id="block-diamondcbd-header"]/div/div[2]/div/div[1]/ul/li[1]/a').click()
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                        '/html/body/div[6]/div/div/div[2]/div[2]/main/section/div[1]/div/div/div/div[2]/div[1]/div/a'))).click()
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        lis = soup.find_all('span', 'facet-item__value')
        for i in range(12):
            category = lis[i].text
            if (category == 'CBD Bath & Body'):
                category = category.replace('& ', '')
            if (category == 'CBD Smokables'):
                category = category.replace('CBD ', '')
            if (category != 'Other' and category != 'CBD Vape Oil'):
                categories.append(category)
            driver.quit()
        return render_template('index2.html', product_categories=categories, display_website_name=display_website_name)


# -------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------

@app.route('/info', methods=['POST'])
def info():
    website_name = session.get('web_name', None)
    display_website_name = website_name + ' Scraper'

    if website_name == 'Green Roads':
        options = Options()
        ua = UserAgent()
        useragent = ua.random
        options.add_argument(f'user-agent={useragent}')
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        category_Name = request.form['dropdown']
        if category_Name == 'Sleep Line':
            driver.get('https://greenroads.com/collections/sleep-line/')

        elif category_Name == 'CBD Oils':
            driver.get('https://greenroads.com/collections/cbd-hemp-oil')

        elif category_Name == 'CBD Topicals':
            driver.get('https://greenroads.com/collections/cbd-topicals')

        elif category_Name == 'CBD Gummies':
            driver.get('https://greenroads.com/collections/cbd-edibles-gummies')

        elif category_Name == 'CBD Capsules & Softgels':
            driver.get('https://greenroads.com/collections/cbd-capsules')

        elif category_Name == 'CBD for Pets':
            driver.get('https://greenroads.com/collections/cbd-oil-pets')

        elif category_Name == 'CBD Chocolate & Coffee':
            driver.get('https://greenroads.com/collections/cbd-tea-cbd-coffee')

        elif category_Name == 'CBD Spa Collection':
            driver.get('https://greenroads.com/cbd-indulgence-line/')

        else:
            return '<h1>SELECT THE CORRECT OPTION</h1>'

        driver.maximize_window()

        driver.find_element(By.CLASS_NAME, 'cookies-notification_button').click()
        try:
            driver.implicitly_wait(10)
            driver.find_element_by_id('bx-element-1329999-rjTUZdl').click()
        except:
            pass

        bs = BeautifulSoup(driver.page_source, 'html.parser')
        Links = []
        links = bs.find_all('div', class_='products-card_title')
        for link in links:
            cc = link.find('a')['href']
            Links.append(cc)

        product_names = []  # CONTAINS NAMES OF THE PRODUCTS
        Price = []
        Rating = []
        Reviews = []
        Description = []

        def load_url(url):
            options = Options()
            ua = UserAgent()
            useragent = ua.random
            options.add_argument(f'user-agent={useragent}')
            options.headless = True
            driver = webdriver.Chrome('chromedriver.exe', options=options)
            driver.get(url)
            driver.maximize_window()
            driver.find_element(By.CLASS_NAME, 'cookies-notification_button').click()
            try:
                driver.implicitly_wait(10)
                driver.find_element_by_id('bx-element-1329999-rjTUZdl').click()
            except:
                pass

            bs = BeautifulSoup(driver.page_source, 'html.parser')
            name = bs.find('h1', class_='product-view_title')
            product_names.append(name.text.strip())
            price = bs.find('div', class_='products-prices_item')
            Price.append(price.text.strip())
            rating = bs.find('span', class_='sr-only')
            Rating.append(rating.text)
            review = bs.find('a', class_='text-m')
            Reviews.append(review.text)
            desc = bs.find('div', class_='bundle-description')
            Description.append(desc.text.strip())

        with ThreadPoolExecutor(max_workers=7) as executor:
            executor.map(load_url, Links)

        file_to_output = open('download.csv', mode='w', newline='')
        csv_writer = csv.writer(file_to_output, delimiter=',')
        w = 'NAME'
        x = 'PRICE'
        y1 = 'RATING'
        y = 'REVIEWS'
        z = 'DESCRIPTION'
        csv_writer.writerows([[w, x, y1, y, z]])
        for i in range(len(product_names)):
            csv_writer.writerows([[product_names[i], Price[i], Rating[i], Reviews[i], Description[i]]])

        return render_template('information.html', product_names=product_names, Price=Price, Rating=Rating,
                               Reviews=Reviews, Description=Description, display_website_name=display_website_name)

    elif website_name == 'Lazarus Naturals':
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://www.lazarusnaturals.com/')
        actions = ActionChains(driver)
        shop = driver.find_element_by_xpath(
            '/html/body/div[2]/header/div/div[2]/div/div[1]/div/div/div/nav/ul[1]/li[1]/a/span[2]')
        actions.move_to_element(shop).perform()

        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_names = bs.find_all('a', class_='ui-corner-all', limit=11)
        product_categories = []

        for i in category_names[2:]:
            product_categories.append(i.text.strip())

        category_Name = request.form['dropdown']
        index = product_categories.index(category_Name)
        shop_category = driver.find_element(By.XPATH,
                                            '/html/body/div[2]/header/div/div[2]/div/div[1]/div/div/div/nav/ul[1]/li[1]/ul/li[' + str(
                                                index + 2) + ']/a')
        actions.click(shop_category).perform()

        if True:
            bs = BeautifulSoup(driver.page_source, 'html.parser')
            Links = []
            links = bs.find_all('div', class_='product-item-info')
            for link in links:
                cc = link.find('a')['href']
                Links.append(cc)

            product_names = []  # CONTAINS NAMES OF THE PRODUCTS
            Price = []
            Rating = []
            Reviews = []
            Description = []

            def load_url(url):
                options = Options()
                options.headless = True
                driver = webdriver.Chrome('chromedriver.exe', options=options)
                driver.get(url)
                driver.maximize_window()
                bs = BeautifulSoup(driver.page_source, 'html.parser')

                w = []
                name = bs.find('h1', class_='h2-public')
                z = name.text.strip().split(" ")
                for i in z:
                    if i != '':
                        w.append(i)

                product_names.append(" ".join(w))

                bs = BeautifulSoup(driver.page_source, 'html.parser')
                price = bs.find('span', class_='price').text
                # price1 = bs.find('span', class_='max-price-class').text.strip()
                # final_price = price+" "+price1
                # Price.append(final_price)
                Price.append(price)

                bs = BeautifulSoup(driver.page_source, 'html.parser')
                try:
                    rating = bs.find('a', class_='action view')['aria-label']
                    Rating.append(re.findall('\d*\.?\d+', rating)[0])
                    review = bs.find('span', class_='reviews-actions')
                    Reviews.append(review.text.strip())
                except:
                    Rating.append(0)
                    Reviews.append(0)

                bs = BeautifulSoup(driver.page_source, 'html.parser')
                desc = bs.find('div', class_='product attribute overview').text.strip()
                if desc.startswith('<!'):
                    desc = bs.find('div', class_='product attribute overview').p.text.strip()

                Description.append(desc)

            # with ThreadPoolExecutor(max_workers=7) as executor:
            # 	executor.map(load_url, Links)

            for lii in Links:
                load_url(lii)

            file_to_output = open('download.csv', mode='w', newline='')
            csv_writer = csv.writer(file_to_output, delimiter=',')
            w = 'NAME'
            x = 'PRICE'
            y1 = 'RATING'
            y = 'REVIEWS'
            z = 'DESCRIPTION'
            csv_writer.writerows([[w, x, y1, y, z]])
            for i in range(len(product_names)):
                csv_writer.writerows([[product_names[i], Price[i], Rating[i], Reviews[i], Description[i]]])

            return render_template('information.html', product_names=product_names, Price=Price, Rating=Rating,
                                   Reviews=Reviews, Description=Description, display_website_name=display_website_name)

    elif website_name == 'CBDfx':
        category_Name = request.form['dropdown']
        items = []
        prices = []
        ratings = []
        reviews = []
        description = []
        options = Options()
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://cbdfx.com/collections/' + category_Name + '/')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        divs = soup.find_all('h2', 'woocommerce-loop-product__title')
        for i in divs:
            items.append(i.text)
        dollars = soup.find_all('span', 'price')
        for i in dollars:
            print(i)
            try:
                prices.append(i.ins.span.bdi.text)
            except:
                try:
                    prices.append(i.span.bdi.text)
                except:
                    prices.append(i.find('span', 'woocommerce-Price-amount amount').bdi.text)

        for i in range(1, len(items) + 1):
            try:
                ele = driver.find_element_by_xpath(
                    '/html/body/div[1]/div[2]/main/div[3]/div[2]/div[2]/div/ul/li[' + str(
                        i) + ']/div/div/div/div/div[2]')
                reviews.append(ele.text[1:-1] + ' reviews')
            except:
                reviews.append(None)

        stars = soup.find_all('div', 'bear-center')
        for i in stars:
            try:
                starno = i.div.get('aria-label')[6]
                ratings.append(starno)
            except:
                ratings.append(None)

        for i in range(1, len(items) + 1):
            try:
                el = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div/div/div/button/img')))
                el.click()
                elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                   '/html/body/div[1]/div[2]/main/div[3]/div[2]/div[2]/div/ul/li[' + str(
                                                                                       i) + ']/div/a[2]/h2')))
                driver.execute_script('arguments[0].click()', elem)
            except:
                elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                   '/html/body/div[1]/div[2]/main/div[3]/div[2]/div[2]/div/ul/li[' + str(
                                                                                       i) + ']/div/a[2]/h2')))
                driver.execute_script('arguments[0].click()', elem)
            try:
                var = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div[2]/main/div[3]/div/div/div[5]/div/div[2]/div[2]'))).text
                if (var == ''):
                    var = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div[1]/div[2]/main/div[3]/div/div/div[5]/div/div[1]/div[2]'))).text
                description.append(var)

            except:
                try:
                    var = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH,
                                                                                          '/html/body/div[1]/div[2]/main/div[3]/div/div/div[3]/div/div/div/div/div/div/div/div/div/div'))).text
                    description.append(var)
                except:
                    try:
                        var = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                            (By.XPATH, '/html/body/div[1]/div[2]/main/div[3]/div/div/div[3]/div'))).text
                        description.append(var)
                    except:
                        description.append(None)

            driver.back()

        file_to_output = open('download.csv', mode='w', newline='')
        csv_writer = csv.writer(file_to_output, delimiter=',')
        # u='SNO.'
        v = 'NAME'
        w = 'PRICE'
        x = 'REVIEWS'
        y = 'RATING'
        z = 'DESCRIPTION'
        csv_writer.writerows([[v, w, x, y, z]])
        for i in range(len(items)):
            csv_writer.writerows([[items[i], prices[i], reviews[i], ratings[i], description[i]]])

        driver.quit()
        return render_template('information.html', product_names=items, Price=prices, Rating=ratings, Reviews=reviews,
                               Description=description, display_website_name=display_website_name)

    elif website_name == 'CBDistillery':
        options = Options()
        options.add_argument("--window-size=1920,1080")
        options.headless = True
        driver = webdriver.Chrome('chromedriver.exe', options=options)
        driver.get('https://www.thecbdistillery.com/?hbt')
        driver.maximize_window()
        driver.implicitly_wait(20)
        try:
            driver.find_element_by_xpath('//*[@id="bx-element-1341733-EAhHBh6"]/button').click()
        except:
            pass
        try:
            driver.find_element_by_xpath('//*[@id="bx-element-1341734-UydskiE"]/button').click()
        except:
            pass

        shop_CBD = driver.find_element_by_xpath('//*[@id="menu"]/nav/ul[1]/li[1]/a/span')
        actions = ActionChains(driver)
        actions.move_to_element(shop_CBD).perform()
        bs = BeautifulSoup(driver.page_source, 'html.parser')

        categories = bs.find_all('span', class_='navPages-label')[1:7]
        product_categories = []
        split_product = []
        for i in categories:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_product.append(j)

        for k in split_product:
            if k != '':
                product_categories.append(k)

        category_Name = request.form['dropdown']
        index = product_categories.index(category_Name)
        shop_CBD_category = driver.find_element(By.XPATH,
                                                '//*[@id="navPages-shopCbd"]/ul/li[' + str(index + 1) + ']/a/span')
        actions.click(shop_CBD_category).perform()
        driver.implicitly_wait(20)
        try:
            driver.find_element_by_xpath('//*[@id="bx-element-1237652-H1IP6e1"]/button').click()
        except:
            pass

        names = []
        product_no_review = []
        product_price = []
        product_rating = []
        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_product_names = bs.find_all('h4', class_='card-title')
        split_product_names = []
        for i in category_product_names:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_product_names.append(j)

        for k in split_product_names:
            if k != '':
                names.append(k)

        bs = BeautifulSoup(driver.page_source, 'html.parser')
        category_price = bs.find_all('span', class_='price price--withoutTax')
        split_price = []
        for i in category_price:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_price.append(j)

        for k in split_price:
            if k != '':
                product_price.append(k)

        category_no_review = bs.find_all('a', class_='text-m')
        split_no_review = []
        for i in category_no_review:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_no_review.append(j)

        for k in split_no_review:
            if k != '':
                product_no_review.append(k)

        category_rating = bs.find_all('span', class_='sr-only')
        split_rating = []
        for i in category_rating:
            spiltting = i.text.split('\n')
            for j in spiltting:
                if '\n' not in j:
                    split_rating.append(j)

        for k in split_rating:
            if k != '':
                product_rating.append(k)

        Description = []

        for i in range(len(names)):
            Description.append("None")

        file_to_output = open('download.csv', mode='w', newline='')
        csv_writer = csv.writer(file_to_output, delimiter=',')
        v = 'NAME'
        w = 'PRICE'
        x = 'REVIEWS'
        y = 'Rating'
        for i in range(len(names)):
            csv_writer.writerows(
                [[names[i], product_price[i], product_no_review[i], product_rating[i], Description[i]]])

        return render_template('information.html', product_names=names, Price=product_price, Reviews=product_no_review,
                               Rating=product_rating, Description=Description,
                               display_website_name=display_website_name)

    elif website_name == 'Diamond CBD':
        category_Name = request.form['dropdown']
        PATH = "chromedriver.exe"
        items = []
        prices = []
        ratings = []
        reviews = []
        description = []
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(PATH)
        str1 = ''
        for i in category_Name:
            if i == ' ':
                str1 = str1 + '-'
            elif i.isupper(): \
                    str1 = str1 + i.lower()
            else:
                str1 = str1 + i
        driver.get('https://www.diamondcbd.com/collections/' + str1)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        divs = soup.find_all('div', 'small-6 large-4 xlarge-3 columns views-row')
        for div in divs:
            item = div.find('h4', class_='text-box-title').text[1:-1]
            price = div.find('div', class_='calculate-price').text
            rating = div.find('ul', class_='stars')
            review = div.find('a', class_='link')
            if (rating != None):
                rating = rating.get('data-vote-average-rounded')
            if (review != None):
                review = review.text[1:-1].strip()
            items.append(item)
            prices.append(price)
            ratings.append(rating)
            reviews.append(review)

    a1 = len(items)

    for item in range(len(items)):
        try:
            elem = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, items[item])))
            driver.execute_script('arguments[0].click()', elem)
        except:
            description.append(None)
            continue
        try:
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'Read more...')))
            element.click()
        except:
            description.append(None)
            driver.back()
            continue
        time.sleep(5)
        lement = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                             '#product-info > div.product-page__info > div.product-page__description > div.details > div')))
        var = lement.text
        var = var.replace('\n', '')
        description.append(var)
        driver.back()
    try:
        lement = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                             '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > nav > ul > li.pager__item.pager__item--next > a > i')))
        lement.click()
    except:
        file_to_output = open('download.csv', mode='w', newline='')
        csv_writer = csv.writer(file_to_output, delimiter=',')
        u = 'SNO.'
        v = 'NAME'
        w = 'PRICE'
        x = 'REVIEWS'
        y = 'Rating'
        z = 'DESCRIPTION'
        csv_writer.writerows([[u, v, w, x, y, z]])
        for i in range(0, len(items)):
            csv_writer.writerows([[i + 1, items[i], prices[i], reviews[i], ratings[i], description[i]]])
        driver.quit()
        return render_template('information.html', product_names=items, Price=prices, Reviews=reviews, Rating=ratings,
                               Description=description)
    while (True):
        driver.implicitly_wait(20)
        element = driver.find_element_by_css_selector(
            '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > div > div > div:nth-child(3)')
        count = 3
        html = element.get_attribute('innerHTML')
        soup2 = BeautifulSoup(html, 'html.parser')
        item = soup2.find('h4', class_='text-box-title').text[1:-1].strip()
        price = soup2.find('div', class_='calculate-price').text
        rating = soup2.find('ul', class_='stars')
        review = soup2.find('a', class_='link')
        if (rating != None):
            rating = rating.get('data-vote-average-rounded')
        if (review != None):
            review = review.text[1:-1]
        items.append(item)
        prices.append(price)
        ratings.append(rating)
        reviews.append(review)
        while (True):
            count = count + 1
            try:
                element2 = driver.find_element_by_css_selector(
                    '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > div > div > div:nth-child(' + str(
                        count) + ')')
                html = element2.get_attribute('innerHTML')
                soup2 = BeautifulSoup(html, 'html.parser')
                item = soup2.find('h4', class_='text-box-title').text[1:-1].strip()
                price = soup2.find('div', class_='calculate-price').text
                rating = soup2.find('ul', class_='stars')
                review = soup2.find('a', class_='link')
                if (rating != None):
                    rating = rating.get('data-vote-average-rounded')
                if (review != None):
                    review = review.text[1:-1].strip()
                items.append(item)
                prices.append(price)
                ratings.append(rating)
                reviews.append(review)
            except:
                break
        try:
            driver.find_element_by_css_selector(
                '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > nav > ul > li.pager__item.pager__item--next > a > i').click()
        except:
            try:
                driver.find_element_by_css_selector(
                    '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > div > div > nav > ul > li.pager__item.pager__item--next > a > i').click()
            except:
                break
    driver.find_element_by_css_selector(
        '#privy-inner-container > div.privy.privy-spin-to-win-container.privy-s2w-animate-in > div.privy-spin-to-win-content-wrap > div.privy-dismiss-content > img').click()
    for item in range(a1, len(items)):
        try:
            ele = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, items[item])))
            driver.execute_script('arguments[0].click()', ele)
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.LINK_TEXT, 'Read more...')))
            element.click()
            time.sleep(5)
            lement = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                                 '#product-info > div.product-page__info > div.product-page__description > div.details > div')))
            var = lement.text
            var = var.replace('\n', '')
            description.append(var)
            driver.back()
            driver.find_element_by_css_selector(
                '#block-dcbd-content > div.cpl-layout-blocks-main.cpl-shop-page-style-1 > div > div > div > section > div > div > div > div > nav > ul > li.pager__item.pager__item--next > a > i').click()
        except:
            description.append(None)
    # IMPORT CSV

    file_to_output = open('download.csv', mode='w', newline='')
    csv_writer = csv.writer(file_to_output, delimiter=',')
    u = 'SNO.'
    v = 'NAME'
    w = 'PRICE'
    x = 'REVIEWS'
    y = 'Rating'
    z = 'DESCRIPTION'
    csv_writer.writerows([[u, v, w, x, y, z]])
    for i in range(0, len(items)):
        csv_writer.writerows([[i + 1, items[i], prices[i], reviews[i], ratings[i], description[i]]])
    driver.quit()
    return render_template('information.html', product_names=items, Price=prices, Reviews=reviews,
                           Rating=ratings, Description=description, display_website_name=display_website_name)


@app.route('/download')
def download_csv():
    try:
        p = "download.csv"
        return send_file(p, as_attachment=True)

    except:
        return '<h1>Please reload and try again</h1>'


if __name__ == '__main__':
    app.secret_key = 'SECRET KEYY'
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)
    print(datetime.now() - begin_time)
