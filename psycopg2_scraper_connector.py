import psycopg2
import csv

credentials_list = list

with open('credentials.csv', 'r') as credentials:
    for row in credentials:
        credentials_list.append(row)

with psycopg2.connect(host = credentials_list[0], user = credentials_list[1], password = credentials_list[2], port = credentials[3]) as connection:
    with connection.cursor as cursor:
        cursor.execute(
        '''CREATE TABLE [IF NOT EXISTS] heroes(
        hero_name VARCHAR(50) PRIMARY KEY
        );''')