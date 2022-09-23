from scraper import dotaScraper
from psycopg2_scraper_connector import PostgreSQL_Connector
from psycopg2_fetcher import PostgreSQL_Fetcher

credentials = 'credentials.json'

scraper = dotaScraper(url = 'https://www.dotabuff.com/')
connector = PostgreSQL_Connector(credentials_json = credentials, hero_list = scraper.hero_urls)
fetcher = PostgreSQL_Fetcher(credentials_json = credentials)

for url in scraper.hero_urls:
    id_to_scrape = scraper.generate_id(url.split('/')[-1])
    scrape_flag = fetcher.fetch_id(target_id = id_to_scrape)
    if scrape_flag == 0:
        data = scraper.scrape_hero_data(url = url, id = id_to_scrape, hero_name = url.split('/')[-1])
        scraper.stash_data_local(data = data)
    connector.push_data_from_local()
    


scraper.scrape_all_heroes()
connector.push_data_from_local()