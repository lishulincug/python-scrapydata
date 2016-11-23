# coding=GBK
from  scrapy.spiders import Spider
import myweibo.login as login
from scrapy.selector import Selector
import json,re
import scrapy
from scrapy import Request
from myweibo.items import InformationItem,TweetsItem
import cookielib

class MyWeiboSpider(Spider):
    name = "myweibo"
    domian = "http://weibo.cn/"
    login_urls = []
    start_urls = []
    old_weibos = []
    #�Ѿ���ȡ���û�ID�����б���
    Follow_ID = []
    #�Ѿ���ȡ��΢��ID
    Tweets_ID = []
    cookies = []

    #��������е�¼������ȡ��¼���URL����Ϊ��ʼURL
    def __init__(self,*args,**kw):
        super(Spider,self).__init__(*args,**kw)
        weibo = login.WeiboLogin()
        loginurl = weibo.login()
        if loginurl:
            #starturl = "http://weibo.com"
            self.start_urls.append(loginurl)
            # ����MozillaCookieJarʵ������
            self.cookies = weibo.getCookieInfo()
            print "self.cookies:", self.cookies
                # cookie = "<Cookie ALC=ac%3D2%26bt%3D1479746756%26cv%3D5.0%26et%3D1511282756%26scf%3D%26uid%3D3815666512%26vf%3D0%26vs%3D0%26vt%3D0%26es%3De5f0cbff8d7d1a43b7d312af20e03fad for .login.sina.com.cn/>, <Cookie LT=1479746756 for .login.sina.com.cn/>, <Cookie tgc=TGT-MzgxNTY2NjUxMg==-1479746756-ja-4002E565EEDFBCD528E34BA900197741 for .login.sina.com.cn/>, <Cookie ALF=1511282756 for .sina.com.cn/>, <Cookie SCF=AljccvcU-MXu7dAv8tAU2PqxO4Mh7up-usmKN5WrBDF0xOM-PlP46wE8x9D412lFm5WyaEIPSrPOOaWwny-SjJY. for .sina.com.cn/>, <Cookie SUB=_2A251N1SUDeTxGeVG6lcX9ijJyj6IHXVWRcFcrDV_PUNbm9ANLU3fkW8TgsgYNcJIhGs7MK3rk72XiOEqaw.. for .sina.com.cn/>, <Cookie SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5Haujr-W3aFpl1sG5HoUay5NHD95Q01h2fSoqcSK2EWs4Dqcjdi--Xi-iWiK.pi--NiKLsi-z0i--ci-zpiKnN for .sina.com.cn/>, <Cookie sso_info=v02m6alo5qztKWRk5yljpOQpZCToKWRk5iljoOgpZCjnLOOg4S1jaOYto2ThLKJp5WpmYO0s46DhLWNo5i2jZOEsg== for .sina.com.cn/>"
                # p = re.compile('\<LWPCookieJar\[\<Cookie (.*?) for .weibo.com\/\>\]\>')
                # cookiess = re.findall(p, cookie)
                # cookiess = (cookiejar.split('=') for cookiejar in cookiess)
                # print "cookies:",cookiess
                # for each in dict(cookiess):
                #     print "each:",each
                #self.cookies = dict(cookie)
                # with open(self.cookie_file, 'wb+') as f:
            #     for cookie in cookie_jar:
            #         f.write(str(cookie) + '\n')

    def parse(self, response):
        #print "response:",response.body
        if response.body.find('feedBackUrlCallBack') != -1:
            print response.body
            url = 'http://weibo.cn/'
            print "self.cookies:",self.cookies
            yield Request(url=url, callback=self.parseFollow,cookies=self.cookies)
        else:
            print('login failed: errno=%s, reason=%s')

    # def start_requests(self):
    #     url = 'http://weibo.com/u/3815666512/home?wvr=5'
    #     yield Request(url=url, callback=self.parseFollow)


    def parseFollow(self,response):
        #print response.body
        selector = Selector(response)
        #followUrl = selector.xpath("//div[@class='WB_innerwrap']/ul/li[1]/a/@href").extract()

        followurl = selector.xpath("//div[@class='u']/div[@class='tip2']/a[2]/@href").extract()
        if followurl:
            follow = followurl[0]
            print "followUrl:",follow
            #domian = "http://weibo.cn/"
            yield Request(url=self.domian+follow, callback=self.parsePerson)


    # �������������ڽ�������������ҳ,���������Ļص���������request������󣬷���response��Ӧ�����ô˺���
    def parsePerson(self, response):
        # ���ݴ�ŵĶ���
        infoItem = InformationItem()
        tweetsItem = TweetsItem()
        # ѡ���������ڻ�ȡ��ҳ�еı�ǩԪ�غ�ֵ,response��Σ�����ֱ��ʹ��selector
        selector = Selector(response)

        # ��ע���б���֪��Ϊʲô��Ҫ��������ʱ�������
        # http://weibo.cn/attention/remark?uid=1781379945&rl=1&vt=4
        Followlist = selector.xpath('//tr/td[2]/a[2]/@href').extract()

        if len(Followlist)>0:
            print "follow numbers:", len(Followlist)
            # ����ÿ����ע�˶���
            for everyone in Followlist:
                # ��ȡÿ����ע��url���й��û�ID�Ĳ���
                followId = everyone[(everyone.index("uid") + 4):(everyone.index("rl") - 1)]
                print "followId:",followId

                # ��ע�˵���ҳ�� �����û�ID���������
                followUrl = "http://weibo.cn/%s/profile" % followId
                print "followId:", followId, "------followUrl:", followUrl
                # ��ȡ������Ҫ����Ϣ�������ǻ�ȡԭ����ͼ�����һ���ڵ�΢�������������ͨ��F12��request�л�֪
                correctUrl = "http://weibo.cn/%s/profile?hasori=1&haspic=1&starttime=20161020&endtime=20161120&advancedfilter=1&page=1" % followId

                if followId not in self.Follow_ID:
                    # ��ÿ����ȡ�Ĺ�ע��ID���½�������--�ҵ����ǣ������ע���˺ܶ࣬���Ҳ���Ҫ�����޾�
                    # ���·���request���󣬴���һЩ�����������ûص�����,meta��Ҫ���ڴ�������һЩ��Ϣ
                    yield Request(url=followUrl, meta={"item": infoItem, "ID": followId, "URL": followUrl},
                                  callback=self.parseForFollow)
                    # �Ե�ǰ��ȡ�Ĺ�ע��ӵ�е�΢�����������ݣ�����һ���ÿ����һ�����ˣ���Ȼ̫����
                    yield Request(url=correctUrl, meta={"item": tweetsItem, "ID": followId},
                                  callback=self.parseForCorrect)
                    self.Follow_ID.append(followId)

                # �ж��Ƿ�����һҳ���������һҳ��ʹ��request�������󣬵��õ�ǰ����Ϊ�ص��������е����Ƶݹ�
        nextUrl = selector.xpath("//div[@class='pa']/form/div/a/@href").extract()
        if nextUrl:
            nextUrl = nextUrl[0]
            yield Request(url=self.domian + nextUrl, callback=self.parsePerson)

    # �����ȡ���Ĺ�ע����ҳ
    def parseForFollow(self, response):
        # ����ǰ��ע�ߵĻ�����Ϣ����item��
        infoItem = response.meta['item']
        infoItem['_id'] = response.meta['ID']
        infoItem['Home_Page'] = response.meta['URL']

        selector = Selector(response)
        info = selector.xpath("//div[@class='ut']/span[@class='ctt']/text()").extract()
        # join ����ͨ��ָ���ַ�����������Ԫ�غ����ɵ����ַ���
        newInfo = '/'.join(info)
        try:
            # exceptions.TypeError: expected string or buffer ??
            infoItem['Info'] = newInfo
        except:
            pass

        # tip2�и���Ϣ,Num_Tweet Num_Follows Num_Fans
        num_tweets = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/span/text()').extract()  # ΢����
        num_follows = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/a[1]/text()').extract()  # ��ע��
        num_fans = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/a[2]/text()').extract()  # ��˿��
        # ��ȡ[ ]֮�������
        if num_tweets:
            # ֮���Դ�[0]����Ϊ������ͬ�ı�ǩ
            infoItem['Num_Tweets'] = (num_tweets[0])[(num_tweets[0].index('[') + 1):num_tweets[0].index(']')]
        if num_follows:
            infoItem['Num_Follows'] = (num_follows[0])[(num_follows[0].index('[') + 1):num_follows[0].index(']')]
        if num_fans:
            infoItem['Num_Fans'] = (num_fans[0])[(num_fans[0].index('[') + 1):num_fans[0].index(']')]
        yield infoItem



    # ��ȡ��ע��΢����Ϣ
    def parseForCorrect(self, response):
        # ����ǰ��ע�ߵĻ�����Ϣ����item��
        tweetsItem = response.meta["item"]
        tweetsItem["_id"] = response.meta["ID"]

        selector = Selector(response)
        Tweets = selector.xpath('//div[@class="c"]')
        if Tweets:
            # ��parse1���в�ͬ��ͨ��forѭ��Ѱ����Ҫ�Ķ���
            for everytweet in Tweets:
                # ��ȡÿ��΢��Ψһid��ʶ
                mark_id = everytweet.xpath('@id').extract()
                print mark_id
                # ��id��Ϊ�յ�ʱ����뵽΢����ȡ�б�,ȥ�ز����������Ѿ���ȡ����΢�����ٻ�ȡ
                if mark_id and mark_id not in self.Tweets_ID:
                    content = everytweet.xpath('div/span[@class="ctt"]/text()').extract()
                    timeloc = everytweet.xpath('div[2]/span[@class="ct"]/text()').extract()
                    #picurl = everytweet.xpath('div[2]/a[2]/img/@src').extract()
                    picurl = everytweet.xpath('div[2]/a[2]/@href').extract()
                    like = everytweet.xpath('div[2]/a[3]/text()').extract()
                    transfer = everytweet.xpath('div[2]/a[4]/text()').extract()
                    comment = everytweet.xpath('div[2]/a[5]/text()').extract()
                    if content:
                        #print content
                        tweetsItem['Content'] = content[0]
                    if picurl:
                        #print picurl
                        tweetsItem['Pic_Url'] = picurl[0]
                    if comment:
                        #print comment
                        #tweetsItem['Num_Comment'] = (comment[0])[(comment[0].index('[') + 1):comment[0].index(']')]
                        tweetsItem['Num_Comment'] = comment[0]
                    if like:
                        #print like
                        #tweetsItem['Num_Like'] = (like[0])[(like[0].index('[') + 1):like[0].index(']')]
                        tweetsItem['Num_Like'] = like[0]
                    if transfer:
                        #print transfer
                        #tweetsItem['NUm_Transfer'] = (transfer[0])[(transfer[0].index('[') + 1):transfer[0].index(']')]
                        tweetsItem['NUm_Transfer'] = transfer[0]
                    if timeloc:
                        tweetsItem['Time_Location'] = timeloc[0]


        yield tweetsItem
        nextLink = selector.xpath('//div[@class="pa"]/form/div/a/@href').extract()
        if nextLink:
            nextLink = nextLink[0]
            print nextLink
            yield Request(self.domian + nextLink, callback=self.parseForCorrect,meta={"item":tweetsItem,"ID":tweetsItem["_id"]})


