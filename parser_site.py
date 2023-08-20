import json
import requests
import datetime
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

def get_list_category_urls():
    list_category_urls = []
    for i in range(1, 110):
        url = f'http://stelmeb.com/produktsiya/category/view/{i}'
        response = requests.get(url)
        if response.url != 'http://stelmeb.com/error-404' and response.url != 'https://paksmet.ru/produktsiya':
            list_category_urls.append(url)
        else:
            print(f'Такой страницы нет: {url}')
    return list(list_category_urls)

# Считваем все ссылки на категории и добовляем их в JSON файл
list_category_urls = get_list_category_urls()
with open('list_category_urls_stelmeb.json', 'w', encoding='utf-8') as f:
    json.dump(list_category_urls, f, ensure_ascii=False)

def get_all_link_product(list_urls):    
    list_all_links_product = []
    for url in list_urls:
        print(f'Собираю страницы товаров для категории: {url}')
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        main_soup = BeautifulSoup(driver.page_source, 'lxml')
        all_products = main_soup.find_all(class_= 'block_product')
        if all_products:
            for product in all_products:
                block_product_name = product.find('div', class_='name list_product_nam')
                link_product = block_product_name.find('a')['href']
                full_link_product = 'http://stelmeb.com'+link_product
                list_all_links_product.append(full_link_product)
                print(full_link_product)
        else:
            continue
    print(f'Всего страниц товаров {len(list_all_links_product)}')
    return list_all_links_product

# Открываем JSON со всеми категориями и сохраням все ссылки на товары в другой JSON
with open('list_category_urls_stelmeb.json') as json_file:
    list_category_urls_stelmeb = json.load(json_file)
list_all_urls_product = get_all_link_product(list_category_urls_stelmeb)
with open('list_all_urls_product_stelmeb.json', 'w', encoding='utf-8') as f:
    json.dump(list_all_urls_product, f, ensure_ascii=False)

def open_product_page(url, wait_time):
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
    except TimeoutException:
        print(f'Превышено время ожидания ответа страницы: {url}\nЗапрос будет отправлен повторно через 5 минут.')
        driver.quit()
        sleep(wait_time)
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        return driver
    return driver

def get_all_info_product(list_all_urls_product):
    start_time = datetime.datetime.now()
    print(f'Начало работы: {start_time}')
    data_products = []
    quantity_url = len(list_all_urls_product)
    count = quantity_url
    print(f'Всего {count} товаров.')
    for url in list_all_urls_product:
        print(f'Сейчас работаю со стринцей: {url}')
        driver = open_product_page(url, 300)
        main_soup = BeautifulSoup(driver.page_source, 'lxml')   
        about_product = main_soup.find_all(class_= 'row-fluid jshop')
        if about_product:
            for element in about_product:
                info_product = element.find('div', class_='span9 jshop_img_description')
                name_product = info_product.find('h1').text
                dis_product = info_product.find('div', class_='jshop_prod_description')
                if dis_product.find('p'):
                    discription_product = dis_product.find('p').text
                else:
                    discription_product = ''
                block_images = element.find('div', class_='span3 image_middle')
                link_image = block_images.find_all('a')
                list_links_images = []
                for link in link_image:
                    new_link = link['href']
                    list_links_images.append(new_link)
                products_vars = info_product.find_all('div', class_='product-var')
                list_price_and_size = []
                for product in products_vars:
                    price_and_size = product.find('div', class_='product-var-left')
                    if price_and_size.find('b', class_='product-subtitle'):
                        name_size = price_and_size.find('b', class_='product-subtitle').text
                    else:
                        name_size = ''
                    if price_and_size.find('p', class_='product-size'):
                        size = price_and_size.find('p', class_='product-size').text
                    else:
                        size = ''
                    if price_and_size.find('p', class_='product-price'):
                        price = price_and_size.find('p', class_='product-price').text
                    else:
                        price = ''
                    list_price_and_size.append({
                        'НазваниеРазмера': name_size,
                        'Размер': size,
                        'Цена': price
                    })
                data_products.append({
                    'СсылкаНаТовар': url,
                    'Название': name_product,
                    'Описание': discription_product,
                    'Картинки': list_links_images,
                    'РазмерЦена': list_price_and_size
                })
            count -= 1
            print(f'Осталось {count} товаров.')
    end_time = datetime.datetime.now()
    print(f'Время окончания работы: {end_time}')
    return data_products

# Открываем JSON со всеми ссылками на товары и записываем данные о товарах в другой JSON
with open('list_all_urls_product_stelmeb.json') as json_file:
    list_all_urls_product_stelmeb = json.load(json_file)
final_data_list = get_all_info_product(list_all_urls_product_stelmeb)
with open('data_products.json', 'w', encoding='utf-8') as f:
    json.dump(final_data_list, f, ensure_ascii=False)





