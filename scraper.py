from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random


class Scraper:
    def __init__(self, url):
        self.url = url      
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(executable_path = r'D:\chromedriver.exe', options=self.chrome_options)
        self.hero_urls = list()
        self.item_table_xpath = '//table[descendant::thead[descendant::tr[descendant::th[contains(text(), "Item")]]]]'

    def connect_cookies(self,):
        self.driver.get(self.url)
        time.sleep(random.randint(1,3))
        try:
            self.driver.switch_to.frame('fc-dialog-container')
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//button[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]")
            accept_cookies_button.click()
            time.sleep(1)
        except AttributeError:
            self.driver.switch_to_frame('fc-dialog-container')
            accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//button[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]")
            accept_cookies_button.click()
            time.sleep(1)
        except:
            pass
        
    def get_heroes(self):
        button = self.driver.find_element_by_xpath("/html/body/div[2]/div[1]/div[2]/div/nav/ul/li[4]/a")
        button.click()
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
        
    def retrieve_hero_stats(self, url):
        self.driver.get(url)
        try:
            win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "won"]]/span')
        except:
             win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "lost"]]/span')
        win_rate = win_rate_span.text
        hero_list = list()
        hero_name = url.split('/')[-1]
        #hero_list.append(hero_name)
        #hero_list.append(win_rate)
        #item_table = self.driver.find_element(by = By.XPATH, value = self.item_table_xpath)
        
        item_rows = self.driver.find_elements_by_xpath(self.item_table_xpath + '/tbody/tr')
        print(len(item_rows))
        values = list()
        
        for i in range(1, 13):
            values.append({
               'Item Name': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[2]').text,
               'Matches Played': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[3]').text,
               'Matches Won': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[4]').text,
               'Win Rate': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[5]').text
            })
        print(hero_name)
        print(values)
        #item_cols = len(self.driver.find_elements_by_xpath(self.item_table_xpath + '/tbody/tr[1]/td'))
        #print(hero_name, win_rate, item_rows, item_cols)
        #for r in range(1, 12):
        #    for c in range(2, 6):
        #        value = self.driver.find_element_by_xpath(self.item_table_xpath + f'/tbody/tr[{str(r)}]/td[{str(c)}]').text
        #        print(value)
        #pass
  
if __name__ == '__main__':
    scraper = Scraper(url = 'https://www.dotabuff.com/')
    scraper.connect_cookies()
    scraper.get_heroes()
    for hero in scraper.hero_urls:
        scraper.retrieve_hero_stats(hero)