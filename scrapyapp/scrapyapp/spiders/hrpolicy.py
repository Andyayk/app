import scrapy
from w3lib.html import remove_tags
from scrapyapp.items import HRPolicyRelationItem, DocumentItem

"""
Useful commands:

scrapy crawl jokes -o data.csv
scrapy shell "http://quotes.toscrape.com"

"""

class HRSpider(scrapy.Spider):
	name = 'hrpolicy'
	start_urls = [
		'http://www.hr.uct.ac.za/hr/policies/HR_policies'
	]

	#response contains the source codes
	def parse(self, response):
		listofhrpolicy = response.css('.tablehr')[0] #get all hr policies

		tablerows = listofhrpolicy.xpath(".//tbody/tr") #retrieve all the rows
		counter = 1 #set row as 1

		for row in tablerows:
			if counter%2 == 1: #odd rows
				noofcol = len(row.xpath("th").extract()) #extract header column
			else: #even rows
				noofcol = len(row.xpath("td").extract()) #extract normal column

			for x in range(1, noofcol+1):
				next_pages = None
				if counter%2 == 1: #odd rows
					policygroup = row.xpath("th[" + str(x) + "]//text()").extract_first() #extract policygroup
				else: #even rows
					next_pages = row.xpath("td[" + str(x) + "]//a/@href").extract() #extract all links

				#check next page not empty and is not a document
				if next_pages is not None and ".doc" not in next_pages:
					for next_page in next_pages:
						yield response.follow(next_page, callback=self.parse_page) #return

			counter += 1 #go next row

	def parse_page(self, response):
		#create an item
		hrpolicyrelationitems = HRPolicyRelationItem()
		documentitems = DocumentItem()

		policyname = response.css("h1::text").extract_first() #extract policyname
		headers = response.css(".head::text").extract() #extract headers

		if "Policy information" in headers:
			table = response.css('.tablehr')[0] #extract policy information
			rows = table.xpath(".//tbody/tr") #retrieve all the rows

			for row in rows:
				hrpolicyrelationitems['policyname'] = policyname #add policyname to item
				hrpolicyrelationitems['relationship'] = row.xpath("td[1]//text()").extract_first() #add relationship to item
				hrpolicyrelationitems['name'] = row.xpath("td[2]//text()").extract_first() #add person name to item
				
				yield hrpolicyrelationitems #return
			
		document = response.css("#node-page-full-group-content-wrapper").extract_first() #extract whole policy webpage
		document = remove_tags(document) #remove html tags
		document = document.replace('\n', ' ').replace('\t', '') #replace all line breaks and tabs
		documentitems['document'] = document.strip() #add document to item
		documentitems['policyname'] = policyname #add policyname to item
		
		yield documentitems #return
		