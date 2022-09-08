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

Scraping the data relied on writing XPATH queries for the various fields. This required the use of the descendant query to select elements containing specific terms, then selecting other tags that contained necessary data. For tabular data, this was especially necessary. This data, including a URL to the relevant hero portrait, was dumped to a json file.

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

