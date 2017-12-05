# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http import Request
import csv


class ComundiBotSpider(CrawlSpider):
    name = 'comundibot'
    allowed_domains = ['https://www.comundi.fr/']
    start_urls = ['https://www.comundi.fr/']

    def parse(self, response):
        #Sur la premiere page on recupère les liens
        categories = response.xpath('//a[@class="btn btn-tag"]/@href').extract()
        for cat in categories:
            caturl = "https://www.comundi.fr" + cat
            yield Request(caturl, callback=self.scrap_cat, dont_filter=True)

    def scrap_cat(self, response):
        links = response.xpath('//div[contains(@class,"panel-default")]/a/@href').extract()
        for link in links:
            formurl = "https://www.comundi.fr" + link
            yield Request(formurl, callback=self.scrap_form, dont_filter=True)

    def scrap_form(self, response):
        links = response.xpath('//a[@class = "category-list-item"]/@href').extract()
        formation_list = []
        for link in links:
            detailsurl = "https://www.comundi.fr" + link
            yield Request(detailsurl, callback=self.scrap_details, dont_filter=True)

    def scrap_details(self,response):
        url = response.url
        name = response.xpath('//h1[@class="h1 title-topping"]/text()').extract_first()
        objectifs = response.xpath('//div[@id = "objectifs1"]/ul').extract()
        duree = response.xpath('//table/tbody/tr/th/text()').extract_first()
        prix = response.xpath('//table/tbody/tr/td/ins/text()').extract_first()
        if duree == None:
            duree = "NA"
        if prix == None:
            prix = "NA"

        formation = [url.encode('utf-8'), name.encode('utf-8'), str(objectifs).encode('utf8'), duree.encode('utf-8'), prix.encode('utf-8')]

        with open(r'document.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow(formation)
