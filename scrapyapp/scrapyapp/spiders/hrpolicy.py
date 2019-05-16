import scrapy
from w3lib.html import remove_tags
from scrapyapp.items import HRPolicyRelationItem, DocumentItem

class HRSpider(scrapy.Spider):
	name = 'hrpolicy'
	start_urls = [
		'http://www.hr.uct.ac.za/hr/policies/HR_policies'
	]

	#response contains the source codes
	def parse(self, response):
		listofhrpolicy = response.css('.tablehr')[0] #get all hr policies

		tablerows = listofhrpolicy.xpath(".//tbody/tr") #retrieve all the rows
		counter = 1

		for row in tablerows:
			if counter%2 == 1:
				noofcol = len(row.xpath("th").extract())
			else:
				noofcol = len(row.xpath("td").extract())

			for x in range(1, noofcol+1):
				next_page = None
				if counter%2 == 1:
					policygroup = row.xpath("th[" + str(x) + "]//text()").extract_first()
				else:
					next_page = row.xpath("td[" + str(x) + "]//a/@href").extract_first()

				#check next page not empty and is not a document
				if next_page is not None and ".doc" not in next_page:
					yield response.follow(next_page, callback=self.parse_page) #return

			counter += 1

	def parse_page(self, response):
		#create an item
		hrpolicyrelationitems = HRPolicyRelationItem()
		documentitems = DocumentItem()

		policyname = response.css("h1::text").extract_first()
		headers = response.css(".head::text").extract()

		if "Policy information" in headers:
			table = response.css('.tablehr')[0] #policy information first
			tr = table.xpath(".//tbody/tr") #retrieve all the rows

			for row in tr:
				hrpolicyrelationitems['policyname'] = policyname
				hrpolicyrelationitems['relationship'] = row.xpath("td[1]//text()").extract_first()
				hrpolicyrelationitems['name'] = row.xpath("td[2]//text()").extract_first()
  				
				yield hrpolicyrelationitems #return
			
		document = response.css("#node-page-full-group-content-wrapper").extract_first()
		document = remove_tags(document)
		document = document.replace('\n', ' ').replace('\t', '')
		documentitems['document'] = document.strip()
		documentitems['policyname'] = policyname
		
		yield documentitems #return
		