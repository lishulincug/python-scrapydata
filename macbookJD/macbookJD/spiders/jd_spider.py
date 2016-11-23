# coding=GBK
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from macbookJD.items import MacbookjdItem,CommentItem
from scrapy import Request
import requests


class MacbookJDSpider(Spider):
    name = "macbookJD"
    #allowed_domains = ["https://www.jd.com/"]
    #��ʼURL
    begin_Url = ["http://search.jd.com/Search?keyword=macbook&enc=utf-8&wq=macbook&pvid=yq4jtrvi.1w3z06"]
    start_urls=[]
    index = 1

    has_url=[] #�Ѿ�������URL
    # �������ֵ�¼״̬���ɰ�chrome�Ͽ����������ַ�����ʽcookieת�����ֵ���ʽ��ճ�����˴�
    cookies = {}

    # ���͸���������httpͷ��Ϣ���е���վ��Ҫαװ�������ͷ������ȡ���е�����Ҫ
    headers = {
        # 'Connection': 'keep - alive',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }

    def getNextScrapyUrl(self):
        if len(self.start_urls) > self.index :
            self.index = self.index + 1
            return self.start_urls[self.index-1]
        else:
            return None


    def start_requests(self):
        """
        ����һ�����غ��������������Ƿ�����һ��Request����
        """
        #��ȡ��Ҫ������ƷID
        response = requests.Session().get(self.begin_Url[0])
        print response.content
        selector = Selector(response)
        goods = selector.xpath("//div[@id='J_goodsList']/ul/li/@data-sku").extract()
        for each in goods:
            #ǰ�������һ��u   u'1213424'
            #ID = (eachID[0])[(eachID[0])[1]:(eachID[0])[-1]]
            #print each
            urlString = "http://item.jd.com/%s.html" % each
            print "urlString:",urlString
            self.start_urls.append(urlString)
        if len(self.start_urls) > 0:
            yield Request(self.start_urls[0], callback=self.parse,headers=self.headers, cookies=self.cookies,meta={"id":self.start_urls[0]})

    def parse(self, response):
        macitem = MacbookjdItem()
        macitem['_id'] = response.meta['id']
        selector = Selector(response)
        goodsInfo = selector.xpath("//div[@id='product-intro']")
        macitem['title'] = goodsInfo.xpath("div[2]/div/div[1]/h1/text()").extract()[0]
        macitem['img_url'] = goodsInfo.xpath("div[1]/div[1]/img/@src").extract()[0]
        #macitem['price'] = goodsInfo.xpath("div[2]/div/div[@id='summary']/div[2]/div[1]/text()").extract()[0]
        price = goodsInfo.xpath("div[2]/div/div[@id='summary']/div[2]/div[2]")
        if price:
            firstprice = (price.xpath('string(.)').extract()[0]).replace(" ","")
            if firstprice.find('[') != -1 and  firstprice.find(']') != -1:
                macitem['price'] = firstprice[firstprice.index('[')+1:firstprice.index(']')]
            else:
                macitem['price'] = 'None'
        else:
            macitem['price'] = 'None'

        macitem['description'] = goodsInfo.xpath("div[2]/div/div[1]/div[@id='p-ad']/text()").extract()
        macitem['comments'] = " "

        print macitem['_id']
        print macitem['title']
        print macitem['img_url']
        print macitem['price']
        print macitem['description']
        print macitem['comments']
        yield macitem

        next_url = self.getNextScrapyUrl()  # response.url����ԭ�����url
        if next_url != None:  # ����������µ�url
            print("begin next scrapy")
            print "next_url:", next_url
            yield Request(next_url, callback=self.parse, headers=self.headers, cookies=self.cookies,meta={"id":next_url})





