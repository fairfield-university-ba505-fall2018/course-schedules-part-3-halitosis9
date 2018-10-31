import scrapy
    
class CatalogSpider(scrapy.Spider):
        name = "catalog"
    
        def start_requests(self):
            urls = ['http://catalog.fairfield.edu/courses/']
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
    
        def parse(self, response):
            links = response.css('a::attr(href)').re(r'/courses/.+')
            
            for link in links:
                yield response.follow(url=link, callback=self.parse_program)
        
        def parse_program(self,response):
            program_code =response.css('.page-title::text').re_first(r'\(\w+\)').strip('()')
            program_name =response.css('.page-title::text').extract_first().split(' (')[0]
            extratypes = {'Attributes: ':'attributes','Attribute: ':'attributes',
                'Fee:':'fees',
                'Corequisite: ':'coreqs','Corequisites: ':'coreqs',
                'Prerequisite: ':'prereqs','Prerequisites: ':'prereqs'}
            courseblocks = response.css('.courseblock')
            for courseblock in courseblocks:
                titleblock = courseblock.css('.courseblocktitle strong::text').extract_first()
                catalogid = titleblock.split('\xa0')[0]
                coursetitle = titleblock.split('\xa0')[1]
                credits = courseblock.css('.courseblocktitle .credits::text').extract_first()
                extratexts = courseblock.css('.courseblockextra *::text').extract()
                extras = {'attributes':'','fees':'','coreqs':'','prereqs':''}

                typ=""
                for etxt in extratexts:
                    if etxt in extratypes:
                        if typ != "":
                            extras[extratypes[typ]] = txt.replace('\xa0',' ').strip()
                        typ =etxt
                        txt =""
                    else:
                        txt += etxt
                if typ != "":
                    extras[extratypes[typ]] = txt.replace('\xa0',' ').strip()
                
                description = courseblock.css('.courseblockdesc::text').extract_first()
                yield {
                    'program_code':program_code,
                    'program_name':program_name,
                    'catalog_id':catalogid,
                    'course_title':coursetitle,
                    'credits':credits,
                    'prereqs':extras['prereqs'],
                    'coreqs':extras['coreqs'],
                    'fees':extras['fees'],
                    'attributes':extras['attributes'],
                    'description':description
                }