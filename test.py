from scraper import dotaScraper
from unittest.mock import patch
import unittest

class TestScraper(unittest.TestCase):
    
    @patch(dotaScraper.driver.find_element)
    def test_init(self, mock_driver, mock_cookies, mock_heroes):
        dS = dotaScraper(url = 'https://www.dotabuff.com/')
        self.assertTrue(mock_driver.called)
        self.assertTrue(mock_cookies.called)
        self.assertTrue(mock_heroes.called)

