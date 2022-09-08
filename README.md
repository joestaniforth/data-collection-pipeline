# Dotabuff Scraper

## Milestone 3: Prototype finding the individual page for each entry

Dotabuff provides structured pages for each hero which this scraper scrapes. The fields scraped are the hero name, portrait, win rate, and item data. This data changes on a weekly basis, and therefore, repeat scraping will have seperate data for win rate and items, allowing trends to be drawn from this data.

Scraping the data relied on writing XPATH queries for the various fields. This required the use of the descendant query to select elements containing specific terms, then selecting other tags that contained necessary data. For tabular data, this was especially necessary. This data, including a URL to the relevant hero portrait, was dumped to a json file.