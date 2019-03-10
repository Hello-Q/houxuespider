import scrapy
import json
import logging

def city_INFO():
    """
    从厚学网的城市json文件中提取城市以及域名信息,
    组合成字典
    :return:包含城市名称以及url的字典
    """

    # 读取json文件
    with open('/home/zhangyanqing/work/Spider/houxuewang/houxuewang/spiders/city_info.json', 'r') as f:
        city_file = json.load(f)

    city_names_urls = []

    for city_info in city_file:
        city_name_url = {}
        name = city_info['AreaName']
        url = r'https://www.houxue.com/'+city_info['Domain']+'/xuexiao-wentiyishu6.html'
        city_name_url['name'] = name
        city_name_url['url'] = url
        city_names_urls.append(city_name_url)
    return city_names_urls


city_urls = [url['url'] for url in city_INFO()][:2]
city_names = [name['name'] for name in city_INFO()]


class HouxueSpider(scrapy.Spider):
    name = 'houxue'
    start_urls = city_urls
    # 城市数
    city_num = 0
    def parse(self, response):
        """
        将所有城市的url处理加上一级分类并交给下级处理
        :param response:
        :return: 返回包含城市以及一级分类的url
        """
        """此部分请求url以及根据url得到的城市信息,每次被调用都会更新"""
        print('开始提取城市+一级分类url')

        self.city_num += 1
        # 本次请求城市的url
        city_url = response.url
        # 本次请求城市url的索引值
        index = city_urls.index(city_url)
        # 本次请求城市的名字
        city_name = city_names[index]
        """以下部分是从的得的页面中解析出的信息, 注意要yield返回"""
        # 城市+一级分类url列表(书画、音乐、舞蹈、棋类、球类、爱好)
        classify_urls = response.xpath('//div[@class="row clear"][1]/ul/li[not(@class)]/a/@href').extract()[:2]  # 上线前取消切片
        # 一级分类的名称列表

        one_lv_class_names = response.xpath('//div[@class="row clear"][1]/ul/li[not(@class)]/a/text()').extract()[:2]  # 上线前取消切片
        # 将 一级分类的名字和url合并成字典
        one_lv_class_dicts = dict(zip(one_lv_class_names, classify_urls))
        # 返回城市+一级分类信息
        for one_lv_class_name, one_lv_class_url in one_lv_class_dicts.items():
            yield scrapy.Request(one_lv_class_url, callback=self.two_lv_class, dont_filter=True,
                                 meta={
                                     'city_name': city_name,
                                     'one_lv_class_name': one_lv_class_name
                                    })

    def two_lv_class(self, response):
        pass
        """
        提取城市一级分类页面中的二级分类url并交给下级处理
        :param response:
        :return:城市+二级分类的url
        """


        # 上级(parse)解析传来的城市名称
        city_name = response.meta['city_name']
        # 上级(parse)解析传来的一级分类名称
        one_lv_class_name = response.meta['one_lv_class_name']

        # 城市+二级分类的url列表
        two_lv_class_urls = response.xpath('//div[@class="row clear"][1]/ul/li[not(@class)]/a/@href').extract()[:2]  # 上线前取消切片
        # 二级分类名称
        two_lv_class_names = response.xpath('//div[@class="row clear"][1]/ul/li[not(@class)]/a/text()').extract()
        # 将二级分类和url合并成字典
        two_lv_class_dict = dict(zip(two_lv_class_names, two_lv_class_urls))

        for two_lv_class_name, two_lv_class_url in two_lv_class_dict.items():

            yield scrapy.Request(two_lv_class_url, callback=self.district, dont_filter=False,
                                 meta={
                                     'city_name': city_name,
                                     'one_lv_class_name': one_lv_class_name,
                                     'two_lv_class_name': two_lv_class_name,
                                 })

    def district(self, response):
        """
        提取行政区+二级分类的url交给下级处理
        :param response:
        :return:行政区+二级分类的url
        """
        print('开始提取行政区+二级分类url')
        # 上级(parse)解析传来的城市名称
        city_name = response.meta['city_name']
        # 上级(parse)解析传来的一级分类名称
        one_lv_class_name = response.meta['one_lv_class_name']
        # 二级分类名称
        two_lv_class_name = response.meta['two_lv_class_name']

        # 行政区名称
        district_names = response.xpath('//div[@class="row clear"][2]/ul/li[not(@class)]/a/text()').extract()
        # 行政区+二级分类url
        district_urls = response.xpath('//div[@class="row clear"][2]/ul/li[not(@class)]/a/@href').extract()

        # 将行政区名称和url合并成字典
        district_dict = dict(zip(district_names, district_urls))

        for district_name, district_url in district_dict.items():
            print(city_name, one_lv_class_name, two_lv_class_name, district_name, district_url)


