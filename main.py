from scraper import dotaScraper
from psycopg2_scraper_connector import PostgreSQL_Connector
from psycopg2_fetcher import PostgreSQL_Fetcher

credentials = 'credentials.json'

scraper = dotaScraper(url = 'https://www.dotabuff.com/')
connector = PostgreSQL_Connector(credentials_json = credentials, hero_list = scraper.hero_urls)
fetcher = PostgreSQL_Fetcher(credentials_json = credentials)

id_list = fetcher.fetch_id()
scraper.scrape_all_heroes(id_list = id_list)
connector.push_data_from_local()