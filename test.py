import os.path
import scraper
from unittest.mock import patch
import unittest

class TestScraper(unittest.TestCase):
    
    @patch('scraper.dotaScraper.connect_cookies')
    @patch('scraper.dotaScraper.get_heroes')
    def test_init(self,  mock_cookies, mock_heroes):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        self.assertTrue(mock_cookies.called)
        self.assertTrue(mock_heroes.called)
        self.assertTrue(os.path.isdir('raw_data'))


    def test_get_heroes(self):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        self.assertEqual(len(dS.hero_urls), 123)
        self.assertEqual

if __name__ == '__main__':
    unittest.main()