from __init__ import *
from furniture import Furniture

class Crawler:
    def __init__(self):
        self.base_url = config.base_url
        self.depth = config.depth
    
    def get_result(self, url):
        '''
        @usage: construct a furniture instance and write into local storage
        @arg: url, current furniture url want to crawl
        '''
        name, price, details, new_urls = self.get_furniture(url)
        reviews = self.get_reviews(url)
        furniture = Furniture(name, price, details, reviews, url)
        #once crawled current furniture, remove url from url pool incase of crawl twice 
        print furniture.name                
        #maybe write to local storage
        #write_result() to be defined
        #return new urls, url, remove url from url_pool, add new urls
        return new_urls, url

            

    def get_furniture(self, url):
        '''
        @usage: get data from one furniture base on given url
        @arg: url or current furniture`
        @return: list of furniture name, furniture price, description,new_urls to be crawled
        '''
        furniture_page = requests.get(url)
        tree = html.fromstring(furniture_page.text)
        #extract tags
        name = tree.xpath('//span[@itemprop="name"]/h1/text()')[0]
        price = tree.xpath('//span[@itemprop="price"]/text()')[0]
        description = tree.xpath('//span[@itemprop="description"]/text()')[0]
        description_points = tree.xpath('//span[@itemprop="description"]/ul/li/text()')
        #as description points is a list, split list and add to description_main
        temp_str = ''
        for description_point in description_points:
            temp_str += description_point
        #add temp to description
        description += temp_str
        temp_str = ''
        #extract features
        features = tree.xpath('//tbody/tr/td/text()')
        features = com.clean_feature(features)
        for feature in features:
            temp_str += feature
        description += temp_str
        #extract new urls
        new_urls = tree.xpath('//div[@id="rrVertRecsLarge"]/div/div/ul/li/a/@href')
         
        return name, price, description, list(set(new_urls))

    def get_reviews(self, url):
        '''
        @usage: get reviews from one furniture given url
        @arg: url of current furniture
        @return: list of reviews for a certain furniture
        '''
        reviews = []
        #now have url from furniture page, extract url of all reviews of current furniture
        furniture_page = requests.get(url)
        tree = html.fromstring(furniture_page.text)
        #extract url of all reviews
        try:
            reviewpage_url = tree.xpath('//span[@class="overall-msg"]/a/@href')[0]
            review_page = requests.get(reviewpage_url)
            tree = html.fromstring(review_page.text)
        #extract all reviews, first get number of review pages
            try:
                page_num = tree.xpath('//a[@class="firstChild"][last()]/text()')[0]
            except IndexError as e:
                page_num = 1
            if page_num == 1:
                reviews = self.extract_reviews(reviewpage_url)
            else:
                reviews = self.extract_reviews(reviewpage_url, multi_page = True, max_page = int(page_num))
        except IndexError as e:
            reviews = ['failed to get review']
        return reviews

    def extract_reviews(self, url, multi_page = False, max_page = None):
        '''
        @usage: get reviews from current url
        @arg: url, url of review page
        @arg: multi_page, indicate there are pages of reviews, default false
        @return list of review in current page
        '''
        #get page
        review_page = requests.get(url)
        tree = html.fromstring(review_page.text)
        #init list to store reviews
        #crawl first page reviews
        reviews = tree.xpath('//div[starts-with(@id, "reviewText")]/p/text()')
        reviews = com.clean_reviews(reviews)
        if multi_page:
            #multiple page situation
            for page_num in range(2, max_page + 1):
                #get new page url
                url = tree.xpath('//a[@id="pReviewNext"]/@href')[0]
                review_page = requests.get(url)
                tree = html.fromstring(review_page.text)
                current_reviews = tree.xpath('//div[starts-with(@id, "reviewText")]/p/text()')
                current_reviews = com.clean_reviews(current_reviews)
                reviews = reviews + current_reviews
        return reviews
            



