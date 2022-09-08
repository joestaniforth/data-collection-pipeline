import os.path
import scraper
from unittest.mock import patch
import unittest
import json

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

    def test_scrape_heroes(self):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        dS.scrape_hero_data(dS.hero_urls[0])
        self.assertTrue(os.path.isfile('raw_data\\abaddon\\data.json'))
        with open('raw_data\\abaddon\\data.json', 'r') as file:
            values = json.load(file)
        for key in values:
            self.assertNotEqual(values[key], '')

if __name__ == '__main__':
    unittest.main()