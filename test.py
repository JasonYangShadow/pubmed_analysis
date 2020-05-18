import unittest
from mongo import Mongo
from textprocess import TextProcess

class Test(unittest.TestCase):

    @unittest.skip('skip')
    def testMongo(self):
        mongo = Mongo('config.ini')
        data = [{'name':'1'},{'name':'2'}]
        mongo.insert(data, 'test')

    #@unittest.skip('skip')
    def testText(self):
        tp = TextProcess()
        tp.readfile('pubmed_result.txt')
