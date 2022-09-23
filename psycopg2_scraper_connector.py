import psycopg2
from scraper import dotaScraper
import os
import json

class PostgreSQL_Connector:
    def __init__(self, credentials_json: json, hero_list: list):
        '''
        Establishes connection to postgres server, initialises some variables

        Parameters
        ----------

        credentials_csv: a csv with credentials in it in the following order:
        [0]: hostname
        [1]: username
        [2]: password
        [3]: port
        '''
        with open(credentials_json, 'r') as credentials:
            self.credentials_dict = json.load(credentials)

        self.hero_list = [hero.split('/')[-1] for hero in hero_list]
        
    def create_hero_list(self):
        '''
        Creates a table with a list of all heroes as the only column
        '''
        with psycopg2.connect(
            host = self.credentials_dict['host'], 
            user = self.credentials_dict['user'], 
            password = self.credentials_dict['password'], 
            port = self.credentials_dict['port'], 
            database = 'postgres') as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                '''CREATE TABLE IF NOT EXISTS heroes(
                hero_name VARCHAR(50) PRIMARY KEY
                );'''
                )
                for hero in self.hero_list:
                    cursor.execute(
                        f'''
                            INSERT INTO heroes (hero_name) 
                            VALUES ('{hero}')   
                        '''
                    )
    
    def create_hero_table(self):
        with psycopg2.connect(
            host = self.credentials_dict['host'], 
            user = self.credentials_dict['user'], 
            password = self.credentials_dict['password'], 
            port = self.credentials_dict['port'],
            database = 'postgres') as connection:
            with connection.cursor() as cursor:
                    cursor.execute(
                        f'''CREATE TABLE IF NOT EXISTS all_hero_data(
                        UUID VARCHAR(50) PRIMARY KEY,
                        date DATE NOT NULL,
                        hero_name VARCHAR(20) NOT NULL,
                        win_rate DECIMAL NOT NULL, 
                        item_1 VARCHAR(50) NOT NULL,
                        item_1_matches_played INTEGER NOT NULL,
                        item_1_matches_won INTEGER NOT NULL,
                        item_1_win_rate DECIMAL NOT NULL,
                        item_2 VARCHAR(50) NOT NULL,
                        item_2_matches_played INTEGER NOT NULL,
                        item_2_matches_won INTEGER NOT NULL,
                        item_2_win_rate DECIMAL NOT NULL,
                        item_3 VARCHAR(50) NOT NULL,
                        item_3_matches_played INTEGER NOT NULL,
                        item_3_matches_won INTEGER NOT NULL,
                        item_3_win_rate DECIMAL NOT NULL,
                        item_4 VARCHAR(50) NOT NULL,
                        item_4_matches_played INTEGER NOT NULL,
                        item_4_matches_won INTEGER NOT NULL,
                        item_4_win_rate DECIMAL NOT NULL,
                        item_5 VARCHAR(50) NOT NULL,
                        item_5_matches_played INTEGER NOT NULL,
                        item_5_matches_won INTEGER NOT NULL,
                        item_5_win_rate DECIMAL NOT NULL,
                        item_6 VARCHAR(50) NOT NULL,
                        item_6_matches_played INTEGER NOT NULL,
                        item_6_matches_won INTEGER NOT NULL,
                        item_6_win_rate DECIMAL NOT NULL,
                        item_7 VARCHAR(50) NOT NULL,
                        item_7_matches_played INTEGER NOT NULL,
                        item_7_matches_won INTEGER NOT NULL,
                        item_7_win_rate DECIMAL NOT NULL,
                        item_8 VARCHAR(50) NOT NULL,
                        item_8_matches_played INTEGER NOT NULL,
                        item_8_matches_won INTEGER NOT NULL,
                        item_8_win_rate DECIMAL NOT NULL,
                        item_9 VARCHAR(50) NOT NULL,
                        item_9_matches_played INTEGER NOT NULL,
                        item_9_matches_won INTEGER NOT NULL,
                        item_9_win_rate DECIMAL NOT NULL,
                        item_10 VARCHAR(50) NOT NULL,
                        item_10_matches_played INTEGER NOT NULL,
                        item_10_matches_won INTEGER NOT NULL,
                        item_10_win_rate DECIMAL NOT NULL,
                        item_11 VARCHAR(50) NOT NULL,
                        item_11_matches_played INTEGER NOT NULL,
                        item_11_matches_won INTEGER NOT NULL,
                        item_11_win_rate DECIMAL NOT NULL,
                        item_12 VARCHAR(50) NOT NULL,
                        item_12_matches_played INTEGER NOT NULL,
                        item_12_matches_won INTEGER NOT NULL,
                        item_12_win_rate DECIMAL NOT NULL,
                        scraper_id VARCHAR(50) NOT NULL
                        );'''
                        )
    
    def flatten_json(self, target_json):
        with open(target_json, 'r') as file:
            dict_json = json.load(file)
        flat_json = {
        'UUID':f'{dict_json["UUID"]}',
        'Hero Name':f'{dict_json["Hero Name"]}',
        'Win Rate':f'{dict_json["Win Rate"]}',
        'Date Scraped':f'{dict_json["Date Scraped"]}',
        'ID':f'{dict_json["ID"]}'
        }
        item_keys = list(dict_json['Items'].keys())
        for i, name, item in zip(range(1,13), item_keys, dict_json['Items']):
            item_json = {
                f'item_{i}':f'{name}',
                f'item_{i}_matches_played':f'{dict_json["Items"][item]["Matches Played"]}',
                f'item_{i}_matches_won':f'{dict_json["Items"][item]["Matches Won"]}',
                f'item_{i}_win_rate':f'{dict_json["Items"][item]["Win Rate"]}'
            }   
            flat_json.update(item_json)
        return flat_json

    def push_data(self, hero_json):
        query_dict = self.flatten_json(target_json = hero_json)
        with psycopg2.connect(
            host = self.credentials_dict['host'], 
            user = self.credentials_dict['user'], 
            password = self.credentials_dict['password'], 
            port = self.credentials_dict['port'],
            database = 'postgres') as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'''
                INSERT INTO all_hero_data (UUID, date, hero_name, win_rate, 
                item_1, item_1_matches_played, item_1_matches_won, item_1_win_rate, 
                item_2, item_2_matches_played, item_2_matches_won, item_2_win_rate, 
                item_3, item_3_matches_played, item_3_matches_won, item_3_win_rate, 
                item_4, item_4_matches_played, item_4_matches_won, item_4_win_rate,
                item_5, item_5_matches_played, item_5_matches_won, item_5_win_rate,
                item_6, item_6_matches_played, item_6_matches_won, item_6_win_rate,
                item_7, item_7_matches_played, item_7_matches_won, item_7_win_rate,
                item_8, item_8_matches_played, item_8_matches_won, item_8_win_rate,
                item_9, item_9_matches_played, item_9_matches_won, item_9_win_rate,
                item_10, item_10_matches_played, item_10_matches_won, item_10_win_rate,
                item_11, item_11_matches_played, item_11_matches_won, item_11_win_rate,
                item_12, item_12_matches_played, item_12_matches_won, item_12_win_rate,
                scraper_id)
                VALUES ('{query_dict["UUID"]}','{query_dict["Date Scraped"]}','{query_dict["Hero Name"]}','{query_dict["Win Rate"]}',
                '{query_dict["item_1"]}','{query_dict["item_1_matches_played"]}','{query_dict["item_1_matches_won"]}','{query_dict["item_1_win_rate"]}',
                '{query_dict["item_2"]}','{query_dict["item_2_matches_played"]}','{query_dict["item_2_matches_won"]}','{query_dict["item_2_win_rate"]}',
                '{query_dict["item_3"]}','{query_dict["item_3_matches_played"]}','{query_dict["item_3_matches_won"]}','{query_dict["item_3_win_rate"]}',
                '{query_dict["item_4"]}','{query_dict["item_4_matches_played"]}','{query_dict["item_4_matches_won"]}','{query_dict["item_4_win_rate"]}',
                '{query_dict["item_5"]}','{query_dict["item_5_matches_played"]}','{query_dict["item_5_matches_won"]}','{query_dict["item_5_win_rate"]}',
                '{query_dict["item_6"]}','{query_dict["item_6_matches_played"]}','{query_dict["item_6_matches_won"]}','{query_dict["item_6_win_rate"]}',
                '{query_dict["item_7"]}','{query_dict["item_7_matches_played"]}','{query_dict["item_7_matches_won"]}','{query_dict["item_7_win_rate"]}',
                '{query_dict["item_8"]}','{query_dict["item_8_matches_played"]}','{query_dict["item_8_matches_won"]}','{query_dict["item_8_win_rate"]}',
                '{query_dict["item_9"]}','{query_dict["item_9_matches_played"]}','{query_dict["item_9_matches_won"]}','{query_dict["item_9_win_rate"]}',
                '{query_dict["item_10"]}','{query_dict["item_10_matches_played"]}','{query_dict["item_10_matches_won"]}','{query_dict["item_10_win_rate"]}',
                '{query_dict["item_11"]}','{query_dict["item_11_matches_played"]}','{query_dict["item_11_matches_won"]}','{query_dict["item_11_win_rate"]}',
                '{query_dict["item_12"]}','{query_dict["item_12_matches_played"]}','{query_dict["item_12_matches_won"]}','{query_dict["item_12_win_rate"]}',
                '{query_dict["ID"]}'
                );
                ''')

    def push_data_from_local(self):
        for folder in os.listdir('raw_data'):
            for file in os.listdir(f'raw_data\\{folder}'):
                if file.endswith('.json'):
                    self.push_data(hero_json = f'raw_data\\{folder}\\{file}')



if __name__ == '__main__':
    scraper = dotaScraper(url = 'https://www.dotabuff.com/')
    connector = PostgreSQL_Connector(credentials_json = 'credentials.json', hero_list = scraper.hero_urls)
    connector.create_hero_table()
    connector.push_data_from_local()
