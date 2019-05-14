import scrapy
from w3lib.html import remove_tags
from scrapyapp.items import HRPolicyRelationItem, DocumentItem, HRPolicyInfoItem

class HRSpider(scrapy.Spider):
	name = 'hrpolicy'
	start_urls = [
		'http://www.hr.uct.ac.za/hr/benefits/retirement/policy/'
	]

	#response contains the source codes
	def parse(self, response):
		#create an item
		hrpolicyrelationitems = HRPolicyRelationItem()
		documentitems = DocumentItem()
		hrpolicyinfoitems = HRPolicyInfoItem()

		policyname = response.css("h1::text").extract_first()

		hrpolicyinfoitems['policyname'] = policyname
		
		yield hrpolicyinfoitems #return

		headers = response.css(".head::text").extract()

		if "Policy information" in headers:
			table = response.css('.tablehr')[0] #policy information first

			tablerows = table.xpath(".//tbody/tr") #retrieve all the rows

			for row in tablerows:
				hrpolicyrelationitems['policyname'] = policyname
				hrpolicyrelationitems['relationship'] = row.xpath("td[1]//text()").extract_first()
				hrpolicyrelationitems['name'] = row.xpath("td[2]//text()").extract_first()
  				
				yield hrpolicyrelationitems #return
			
		document = response.css("#node-page-full-group-content-wrapper").extract_first()
		document = remove_tags(document)
		document = document.replace('\n', ' ').replace('\t', '')
		documentitems['document'] = document.strip()
		
		yield documentitems #return
		