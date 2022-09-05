from json import dumps, load
from os import mkdir
from os.path import join, isdir
from requests import get
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from time import sleep
from uuid import uuid4

class dotaScraper:
    def __init__(self, url):
        self.url = url      
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(executable_path = r'D:\chromedriver.exe', options=self.chrome_options)
        self.driver.implicitly_wait(10)
        self.hero_urls = list()
        self.item_table_xpath = '//table[descendant::thead[descendant::tr[descendant::th[contains(text(), "Item")]]]]'
        self.connect_cookies()
        self.get_heroes()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}
        if isdir('raw_data'):
            pass
        else:
            mkdir('raw_data')
        
    def connect_cookies(self):
        self.driver.get(self.url)
        sleep(2)
        accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[1]")
        accept_cookies_button.click()
        sleep(1)

    def get_heroes(self):
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
        
    def scrape_hero_data(self, url):
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
            'ID': hero_name.upper(),
            'UUID': str(uuid4())
        }
        if isdir(join(f'raw_data\\{hero_name}')):
            pass
        else:
            mkdir(join(f'raw_data\\{hero_name}'))
        hero_json = dumps(hero_dict)
        with open(f'raw_data\\{hero_name}\\data.json', 'w') as file:
            file.write(hero_json) 
        
    def scrape_hero_image(self, hero_name, url):
        page = get(url, headers = self.headers)
        file_name = url.split('/')[-1]
        with open(f'raw_data\\{hero_name}\\{file_name}', 'wb') as f:
            f.write(page.content)

    def scrape_all_heroes(self):
        for hero in self.hero_urls:
            self.scrape_hero_data(hero)

    def scrape_all_hero_images(self):
        for hero in self.hero_urls:
            hero_name = hero.split('/')[-1]
            with open(f'raw_data\\{hero_name}\\data.json', 'r') as file:
                hero_values = load(file)
            image_url = hero_values['Portrait']
            self.scrape_hero_image(hero_name = hero_name, url = image_url)

if __name__ == '__main__':
    scraper = dotaScraper(url = 'https://www.dotabuff.com/')
    scraper.scrape_all_heroes()
    scraper.scrape_all_hero_images()