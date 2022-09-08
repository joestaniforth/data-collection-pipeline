import os
import os.path
import scraper
from unittest.mock import patch
import unittest
import json
import filetype

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

    def test_scrape_hero(self):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        dS.scrape_hero_data(dS.hero_urls[0])
        self.assertTrue(os.path.isfile('raw_data\\abaddon\\data.json'))
        with open('raw_data\\abaddon\\data.json', 'r') as file:
            values = json.load(file)
        for key in values:
            self.assertNotEqual(values[key], '')
        for key in values['Items']:
            self.assertNotEqual(values['Items'][key],'')
    
    @patch('scraper.dotaScraper.scrape_hero_data')
    def test_scrape_heores(self, mock_get_hero):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        dS.scrape_all_heroes()
        self.assertEqual(mock_get_hero.call_count, len(dS.hero_urls))

    def test_scrape_image(self):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        with open('raw_data\\abaddon\\data.json', 'r') as file:
            test_values = json.load(file)
        test_url = test_values['Portrait']
        dS.scrape_hero_image(hero_name = 'abaddon')
        file_name = test_url.split('/')[-1]
        image_type = filetype.guess_extension(f'raw_data\\abaddon\\{file_name}')
        self.assertEqual('jpg', image_type)

    @patch('scraper.dotaScraper.scrape_hero_image')
    def test_scrape_images(self, mock_image_scrape):
        dS = scraper.dotaScraper(url = 'https://www.dotabuff.com/')
        made_dirs = list()
        for url in dS.hero_urls:
            hero_name = url.split('/')[-1]
            if not os.path.isdir(f'raw_data//{hero_name}'):
                os.mkdir(f'raw_data//{hero_name}')
                made_dirs.append(hero_name)
        dS.scrape_all_hero_images()
        for dir in made_dirs:
            os.rmdir(f'raw_data//{dir}')
        self.assertEqual(mock_image_scrape.call_count, len(dS.hero_urls))


if __name__ == '__main__':
    unittest.main()