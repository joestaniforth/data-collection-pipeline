from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time



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

    def connect_cookies(self):
        self.driver.get(self.url)
        time.sleep(2)
        accept_cookies_button = self.driver.find_element(by=By.XPATH, value="//html/body/div[4]/div[2]/div[1]/div[2]/div[2]/button[1]")
        accept_cookies_button.click()
        time.sleep(1)

    def get_heroes(self):
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
        
    def scrape(self, url):
        self.driver.get(url)
        try:
            win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "won"]]/span')
        except:
             win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "lost"]]/span')
        win_rate = win_rate_span.text
        hero_name = url.split('/')[-1]
        values = list()
        values.append({
            'Hero Name': f'{hero_name}',
            'Win Rate': f'{win_rate}'
        })
        for i in range(1, 13):
            values.append({
               'Item Name': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[2]').text,
               'Matches Played': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[3]').text,
               'Matches Won': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[4]').text,
               'Win Rate': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[5]').text
            })
        print(values)
  
if __name__ == '__main__':
    scraper = dotaScraper(url = 'https://www.dotabuff.com/')
    for hero in scraper.hero_urls:
        scraper.scrape(hero)