from datetime import datetime
from json import dumps, load
from os import mkdir
from os.path import join, isdir
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from uuid import uuid4
import boto3
import io

class dotaScraper:
    def __init__(self, url) -> None:
        self.url = url      
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path = r'D:\chromedriver.exe')
        #self.driver.implicitly_wait(10)
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
        self.hero_urls = list()
        self.hero_portrait_urls = list()
        self.item_table_xpath = '//table[descendant::thead[descendant::tr[descendant::th[contains(text(), "Item")]]]]'
        self.s3_client = boto3.client('s3')
        self.connect_cookies()
        self.get_heroes()  
        if not isdir('raw_data'):
            mkdir('raw_data')
        if not isdir('aws_stash'):
            mkdir('aws_stash')
        
    def connect_cookies(self) -> None:
        '''Connects to Dotabuff and accepts cookies'''
        self.driver.get(self.url)
        sleep(2)
        accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[1]")
        accept_cookies_button.click()
        sleep(1)

    def get_heroes(self) -> None:
        '''Gets the list of heroes from www.dotabuff.com\heroes, and saves the urls to these pages in self.get_heroes'''
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
        
    def scrape_hero_data(self, url) -> None:
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
        win_rate = win_rate_span.text
        hero_name = url.split('/')[-1]
        item_dict = dict()
        date_scraped = datetime.today().strftime("%Y-%m-%d")
        for i in range(1, 13):
            item_name = self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[2]').text
            item_dict.update({
               item_name:{
               'Matches Played': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[3]').text,
               'Matches Won': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[4]').text,
               'Win Rate': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[5]').text
               }
            })
        hero_dict = {
            'Hero Name': hero_name.capitalize(),
            'Win Rate':win_rate,
            'Portrait': hero_portrait,
            'Items': item_dict,
            'ID': f'{hero_name.upper()}' + '-' + f'{date_scraped}',
            'UUID': str(uuid4()),
            'Date Scraped': f'{date_scraped}'
        }
        self.hero_portrait_urls.append(hero_dict['Portrait'])
        return hero_name, hero_dict, date_scraped 
        
    def scrape_hero_image(self, hero_name) -> None:
        '''Scrapes the hero portrait of a hero
        
        Parameters
        ----------
        hero_name: name of the hero to scrape
        '''
        with open(f'raw_data\\{hero_name}\\data.json', 'r') as file:
            hero_values = load(file)
        image_url = hero_values['Portrait']
        page = get(image_url, headers = self.headers)
        file_name = image_url.split('/')[-1]
        with open(f'raw_data\\{hero_name}\\{file_name}', 'wb') as file:
            file.write(page.content)

    def scrape_all_heroes(self) -> None:
        '''Scrapes all heroes'''
        for hero in self.hero_urls:
            data = self.scrape_hero_data(hero)
            self.stash_data_local(hero_name = data[0], hero_dict = data[1])

    def scrape_all_heroes_to_s3(self) -> None:
        '''Scrapes all heroes'''
        for hero in self.hero_urls:
            data = self.scrape_hero_data(hero)
            self.stash_data_s3(data =  data)

    def scrape_all_hero_images(self) -> None:
        for hero in self.hero_urls:
            hero_name = hero.split('/')[-1]
            self.scrape_hero_image(hero_name = hero_name)

    def stash_data_local(self, hero_name, hero_dict) -> None:
        if isdir(join(f'raw_data\\{hero_name}')):
            pass
        else:
            mkdir(join(f'raw_data\\{hero_name}'))
        hero_json = dumps(hero_dict)
        with open(f'raw_data\\{hero_name}\\data.json', 'w') as file:
            file.write(hero_json) 

    def stash_data_s3(self, data) -> None:
        file_obj = io.BytesIO(dumps(data[1]).encode('utf-8'))
        self.s3_client.upload_fileobj(file_obj, 'jsscraperbucket', f'{data[0]}\\{data[0]}-{data[2]}_raw_data.json')


    def stash_image_s3(self, image_url) -> None:
        file_name = image_url.split('/')[-1]
        page = get(image_url, headers = self.headers)
        file_obj = io.BytesIO(page.content)
        self.s3_client.upload_fileobj(file_obj, 'jsscraperbucket', f'{file_name}')
        
    def scrape_images_to_s3(self):
        for url in self.hero_portrait_urls:
            self.stash_image_s3(image_url = url)

if __name__ == '__main__':
    scraper = dotaScraper(url = 'https://www.dotabuff.com/')
    scraper.stash_image_s3(image_url = 'https://www.dotabuff.com/assets/heroes/abaddon-01d9b9a7f55f569c4a81e7d5362a593a871673f91a08671ade83a0139071b47e.jpg')
    #scraper.scrape_all_heroes_to_s3()
    #scraper.scrape_all_heroes()
    #scraper.scrape_all_hero_images()