from scraper import dotaScraper
from unittest.mock import patch
import unittest

class TestScraper(unittest.TestCase):
    
    @patch(dotaScraper.driver.find_element)
    def test_cookies_case(self, mock_driver):
        dS = dotaScraper(url = 'https://www.dotabuff.com/')
        dS.connect_cookies()
        self.assertTrue(mock_driver.called)

    def test_get_heroes(self, mock_driver):
        dS = dotaScraper(url = 'https://www.dotabuff.com/')
        ds