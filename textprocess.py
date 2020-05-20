import json
from rake_nltk import Rake
from geotext import GeoText
import pycountry
import re
import universities
from log import *
from mongo import Mongo

country_map = {'UK':'GB', 'USA':'US', 'NY':'US', 'U.S.A':'US','México':'MX','Republic of Korea':'KR', 'Korea':'KR', 'U.S.':'US', 'Ohio':'US','Australian':'AU','IOWA':'US','Fukushima':'JP','Tohoku':'JP','Tokushima':'JP','Sao Paulo':'BR','Karnataka':'IN','Bosnia & Herzegovina':'BA','Ningbo Yinzhou':'CN'}

class TextProcess:
    def __init__(self,config_path):
        self.uni = universities.API()
        self.reg = r".*(\s+\w+\s+University).*"
        self.config = Config(config_path)
        self.mongo = Mongo(config_path)
        self.collection = 'data'
        self.minimum_length = int(self.config.getValueDefault('Data','MINLENGTH',400))
        self.max_items = int(self.config.getValue('Data','ITEMS'))
        self.start = int(self.config.getValue('Data','START'))
        if not self.max_items:
            raise Exception('Please set max_items inside config.ini')

    def readblock(self,f):
        ret = []
        line = f.readline()
        #if encounterring empty line, skip it
        while not line.strip():
            line = f.readline()
        while line.strip():
            ret.append(line)
            line = f.readline()
        if not ret:
            return None
        return ''.join(ret)

    def findcountry(self, aff):
        places = GeoText(aff)
        countries = []
        #match country firstly
        for item in places.country_mentions:
            countries.append(item)
        #match customized country_map
        for key, val in country_map.items():
            if key in aff and val not in countries:
                countries.append(val)
        #match universities
        m = re.match(self.reg, aff) 
        if m is not None:
            for group in m.groups():
                group = group.strip()
                for university in self.uni.search(name = group):
                    if university.country_code not in countries:
                        countries.append(university.country_code)
        return countries
    

    def readfile(self, path):
        with open(path) as f:
            n = self.start
            rake = Rake()
            while True:
                line = self.readblock(f)
                #check new record starts
                if line.startswith('%d. ' % n):
                    data = {}
                    data['seqid'] = n
                    #get time
                    data['time'] = line.split('.')[2].split(';')[0].strip()
                    #get title
                    data['title'] = self.readblock(f).replace('\n',' ').strip()
                    #get author
                    data['author'] = self.readblock(f).replace('\n',' ').strip()
                    #detect affiliation
                    line = self.readblock(f)
                    if line.startswith('Author information:'):
                        data['affiliation'] = line.replace('\n',' ').strip()
                        countries = self.findcountry(data['affiliation'])
                        if countries:
                            data['country'] = countries
                        else:
                            #could not find country info, skip it
                            LOGGER.info('could not find country info: of paper id: [%d], [%s]' % (int(n), data['affiliation']))
                            n += 1
                            continue
                        line = self.readblock(f)
                    #abstract
                    while line.startswith('Comment'):
                        line = self.readblock(f)
                    #no abstract
                    if line.find('DOI:') >=0 or line.find('PMID:') >= 0 or line.find('PMCID:') >= 0:
                        data['DOI'] = line.replace('\n',' ').rstrip('[Indexed for MEDLINE]').strip()
                        #skip this record as it does not have abstract
                        n += 1
                        continue
                    else:
                        data['abstract'] = line.replace('\n',' ').strip()
                        #abstract length is too short
                        if len(data['abstract']) < self.minimum_length:
                            n += 1
                            continue
                        line = self.readblock(f)
                        #skip all other elements until encountering DOI
                        while line.find('DOI:') == -1 and line.find('PMID:') == -1 and line.find('PMCID:') == -1:
                            line = self.readblock(f)
                        data['DOI'] = line.replace('\n',' ').rstrip('[Indexed for MEDLINE]').strip()
                        n += 1

                        #here data is ready for processing
                        rake.extract_keywords_from_text(data['abstract'])
                        words = rake.get_ranked_phrases()
                        data['keywords'] = words[:2]

                        LOGGER.debug(data)
                        LOGGER.info('starts saving id: %d data into mongodb' % int(n-1))
                        self.mongo.insert([data], self.collection)
                #record ends
                if n > self.max_items:
                    break
