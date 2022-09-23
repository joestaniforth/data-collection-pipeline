from datetime import datetime, timedelta, date
from json import dumps, load
from os import mkdir
from os.path import join, isdir
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from uuid import uuid4
from warnings import warn
import boto3
import io

class dotaScraper:
    def __init__(self, url, id_list) -> None:
        self.url = url      
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path = r'D:\chromedriver.exe')
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
        self.hero_urls = list()
        self.hero_portrait_urls = dict()
        self.item_table_xpath = '//table[descendant::thead[descendant::tr[descendant::th[contains(text(), "Item")]]]]'
        self.s3_client = boto3.client('s3')
        self.connect_cookies()
        self.get_heroes()
        self.id_list = id_list
        if not isdir('raw_data'):
            mkdir('raw_data')
        
    def connect_cookies(self) -> None:
        '''Connects to Dotabuff and accepts cookies'''
        self.driver.get(self.url)
        sleep(2)
        accept_cookies_button = self.driver.find_element(
            by=By.XPATH,
            value="//html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[1]")
        accept_cookies_button.click()
        sleep(1)

    def get_heroes(self) -> None:
        '''Gets the list of heroes from www.dotabuff.com\heroes, and saves the urls to these pages in self.get_heroes'''
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
        
    def scrape_hero_data(self, hero_name, id, url) -> tuple:
        '''Scrapes the data for one hero and saves the result to /raw_data/hero_name/data.json
        
        Parameters
        ----------
        url: url to a hero on dotabuff in the format www.dotabuff.com/heroes/<hero_name>
        '''
        self.driver.get(url)
        try:
            win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "won"]]/span')
        except:
             win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "lost"]]/span')
        hero_portrait = self.driver.find_element(by = By.XPATH, value = '//img[@class = "image-avatar image-hero"]')
        hero_portrait = hero_portrait.get_attribute('src')
        win_rate = win_rate_span.text.replace('%','')
        item_dict = dict()
        date_scraped = datetime.today().strftime("%Y-%m-%d")
        for i in range(1, 13):
            item_name = self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[2]').text.replace("'","")
            item_dict.update({
               item_name: {
               'Matches Played': int(self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[3]').text.replace(",","")),
               'Matches Won': int(self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[4]').text.replace(",","")),
               'Win Rate': float(self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[5]').text.replace(",","").replace('%',''))/100
               }
            })
        hero_dict = {
            'Hero Name': hero_name,
            'Win Rate': float(win_rate)/100,
            'Portrait': hero_portrait,
            'Items': item_dict,
            'ID': f'{id}',
            'UUID': str(uuid4()),
            'Date Scraped': f'{date_scraped}'
        }
        self.hero_portrait_urls.update({hero_dict['Hero Name'] : hero_dict['Portrait']})
        return hero_name, hero_dict, date_scraped 
        
    def scrape_hero_image(self, url, hero_name) -> None:
        '''Scrapes the hero portrait of a hero
        
        Parameters
        ----------
        url: url of image to scrape
        hero_name: name of hero to scrape
        '''
        page = get(url, headers = self.headers)
        file_name = url.split('/')[-1]
        with open(f'raw_data\\{hero_name}\\{file_name}', 'wb') as file:
            file.write(page.content)

    def scrape_all_heroes(self, id_list: list) -> None:
        '''Scrapes all heroes'''
        for url in self.hero_urls:
            hero_name = url.split('/')[-1]
            id_string = self.generate_id(hero_name)
            if id_string not in id_list:
                data = self.scrape_hero_data(hero_name = hero_name, url = url, id = id_string)
            self.stash_data_local(data = data)
        pass

    def scrape_all_heroes_to_s3(self) -> None:
        '''Scrapes all heroes'''
        for hero in self.hero_urls:
            data = self.scrape_hero_data(hero)
            self.stash_data_s3(data =  data)

    def scrape_all_hero_images(self) -> None:
        for key in self.hero_portrait_urls:
            self.scrape_hero_image(url = self.hero_portrait_urls[key], hero_name = key)

    def stash_data_local(self, data) -> None:
        hero_name = data[0]
        if isdir(join(f'raw_data\\{hero_name}')):
            pass
        else:
            mkdir(join(f'raw_data\\{hero_name}'))
        hero_json = dumps(data[1])
        with open(f'raw_data\\{hero_name}\\{data[0]}-{data[2]}.json', 'w') as file:
            file.write(hero_json) 

    def stash_data_s3(self, data) -> None:
        file_obj = io.BytesIO(dumps(data[1]).encode('utf-8'))
        if f'{data[0]}/' not in self.s3_client.list_objects(Bucket = 'jsscraperbucket'):
            self.s3_client.put_object(Bucket = 'jsscraperbucket', Key = f'{data[0]}/', Body = b'')
        response = self.s3_client.upload_fileobj(file_obj, 'jsscraperbucket', f'{data[0]}/{data[0]}-{data[2]}_raw_data.json')
        return response

    def stash_image_s3(self, image_url, hero) -> None:
        file_name = image_url.split('/')[-1]
        page = get(image_url, headers = self.headers)
        file_obj = io.BytesIO(page.content)
        response = self.s3_client.upload_fileobj(file_obj, 'jsscraperbucket', f'{hero}/{file_name}')
        return response
        
    def scrape_images_to_s3(self):
        if len(self.hero_portrait_urls) == 0:
            warn('No URLS to scrape for images, please scrape hero data first')
        for key in self.hero_portrait_urls:
            self.stash_image_s3(hero = key, image_url = self.hero_portrait_urls[key])
    
    def get_week_begin(self):
        today = date.today()
        date_begin = today - timedelta(days = today.weekday())
        return date_begin.strftime("%Y-%m-%d")

    def generate_id(self, hero:str) -> str:
        week_beginning = self.get_week_begin()
        id_string = f'{hero.upper()}' + '-' + f'{week_beginning}'
        return id_string

if __name__ == '__main__':
    id_list = list()
    scraper = dotaScraper(url = 'https://www.dotabuff.com/', id_list = id_list)
    scraper.scrape_all_heroes()
    scraper.scrape_all_hero_images()