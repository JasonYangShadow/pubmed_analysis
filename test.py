import unittest
from mongo import Mongo
from textprocess import TextProcess
from wordcloud import WordCloud, STOPWORDS
import numpy as np
from PIL import Image

class Test(unittest.TestCase):

    @unittest.skip('skip')
    def testMongo(self):
        mongo = Mongo('config.ini')
        data = [{'name':'1'},{'name':'2'}]
        mongo.insert(data, 'test')

    @unittest.skip('skip')
    def testText(self):
        tp = TextProcess('config.ini')
        tp.readfile('pubmed_result.txt')

    @unittest.skip('skip')
    def testTime(self):
        mongo = Mongo('config.ini')
        data = mongo.find('data')
        dic = {}
        for line in data:
            if 'time' not in line:
                continue
            times = line['time'].split()
            for time in times:
                if time.startswith('20'):
                    time = time.split(':')[0]
                    time = time.split('-')[0]
                    if time not in dic:
                        dic[time] = 1
                    else:
                        dic[time] +=1
                    break
        print(dic)


    @unittest.skip('skip')
    def testFindCountry(self):
        mongo = Mongo('config.ini')
        data = mongo.find('data')
        country_map = {}
        for line in data:
            if 'country' not in line:
                continue
            for country in line['country']:
                if country not in country_map:
                    country_map[country] = 1
                else:
                    country_map[country] += 1
        for k in sorted(country_map, key = country_map.get, reverse=True):
            print(k,',',country_map[k])

    @unittest.skip('skip')
    def testFindKeywords(self):
        mongo = Mongo('config.ini')
        data = mongo.find('data')
        keywords = []
        for line in data:
            if 'keywords' not in line:
                continue
            for keyword in line['keywords']:
                keywords.append(keyword)

        text = ','.join(keywords)

        stopwords = set(STOPWORDS)
        stopwords.add("said")

        wc = WordCloud(background_color="white", max_words=2000, stopwords=stopwords, min_font_size=10, width = 800, height = 800)
        wc.generate(text)
        wc.to_file("cloud.png")

    #@unittest.skip('skip')
    def testGenWord(self):
        mongo = Mongo('config.ini')
        data = mongo.find('data')
        keywords = []
        for line in data:
            if 'keywords' not in line:
                continue
            if 'country' not in line:
                continue
            if 'CN' in line['country']:
                for keyword in line['keywords']:
                    keywords.append(keyword)
        text = ','.join(keywords)

        stopwords = set(STOPWORDS)
        stopwords.add("said")

        mask = np.array(Image.open('china.png'))
        wc = WordCloud(background_color="white", max_words=2000, stopwords=stopwords, min_font_size=10, mask=mask)
        wc.generate(text)
        wc.to_file("word_cn.png")
