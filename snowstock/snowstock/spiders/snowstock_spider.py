# coding=gbk
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy import Request
import time
import json
from snowstock.items import SnowstockInfoItem
"""
    ������������ȥѩ��ҳ��
    ����������https://xueqiu.com/S/SZ000651
"""
class SnowStockSpider(Spider):
    name = "snowstock"
    #start_urls = ["https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=01918&hl=0&source=all&sort=alpha&page=5&_=1481013713658"] #��������
    start_urls = "https://xueqiu.com/S/"
    stock_ids = ["SZ000651"] #�����Ժ���ȡ�����Ʊid

    #�ȳ�������������ҳ����������ˣ�Ȼ��ʱ��������п��ж��ٸ�����
    """
        ����һ������ҳ�棺
        https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=01918&hl=0&source=all&sort=alpha&page=5&_=1481013713658
        ���ص���һ��json���������۵����ݣ��ܷ�ֻ�������json�أ�
        �����У�count��comment��symbol��hl��source��sort��page��_
        countΪÿҳ����������
        commentδ֪
        symbolΪ��ƱID
        hlδ֪
        sourceδ֪
        sortΪ����ʽ��time��ʾ��ʱ������alpha��ʾ�������ȶ�����
        pageΪҳ����
        _Ϊʱ���
    """
    cookies={
        "bid":"245d7b1e72c5afb4f22e2709275454ac_iwbw50ic",
        "s":"8s19kxfky4", #���ֵ����������Ƕ�̬�仯�ģ���������Ϊ�̶���Ȼ�ɹ��ˣ��������û�н����
        "snbim_minify":"True",
        "xq_a_token":"47697ade308c557aab035d60928e25f3e4dea8f6",
        "xq_r_token":"c802a9a38f3d779d8181f536020f1da0e6a6c2e5"
    }

    def start_requests(self):
        for id in self.stock_ids:
            url = self.start_urls + id
            yield Request(url,meta={"stock_id":id},callback=self.parse)


    def parse(self, response):
        count = 10
        comment = 0
        symbol = response.meta["stock_id"]
        hl = 0
        source = "all"
        sort = "time"
        pages = range(1,101)
        #page = 1
        #�ɹ��ˣ���Ҫ�������Ĳ�����������ͼ��ϲ�
        print("���ʿ�ʼ,�ӵ�",pages[0],"ҳ����",pages[-1],"ҳ")
        for page in pages:
            current_time = time.time()  # ��ȡ��ǰʱ���
            parse_url = "https://xueqiu.com/statuses/search.json?count={0}&comment={1}&symbol={2}&hl={3}&source={4}&sort={5}&page={6}&_={7}".format(
                            count,comment,symbol,hl,source,sort,page,current_time) #��������
            print("MyCookie",self.cookies)
            print("���ʵ�url:",parse_url)
            yield Request(parse_url,cookies=self.cookies,dont_filter=True,callback=self.parse_page)



    def parse_page(self,response):
        postings = response.body.decode()
        print(postings)
        #postdict = dict(postings)
        postjson =  json.loads(postings)
        print(postjson)

        """
            ����json������ȡ��items����Ҫ������
            user_id:�û�id
            title:�е����е�û��
            created_at:1480245272000  ������ʱ�䣬������ʱ��������ǿ��Ը������������ע�⣬����ʵ���Ϻ�����������0
            retweet_count:ת����
            reply_count:������
            fav_count:�ղ���
            description:����������
            edited_at:�޸�ʱ��� ע�⣬����ʵ���Ϻ�����������0
            pic:ͼƬ��ַ
            user:�û�������
            timeBefore:"11-27 19:14" �����create_at��ʲôû���𣿣�
            reward_count:������
            source:"ѩ��" ��Դ
        """
        for each in postjson['list']:
            print("json:",each)
            #����json�����е�ÿ�����ݶ���
            stockinfoItem = SnowstockInfoItem()
            stockinfoItem["symbol"] = postjson["symbol"]
            stockinfoItem["user_id"] = each["user_id"]
            stockinfoItem["title"] = each["title"]
            stockinfoItem["created_at"] = each["created_at"]
            stockinfoItem["retweet_count"] = each["retweet_count"]
            stockinfoItem["reply_count"] = each["reply_count"]
            stockinfoItem["fav_count"] = each["fav_count"]
            stockinfoItem["description"] = each["description"]
            stockinfoItem["edited_at"] = each["edited_at"]
            stockinfoItem["pic"] = each["pic"]
            # if "user" in each:
            #     print("user��",each["user"])
            #     stockinfoItem["user"] = each["user"]
            stockinfoItem["timeBefore"] = each["timeBefore"]
            stockinfoItem["reward_count"] = each["reward_count"]
            stockinfoItem["source"] = each["source"]
            yield stockinfoItem









