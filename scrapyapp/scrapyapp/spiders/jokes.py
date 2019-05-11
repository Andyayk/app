# -*- coding: utf-8 -*-
import scrapy
from scrapyapp.items import JokeItem
from scrapy.loader import ItemLoader

#scrapy crawl jokes -o data.csv

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

            yield loader.load_item()

            """
            yield {
                'joke_text' : joke.xpath(".//div[@class='joke-text']/p").extract_first()
            }
            """
            
        #go to next page
        next_page = response.xpath("//li[@class='next']/a/@href").extract_first()

        #check next page not empty
        if next_page is not None:
            next_page_link = response.urljoin(next_page)

            yield scrapy.Request(url=next_page_link, callback=self.parse) #go next page 
