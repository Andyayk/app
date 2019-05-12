import scrapy
from scrapyapp.items import QuoteItem

class QuoteSpider(scrapy.Spider):
	name = 'quotes'
	start_urls = [
		'http://quotes.toscrape.com'
	]

	#response contains the source codes
	def parse(self, response):
		"""
		title = response.css('title::text').extract()
		#return
		yield {'titletext' : title}
		"""

		#create an item
		items = QuoteItem()

		all_div_quotes = response.css(".quote")

		for quotes in all_div_quotes:

			title = quotes.css(".text::text").extract()
			author = quotes.css(".author::text").extract()
			tag = quotes.css(".tag::text").extract()

			items['title'] = title
			items['author'] = author
			items['tag'] = tag			

			#return
			yield items