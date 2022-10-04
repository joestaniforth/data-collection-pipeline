import unittest
from unittest.mock import patch
from scraper import dotaScraper
from psycopg2_fetcher import PostgreSQL_Fetcher
from psycopg2_scraper_connector import PostgreSQL_Connector
from main import local_scrape

credentials = 'credentials.json'

class TestMain(unittest.TestCase):
    def __init__(self) -> None:
        self.scraper = dotaScraper(url = 'https://www.dotabuff.com/')
        self.connector = PostgreSQL_Connector(credentials_json = credentials, hero_list = self.scraper.hero_urls)
        self.fetcher = PostgreSQL_Fetcher(credentials_json = credentials)

    def test_class_scraper(self):
        #Test url list to scrape is populated
        self.assertTrue(len(self.scraper.hero_urls) > 0)

    

if __name__ == '__main__':
    unittest.main()
        