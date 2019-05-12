# -*- coding: utf-8 -*-
import scrapy
from scrapyapp.items import JokeItem
from scrapy.loader import ItemLoader
"""
Useful commands:

scrapy crawl jokes -o data.csv
scrapy shell "http://quotes.toscrape.com"

"""
class JokesSpider(scrapy.Spider):
    name = 'jokes'

    #allowed_domains = ['mydomain.com']
    
    start_urls = [
        'http://www.laughfactory.com/jokes/family-jokes'
    ]

    def parse(self, response):
        for joke in response.xpath("//div[@class='jokes']"):
            loader = ItemLoader(item=JokeItem(), selector=joke)
            loader.add_xpath("joke_text", ".//div[@class='joke-text']/p")

            #return
            yield loader.load_item()

            """
            #return
            yield {
                'joke_text' : joke.xpath(".//div[@class='joke-text']/p").extract_first()
            }
            """
            
        #go to next page and retrieve the first item in a list
        next_page = response.xpath("//li[@class='next']/a/@href").extract_first()

        #check next page not empty
        if next_page is not None:
            next_page_link = response.urljoin(next_page)

            #return
            yield scrapy.Request(url=next_page_link, callback=self.parse) #go next page 
