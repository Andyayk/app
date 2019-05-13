import scrapy

class HRSpider(scrapy.Spider):
	name = 'hrpolicy'
	start_urls = [
		'http://www.hr.uct.ac.za/hr/benefits/retirement/policy/'
	]

	#response contains the source codes
	def parse(self, response):

		results = response.css('.head')

		for row in response.xpath('//*[@class="tablehr"]//tbody/tr'):
			#return
			yield {
				'first' : row.xpath('td[1]//text()').extract_first(),
				'last': row.xpath('td[2]//text()').extract_first()
			}