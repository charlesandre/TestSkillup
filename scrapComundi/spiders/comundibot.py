# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http import Request
import csv


class comundiBotSpider(CrawlSpider):
    name = 'comundibot'
    # Define the allowed dommain and the start page
    allowed_domains = ['https://www.comundi.fr/']
    start_urls = ['https://www.comundi.fr/']
    #Headers for ths csv file
    fieldnames = ["Url", "Name", "parsed_ref", "parsed_objectives", "parsed_duration", "parsed_price", "processed_duration", "processed_price"]
    with open(r'formations.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
    formation_list = []

    #First go through the start page
    def parse(self, response):
        #Find the different categories of formations
        categories = response.xpath('//a[@class="btn btn-tag"]/@href').extract()
        #Go though every categories and call a new method with the link
        for cat in categories:
            caturl = "https://www.comundi.fr" + cat
            yield Request(caturl, callback=self.scrap_cat, dont_filter=True)

#Find the 2nd level of categroies and do the same as previous
    def scrap_cat(self, response):
        links = response.xpath('//div[contains(@class,"panel-default")]/a/@href').extract()
        for link in links:
            formurl = "https://www.comundi.fr" + link
            yield Request(formurl, callback=self.scrap_form, dont_filter=True)

#FInd every formation link and call a function that will go thoufh every formation to get the detailed info
    def scrap_form(self, response):
        links = response.xpath('//a[@class = "category-list-item"]/@href').extract()
        for link in links:
            #To be sure that a link isn't called twice, because some formations are in multiple categories
            if link not in self.formation_list:
                self.formation_list.append(link)
                detailsurl = "https://www.comundi.fr" + link
                yield Request(detailsurl, callback=self.scrap_details, dont_filter=True)

#Funciton that will get all the needed details and put them in a csv
    def scrap_details(self,response):
        url = response.url
        name = response.xpath('//h1[@class="h1 title-topping"]/text()').extract_first()
        objectifs = response.xpath('//div[@id = "objectifs1"]/ul').extract()
        duree = response.xpath('//table/tbody/tr/th/text()').extract_first()
        prix = response.xpath('//table/tbody/tr/td/ins/text()').extract_first()
        ref = response.xpath('//p[@class="ref hidden-xs"]/text()').extract_first()

        #when duration and price is undefined we can't process the data so we just put "NA"
        if duree == None or prix == None:
            duree = "NA"
            processed_duration = "NA"
            prix = "NA"
            processed_price = "NA"
        else:
            nombrejour = str(duree).strip().split(' ')[0]
            if '+' in nombrejour:
                tmp = nombrejour.split('+')
                nombrejour = int(tmp[0]) + int(tmp[1])
            processed_duration = int(nombrejour)*7
            processed_price = prix.replace(" ", "").split('\n')[0]
            processed_price = float(processed_price)

        #Creating the row that wil be written in the csv.

        formation = [url.encode('utf-8'), name.encode('utf-8'), ref.encode('utf-8'), str(objectifs).encode('utf8'), duree.encode('utf-8'), prix.encode('utf-8'), processed_duration, processed_price]
        #Open the file and write
        with open(r'formations.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(formation)
