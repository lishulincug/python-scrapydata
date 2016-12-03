# coding=GBK
from scrapy.spiders import Spider
from scrapy import Request
from scrapy import FormRequest
from weibostock.items import InformationItem,TweetsItem
import weibostock.login as login
from scrapy.selector import Selector
import weibostock.info as info


class WeiboStockSpider(Spider):
    SZSHHK = info.SZSHHK
    SZSHHK_hasget = []
    name = "weibostock"
    domian = "http://weibo.cn"
    start_urls = []
    # �Ѿ���ȡ��΢��ID
    Tweets_ID = []
    #�Ѿ����ʵ�����
    hasget_link = []
    cookies = []

    # ��������е�¼������ȡ��¼���URL����Ϊ��ʼURL
    def __init__(self, *args, **kw):
        super(Spider, self).__init__(*args, **kw)
        weibo = login.WeiboLogin()
        loginurl = weibo.login()
        if loginurl:
            self.start_urls.append(loginurl)
            # ����MozillaCookieJarʵ������
            self.cookies = weibo.getCookieInfo()
            print("self.cookies:", self.cookies)


    def parse(self, response):
        body = response.body.decode()
        print("response:",body)
        if body.find('feedBackUrlCallBack') != -1:
            #print response.body

            url = 'http://weibo.cn/'
            print("self.cookies:", self.cookies)

            # ���ҹؼ��ʣ���������·����ʹ��POST����
            # ���SHSZHK���ڣ������ѡ��һ���ؼ��ʽ�������������������ȥ��
            #print self.SZSHHK
            for everyone in self.SZSHHK:
                #SZSHHK_hasget = choice(self.SZSHHK)
                postdata = {
                    "keyword": everyone,
                    "smblog": u"��΢��"
                }
                yield FormRequest(url=info.searchUrl,
                                  formdata=postdata,
                                  callback=self.parseSearch,
                                  cookies=self.cookies)
        else:
            print('login failed: errno=%s, reason=%s')

    def parseSearch(self,response):
        #print response.body
        # ��ȡ��ע��΢����Ϣ
        # ����ǰ��ע�ߵĻ�����Ϣ����item��

        selector = Selector(response)
        Tweets = selector.xpath('//div[@class="c"]')
        if Tweets:
            # ��parse1���в�ͬ��ͨ��forѭ��Ѱ����Ҫ�Ķ���
            for everytweet in Tweets:
                #�ų�΢��Ϊ��
                if everytweet:
                    # ��ȡÿ��΢��Ψһid��ʶ
                    m_id = everytweet.xpath('@id').extract()
                    if m_id:
                        mark_id = m_id[0]
                        if mark_id.find("M_") == -1 or not mark_id:
                            continue
                        # ��id��Ϊ�յ�ʱ����뵽΢����ȡ�б�,ȥ�ز����������Ѿ���ȡ����΢�����ٻ�ȡ
                        if mark_id not in self.Tweets_ID:
                            tweetsItem = TweetsItem()
                            tweetsItem["_id"] = mark_id
                            print("mark_id:",mark_id)
                            contentTemp = everytweet.xpath('div[1]/span[@class="ctt"]')
                            content = contentTemp.xpath('string(.)').extract()

                            #��΢��ҳ���У������ͼƬ�Ļ�����ֳ�����div��ʾ����һ��div����ʾ�������ݣ��ڶ���div��ʾͼƬ�����۵�����
                            #���û��ͼƬ�Ļ���ֻ����ʾһ��div���������۵ȶ�����������ʾ
                            mydiv = ""
                            if everytweet.xpath('div[2]').extract():
                                print("test temp:", everytweet.xpath('div[2]').extract())
                                mydiv = everytweet.xpath('div[2]')
                                timeloc = mydiv.xpath('span[@class="ct"]/text()').extract()
                                # picurl = everytweet.xpath('div[2]/a[2]/img/@src').extract()
                                picurl = mydiv.xpath('a[2]/@href').extract()
                                like = mydiv.xpath('a[3]/text()').extract()
                                transfer = mydiv.xpath('a[4]/text()').extract()
                                comment = mydiv.xpath('a[5]/text()').extract()
                            elif everytweet.xpath('div[1]').extract():
                                print("test temp:", everytweet.xpath('div[1]').extract())
                                mydiv = everytweet.xpath('div[1]')
                                timeloc = mydiv.xpath('span[@class="ct"]/text()').extract()
                                # picurl = everytweet.xpath('div[2]/a[2]/img/@src').extract()
                                picurl = "None"
                                like = mydiv.xpath('a[2]/text()').extract()
                                transfer = mydiv.xpath('a[3]/text()').extract()
                                comment = mydiv.xpath('a[4]/text()').extract()
                            else:
                                continue

                            if content:
                                print("content:", content)
                                tweetsItem['Content'] = content[0]
                            if picurl:
                                print(picurl)
                                tweetsItem['Pic_Url'] = picurl[0]
                            if comment:
                                print(comment)
                                # tweetsItem['Num_Comment'] = (comment[0])[(comment[0].index('[') + 1):comment[0].index(']')]
                                tweetsItem['Num_Comment'] = comment[0]
                            if like:
                                print(like)
                                # tweetsItem['Num_Like'] = (like[0])[(like[0].index('[') + 1):like[0].index(']')]
                                tweetsItem['Num_Like'] = like[0]
                            if transfer:
                                print(transfer)
                                # tweetsItem['NUm_Transfer'] = (transfer[0])[(transfer[0].index('[') + 1):transfer[0].index(']')]
                                tweetsItem['NUm_Transfer'] = transfer[0]
                            if timeloc:
                                tweetsItem['Time_Location'] = timeloc[0]
                            self.Tweets_ID.append(mark_id)
                            yield tweetsItem


        nextLink = selector.xpath('//div[@class="pa"]/form/div/a[1]/@href').extract()
        if nextLink:
            nextLink = nextLink[0]
            if nextLink not in self.hasget_link:
                nextLink = self.domian + nextLink
                print(nextLink)
                self.hasget_link.append(nextLink)
                yield Request(nextLink, callback=self.parseSearch, cookies=self.cookies)


