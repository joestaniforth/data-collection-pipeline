import psycopg2
import json

class PostgreSQL_Fetcher:
    def __init__(self, credentials_json):
        with open(credentials_json, 'r') as credentials:
            self.credentials_dict = json.load(credentials)
    
    def fetch_id(self) -> list:
        with psycopg2.connect(
            host = self.credentials_dict['host'], 
            user = self.credentials_dict['user'], 
            password = self.credentials_dict['password'], 
            port = self.credentials_dict['port'], 
            database = 'postgres') as connection:
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT scraper_id FROM all_hero_data
                ''')
                id_list = cursor.fetchall()
        return id_list
    
if __name__ == '__main__':
    fetcher = PostgreSQL_Fetcher(credentials_json = 'credentials.json')
    print(fetcher.fetch_id())
        