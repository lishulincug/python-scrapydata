# coding=GBK
import scrapy
from scrapy.spider import Spider
from dmoz.items import InformationItem,TweetsItem
from scrapy.selector import Selector
from scrapy.http import Request

class WeiboSpider(Spider):
    name = "dmoz"
    #������Զ�д�����û���Ŀǰ�õ������Լ����˻�
    start_url = ["http://weibo.cn/3745970722/follow"]
    url = "http://weibo.cn"
    # ��¼������΢��ID
    scrawl_ID = set(start_url)
    #�Ѿ���ȡ���û�ID�����б���
    Follow_ID = []
    #�Ѿ���ȡ��΢��ID
    Tweets_ID = []

    #�ʼ������
    def start_requests(self):
        while True:
            ID = self.scrawl_ID.pop()
            self.Follow_ID.append(ID)  # ������������
            ID = str(ID)
            follows = []
            followsItems = InformationItem()
            #followsItems["_id"] = ID
            #followsItems["follows"] = follows
            url_information0 = "http://weibo.cn/attgroup/opening?uid=%s" % ID
            url_follows = "http://weibo.cn/%s/follow" % ID
            url_tweets = "http://weibo.cn/%s/profile?filter=1&page=1" % ID
            yield Request(url=url_follows, meta={"item": followsItems, "result": follows},
                          callback=self.parseForFollow)  # ȥ����ע��
            yield Request(url=url_information0, meta={"ID": ID}, callback=self.parse)  # ȥ��������Ϣ
            yield Request(url=url_tweets, meta={"ID": ID}, callback=self.parseForCorrect)  # ȥ��΢��

    #�������������ڽ�������������ҳ,���������Ļص���������request������󣬷���response��Ӧ�����ô˺���
    def parse(self,response):
        #���ݴ�ŵĶ���
        infoItem = InformationItem()
        tweetsItem = TweetsItem()
        #ѡ���������ڻ�ȡ��ҳ�еı�ǩԪ�غ�ֵ,response��Σ�����ֱ��ʹ��selector
        selector = Selector(response)
        print(selector)

        #��ע���б���֪��Ϊʲô��Ҫ��������ʱ�������
        Followlist = selector.xpath('//tr/td[2]/a[2]/@href').extract()
        print "��ע������:",len(Followlist)

        #����ÿ����ע�˶���
        for everyone in Followlist:
            #��ȡÿ����ע��url���й��û�ID�Ĳ���
            followId = everyone[(everyone.index("uid")+4):(everyone.index("rl")-1)]
            #��ע�˵���ҳ�� �����û�ID���������
            followUrl = "http://weibo.cn/%s/profile" % followId
            print "��ע��ID:",followId,"------��ע�˵���ҳ:",followUrl
            #��ȡ������Ҫ����Ϣ�������ǻ�ȡԭ����ͼ�����һ���ڵ�΢�������������ͨ��F12��request�л�֪
            correctUrl = "http://weibo.cn/%s/profile?hasori=1&haspic=1&starttime=20151120&endtime=20161120&advancedfilter=1&page=1" % followId

            if followId not in self.Follow_ID:
                # ��ÿ����ȡ�Ĺ�ע��ID���½�������--�ҵ����ǣ������ע���˺ܶ࣬���Ҳ���Ҫ�����޾�
                #���·���request���󣬴���һЩ�����������ûص�����,meta��Ҫ���ڴ�������һЩ��Ϣ
                yield Request(url=followUrl,meta={"item":infoItem, "ID": followId, "URL": followUrl},callback=self.parseForFollow)
                #�Ե�ǰ��ȡ�Ĺ�ע��ӵ�е�΢�����������ݣ�����һ���ÿ����һ�����ˣ���Ȼ̫����
                yield Request(url=correctUrl,meta={"item":tweetsItem,"ID":followId},callback=self.parseForCorrect)
                self.Follow_ID.append(followId)

            # �ж��Ƿ�����һҳ���������һҳ��ʹ��request�������󣬵��õ�ǰ����Ϊ�ص��������е����Ƶݹ�
        nextUrl = selector.xpath("//div[@class='pa']/form/div/a/@href").extract()
        if nextUrl:
            yield Request(url=self.url + nextUrl, callback=self.parse)
        else:
            print self.Follow_ID

    #�����ȡ���Ĺ�ע����ҳ
    def parseForFollow(self,response):
        #����ǰ��ע�ߵĻ�����Ϣ����item��
        infoItem = response.meta['item']
        infoItem['_id'] = response.meta['ID']
        infoItem['Home_Page'] = response.meta['URL']

        selector = Selector(response)
        info = selector.xpath("//div[@class='ut']/span[@class='ctt']/text()").extract()
        #join ����ͨ��ָ���ַ�����������Ԫ�غ����ɵ����ַ���
        newInfo = '/'.join(info)
        try:
            # exceptions.TypeError: expected string or buffer ??
            infoItem['Info'] = newInfo
        except:
            pass

        #tip2�и���Ϣ,Num_Tweet Num_Follows Num_Fans
        num_tweets = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/span/text()').extract()  # ΢����
        num_follows = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/a[1]/text()').extract()  # ��ע��
        num_fans = selector.xpath('body/div[@class="u"]/div[@class="tip2"]/a[2]/text()').extract()  # ��˿��
        #��ȡ[ ]֮�������
        if num_tweets:
            #֮���Դ�[0]����Ϊ������ͬ�ı�ǩ
            infoItem['Num_Tweets'] = (num_tweets[0])[(num_tweets[0].index('[')+1):num_tweets[0].index(']')]
        if num_follows:
            infoItem['Num_Follows'] = (num_follows[0])[(num_follows[0].index('[') + 1):num_follows[0].index(']')]
        if num_fans:
            infoItem['Num_Fans'] = (num_fans[0])[(num_fans[0].index('[') + 1):num_fans[0].index(']')]
        yield infoItem



    #��ȡ��ע��΢����Ϣ
    def parseForCorrect(self,response):
        # ����ǰ��ע�ߵĻ�����Ϣ����item��
        tweetsItem = response.meta["Item"]
        tweetsItem["_id"] = response.meta["ID"]

        selector = Selector(response)
        Tweets = selector.xpath('//div[@class="c"]')
        # ��parse1���в�ͬ��ͨ��forѭ��Ѱ����Ҫ�Ķ���
        for everytweet in Tweets:
            # ��ȡÿ��΢��Ψһid��ʶ
            mark_id = everytweet.xpath('@id').extract()
            print mark_id
            # ��id��Ϊ�յ�ʱ����뵽΢����ȡ�б�,ȥ�ز����������Ѿ���ȡ����΢�����ٻ�ȡ
            if mark_id and mark_id not in self.TweetsID:
                content = everytweet.xpath('div/span[@class="ctt"]/text()').extract()
                timeloc = everytweet.xpath('div[2]/span[@class="ct"]/text()').extract()
                picurl = everytweet.xpath('div[2]/a[2]/img/@src').extract()
                like = everytweet.xpath('div[2]/a[3]/text()').extract()
                transfer = everytweet.xpath('div[2]/a[4]/text()').extract()
                comment = everytweet.xpath('div[2]/a[5]/text()').extract()
                if content:
                    tweetsItem['Content'] = content[0]
                if picurl:
                    tweetsItem['Pic_Url'] = picurl[0]
                if comment:
                    tweetsItem['Num_Comment'] = (comment[0])[(comment[0].index('[')+1),comment[0].index(']')]
                if like:
                    tweetsItem['Num_Like'] = (like[0])[(like[0].index('[') + 1), like[0].index(']')]
                if transfer:
                    tweetsItem['NUm_Transfer'] = (transfer[0])[(transfer[0].index('[') + 1), transfer[0].index(']')]

        nextLink = selector.xpath('//div[@class="pa"]/form/div/a/@href').extract()
        if nextLink:
            nextLink = nextLink[0]
            print nextLink
            yield Request(self.url+nextLink, callback=self.parseForCorrect)






















