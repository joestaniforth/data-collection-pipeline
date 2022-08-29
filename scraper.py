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
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)

    def connect_cookies(self,):
        self.driver.get(self.url)
        time.sleep(random.randint(1,3))
        try:
            self.driver.switch_to.frame('fc-dialog-container') # This is the id of the frame
            accept_cookies_button = self.driver.find_elementh(by=By.XPATH, value="//button[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]")
            accept_cookies_button.click()
            time.sleep(1)
        except AttributeError:
            self.driver.switch_to_frame('fc-dialog-container') # This is the id of the frame
            accept_cookies_button = self.driver.find_elementh(by=By.XPATH, value="//button[contains(@class, 'fc-button fc-cta-consent fc-primary-button')]")
            accept_cookies_button.click()
            time.sleep(1)
        except:
            pass

    
