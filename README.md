# Dotabuff Scraper

## Milestone 3: Prototype finding the individual page for each entry

Dotabuff provides structured pages for each hero which this scraper scrapes. The fields scraped are the hero name, portrait, win rate, and item data. This data changes on a weekly basis, and therefore, repeat scraping will have seperate data for win rate and items, allowing trends to be drawn from this data.

Dotabuff has a page with a list of heroes, so using the XPATH query:
```xpath
//a[descendant::*[@class = "hero"]]
```
The hero links can be grabbed by getting the href attribute from the elements returned by the above query. Putting this together, a method can be written to grab all these links, as below:

```python
def get_heroes(self) -> None:
        '''Gets the list of heroes from www.dotabuff.com\heroes, and saves the urls to these pages in self.get_heroes'''
        self.driver.get(self.url + '\heroes')
        heroes = self.driver.find_elements(by = By.XPATH, value = '//a[descendant::*[@class = "hero"]]')
        for hero in heroes:
            self.hero_urls.append(hero.get_attribute('href'))
```

This method is called in the initialiser and is the result is saved to a list, which is also initialised in the initialiser.

## Milestone 4: Retrieving data from details page

Scraping the data relied on writing XPATH queries for the various fields. This required the use of the descendant query to select elements containing specific terms, then selecting other tags that contained necessary data. For tabular data, this was especially necessary. This data, including a URL to the relevant hero portrait, was dumped to a json file. Given that there are some minor variations between hero pages, the queries had to be more robust than a path provided by chrome devtools. UUIDs and an ID were assigned to each entry, to catalogue them.

Scraping tabular data was initially done using nestled for loops, however, this is not performant so this was flattened to one for loop, which looked up the values for the necessary columns in one iteration.

```python
def scrape_hero_data(self, url) -> None:
        '''Scrapes the data for one hero and saves the result to /raw_data/hero_name/data.json
        
        Parameters
        ----------
        url: url to a hero on dotabuff in the format www.dotabuff.com/heroes/<hero_name>
        '''
        self.driver.get(url)
        try:
            win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "won"]]/span')
        except:
             win_rate_span = self.driver.find_element(by = By.XPATH, value = '//dd[descendant::*[@class = "lost"]]/span')
        hero_portrait = self.driver.find_element(by = By.XPATH, value = '//img[@class = "image-avatar image-hero"]')
        hero_portrait = hero_portrait.get_attribute('src')
        win_rate = win_rate_span.text
        hero_name = url.split('/')[-1]
        item_dict = dict()
        for i in range(1, 13):
            item_name = self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[2]').text
            item_dict.update({
               item_name:{
               'Matches Played': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[3]').text,
               'Matches Won': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[4]').text,
               'Win Rate': self.driver.find_element(by = By.XPATH, value = self.item_table_xpath + f'/tbody/tr[{i}]' + '/td[5]').text
               }
            })
        hero_dict = {
            'Hero Name': hero_name.capitalize(),
            'Win Rate':win_rate,
            'Portrait': hero_portrait,
            'Items': item_dict,
            'ID': hero_name.upper(),
            'UUID': str(uuid4())
        }
        if isdir(join(f'raw_data\\{hero_name}')):
            pass
        else:
            mkdir(join(f'raw_data\\{hero_name}'))
        hero_json = dumps(hero_dict)
        with open(f'raw_data\\{hero_name}\\data.json', 'w') as file:
            file.write(hero_json)
```

Scraping images was done with the requests library, see below:
```python
self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}

def scrape_hero_image(self, hero_name) -> None:
        '''Scrapes the hero portrait of a hero
        
        Parameters
        ----------
        hero_name: name of the hero to scrape
        '''
        with open(f'raw_data\\{hero_name}\\data.json', 'r') as file:
            hero_values = load(file)
        image_url = hero_values['Portrait']
        page = get(image_url, headers = self.headers)
        file_name = image_url.split('/')[-1]
        with open(f'raw_data\\{hero_name}\\{file_name}', 'wb') as file:
            file.write(page.content)
```

Sending this request with the user-agent header was necessary, otherwise the server would send a HTTP error 429, regardless of the frequency of the requests sent. This occured in development if headers were not sent. The value of the user-agent header was obtained from monitoring a http request from an instance of chrome.

## Milestone 5: Documentation and Testing

