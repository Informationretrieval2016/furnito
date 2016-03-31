from url_pool import URL_Pool
from url_manager import URL_Manager
from crawler import Crawler
import config
import time

#init
processed = []
processing = []
um = URL_Manager(processed, processing)
crawler = Crawler()
#add start url into um
processing = um.url_add(config.base_url)

while len(processing) > 0:
    try:
        # crawl first url in processing list
        new_urls, crawled_url = crawler.get_result(processing[0])
        print "processing: " + str(processing[0])
        #remove crawled url from processing
        processing = um.url_add(new_urls)
        processing = um.url_remove(crawled_url)
        processed = um.url_history(crawled_url)
        print "%d urls need to crawl" % len(processing)
        print "%d urls has crawled" % len(processed)
        time.sleep(config.sleep_time)
    except:
        pass
