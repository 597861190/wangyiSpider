import scrapy
from scrapy import cmdline
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy_redis.spiders import RedisCrawlSpider, RedisSpider
from selenium.webdriver.chrome.service import Service

from WangSpider.items import WangspiderItem


class WangSpider(RedisSpider):
    name = "wang"
    allowed_domains = ["163.com"]
    # start_urls = ["http://news.163.com/"]
    redis_key = "wangyiurl"
    # lpush wangyiurl "https://news.163.com/"
    # start_urls.append("http://news.163.com")

    def __init__(self):
        super(WangSpider, self).__init__()
        options = webdriver.ChromeOptions()
        options.add_argument("--window-position=0,0") #chrome启动初始位置
        options.add_argument("--window-size=1080,800") #chrome启动初始大小
        options.add_argument('--ignore-certificate-errors')
        # 忽略 Bluetooth: bluetooth_adapter_winrt.cc:1075 Getting Default Adapter failed. 错误
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 忽略 DevTools listening on ws://127.0.0.1... 提示
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        services = Service(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe")
        self.bro = webdriver.Chrome(service=services, options=options)

    def parse(self, response, **kwargs):
        lis = response.xpath("//div[@class='ns_area list']/ul/li")
        li_list = []
        indexs = [1, 2, 4, 5]
        # indexs = [2]
        for index in indexs:
            li_list.append(lis[index])
        #获取四个板块的文字标题和url
        for li in li_list:
            url = li.xpath("./a/@href").extract_first()
            title = li.xpath("./a/text()").extract_first()
            #对每一个板块对应的url发起请求,获取页面数据（标题，缩略图，关键字，发布时间,url）
            print(title)
            print(url)
            yield scrapy.Request(url, callback=self.parseSecond, meta={"title": title})


    def parseSecond(self, response):
        div_list = response.xpath('//div[@class="data_row news_article clearfix "]')
        print(len(div_list))
        for div in div_list:
            head = div.xpath(".//div[@class='news_title']/h3/a/text()").extract_first()
            url = div.xpath(".//div[@class='news_title']/h3/a/@href").extract_first()
            imgUrl = div.xpath("./a/img/@src").extract_first()
            tag = div.xpath(".//div[@class='news_tag']//text()").extract()
            tags = []
            for t in tag:
                t = t.strip()
                tags.append(t)
            tag = "".join(tags)
            #获取Meta传递过来的数据值title
            title = response.meta["title"]

            #实例化Item对象, 将解析到的数据值存储到item对象中
            item = WangspiderItem()
            item['head'] = head
            item['url'] = url
            item['imgUrl'] = imgUrl
            item['tag'] = tag
            item['title'] = title
            #对url发起请求,获取对应页面中存储的新闻内容数据
            yield scrapy.Request(url, callback=self.getContent, meta={"item":item})


    def getContent(self, response):
        #获取传递过来的item
        item = response.meta["item"]

        #解析当前页面中存储的新闻数据
        content_list = response.xpath('//div[@class="post_body"]/p/text()').extract()
        content = "".join(content_list)
        item['content'] = content
        yield item

    def closed(self, spider):
        self.bro.quit()


if __name__ == '__main__':
    cmdline.execute("scrapy crawl wang".split())
