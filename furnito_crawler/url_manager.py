class URL_Manager:
    def __init__(self, processed, processing):
        #url finished crawl
        self.processed = processed
        #url need to crawl
        self.processing = processing
    
    def get_processed(self):
        '''
        @usage: get url that has been crawled
        return list of url has been crawled
        '''
        return self.processed

    def get_processing(self):
        '''
        @usage: get url that need to be crawled
        @return list of url need to crawl
        '''
        return self.processing

    def url_add(self, url_list):
        '''
        @usage: discover furniture url and push into url pool
        @arg: list of url discovered from one furniture page
        '''
        #remove dulpilicate urls that not appear in both current list and history list
        if isinstance(url_list, list):
            for url in url_list:
                if url not in self.processing and url not in self.processed:
                    self.processing.extend(url_list)
        else:
            self.processing.append(url_list)
        return self.processing

    def url_remove(self, url):
        '''
        @usage: remove url that data has been crawled, call before url_history
        @arg: url, str, current url that has finished crawl
        '''
        self.processing.remove(url)
        return self.processing
    def url_history(self, url):
        '''
        @usage: store history url that has been removed from url_pool, call this function after url_remove
        @arg: url, str, removed url
        '''
        self.processed.append(url)
        return self.processed