Unit testing was initially a challenge; none of the functions have any return values. Unit testing was therefore split into two broad types of test:
- Mock testing to determine whether a function was called or checking it was called the appropriate number of times
- Testing output files (data.json and jpgs of hero portraits) to determine they are in the correct format and not blank

.json files were loaded and iterated over to ensure no fields were blank. The filetype library was used to check whether the image was saved correctly as a jpg; as the method used to retrieve it could also retrieve HTTP errors and save the corresponding html document with a .jpg extension.

Patching the methods to be mock tested then allowed the number of calls to be tracked.

## Milestone 6: Scalably store the Data

PoatgreSQL was used on a free-tier microRDS AWS database. Psycopg2 was the connector of choice used for communication between the scraper and the Database. Initially, the intention was to scrape all data to the S3 bucket and pull the data into the SQL database from the bucket. The advantage to this approach was that the need local storage space was reduced, as the data could be stored in memory rather than on disk, through the below approach:
```python
 def stash_data_s3(self, data) -> None:
        file_obj = io.BytesIO(dumps(data[1]).encode('utf-8'))
        if f'{data[0]}/' not in self.s3_client.list_objects(Bucket = 'jsscraperbucket'):
            self.s3_client.put_object(Bucket = 'jsscraperbucket', Key = f'{data[0]}/', Body = b'')
        response = self.s3_client.upload_fileobj(file_obj, 'jsscraperbucket', f'{data[0]}/{data[0]}-{data[2]}_raw_data.json')
        return response
```
However, the storage taken up by the raw data was minimal, and as such, local storage is sufficient for these needs. The S3 bucket is still in use for image hosting, but data does not need to be stored there as this is not sustainable as it will incur costs.

## Milestone 7: Preventing Re-Scraping and Getting more data

As essentially the same data is being scraped each time the scraper runs, preventing re-scraping was more difficult than simply assigning and ID and looking this ID up. Eventually, it was decided that an ID of the hero name and the date of the week beginning would be concatenated to create an ID. A postgres query, shown below is run through psycopg2 to determine if a record exists, and in main.py, this is evaluated and if no record is found, the hero is scraped.
```SQL
SELECT COUNT(*) FROM all_hero_data
WHERE scraper_id = <target_id>
```
This returns a count, which means it will scale better as the database grows in size.

## Milestone 8: Containerising the scraper and running it on a Cloud Server

The scraper was containerised with the following dockerfile:
```dockerfile
COPY . .

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN apt-get install -yqq unzip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/


ENV DISPLAY=:99

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

The dockerfile installs chrome and chromedriver. This was tested locally and ran fine, with some minor alterations to allow the scraper to run on linux. These changes were significant enough to merit a branch (docker) to be created. For convienience, a docker-compose.yml file was written to streamline deployment. The use of docker compose had the added benefit of the secret section providing a secure way to store database credentials withut having to supply them as environemnt variables, which is insecure as they can be accessed from the running container through docker exec. 

An EC2 Instance running amazon linux 2 as the AMI was created, and docker was installed on it. Cronjobs were created to allow the scraper to run every week:
```shell
0 12 * * 1 (cd /home/ec2-user; docker-compose up && docker-compose down) >/home/ec2-user/container.log 2>&1
```
The idea of running the scraper on a Lambda or FarGate was considered, as they have better schedulers for starting and stopping the instance, not just running commands. The idea is that this would potentially reduce costs, as keeping an ec2 instance on full time can incur costs, especially out of the free tier usage limits, however, the free tier offerings were insufficient for this to be taken any further.

## Milestone 9: Monitoring and Alerting

The prometheus docker image was pulled to the EC2 instance. The prometheus.yml was configured to expose the ports on local host and the public IPv4 address to allow for metric monitoring. The prometheus command is incredibly complex with many arguments and switches (see below), so a prometheus-docker-compose.yml was written to streamline running the container.

```shell
sudo docker run --rm -p 9090:9090 --name prometheus -v /home/ec2-user/prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus --config-file=/etc/prometheus/prometheus.yml --web.enable-lifecycle
```
Grafana was then installed on a local machine, and was pointed at the public IPv4 address on port 9090 to monitor both the docker container and the ec2 instance as a whole. Most of the metrics on the dashboard were decided through trial and error and extensive research as to what they represent; they are not all intuitively named.

![Grafana Dashboard](https://github.com/joestaniforth/DataCollection/blob/docker/grafana%20screenshot.png)