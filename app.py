# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Resource, Api
from flask_caching import Cache
from news import NewsSpider
from galerie import GalerieSpider
import scrapy.crawler as crawler
from multiprocessing import Process, Queue
from twisted.internet import reactor

app = Flask(__name__)
api = Api(app)
cache = Cache(app, config={'CACHE_TYPE': 'SIMPLE'})
# cache = Cache(app, config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_KEY_PREFIX': 'fcache',
#     'CACHE_REDIS_HOST': 'localhost',
#     'CACHE_REDIS_PORT': '6379',
#     'CACHE_REDIS_URL': 'redis://localhost:6379'
#     })

class News(Resource):
    @cache.cached(timeout=600)
    def get(self):
        data = []
        def f(q):
            try:
                runner = crawler.CrawlerRunner()
                deferred = runner.crawl(NewsSpider)
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(NewsSpider.getNews())
            except Exception as e:
                q.put(e)

        q = Queue()
        p = Process(target=f, args=(q,))
        p.start()
        result = q.get()
        p.join()
        return {'news': result}

        # runner = CrawlerRunner()
        # d = runner.crawl(NewsSpider)
        # d.addBoth(lambda _: reactor.stop())
        # reactor.run()
        # process = CrawlerProcess({
        #     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
        # })
        # process.crawl(NewsSpider)
        # process.start()



class Galerie(Resource):
    @cache.cached(timeout=600)
    def get(self):
        data = []
        def f(q):
            try:
                runner = crawler.CrawlerRunner()
                deferred = runner.crawl(GalerieSpider)
                deferred.addBoth(lambda _: reactor.stop())
                reactor.run()
                q.put(GalerieSpider.getNews())
            except Exception as e:
                q.put(e)

        q = Queue()
        p = Process(target=f, args=(q,))
        p.start()
        result = q.get()
        p.join()
        return {'news': result}



api.add_resource(News, '/news')
api.add_resource(Galerie, '/galerie')

if __name__ == '__main__':
    app.run(port=5000)
