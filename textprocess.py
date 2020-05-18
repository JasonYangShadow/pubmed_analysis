import json
from rake_nltk import Rake

class TextProcess:

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

    def readfile(self, path):
        with open(path) as f:
            n = 1
            rake = Rake()
            while True:
                line = self.readblock(f)
                #check new record starts
                if line.startswith('%d. ' % n):
                    data = {}
                    data['id'] = n
                    #get time
                    data['time'] = line.split('.')[2].split(';')[0].strip()
                    #get title
                    data['title'] = self.readblock(f).replace('\n','').strip()
                    #get author
                    data['author'] = self.readblock(f).replace('\n','').strip()
                    #detect affiliation
                    line = self.readblock(f)
                    if line.startswith('Author information:'):
                        data['affiliation'] = line.replace('\n','').strip()
                        line = self.readblock(f)
                    #abstract
                    while line.startswith('Comment'):
                        line = self.readblock(f)
                    #no abstract
                    if line.find('DOI:') >=0 or line.find('PMID:') >= 0 or line.find('PMCID:') >= 0:
                        data['DOI'] = line.replace('\n','').rstrip('[Indexed for MEDLINE]').strip()
                        #skip this record as it does not have abstract
                        n += 1
                        continue
                    else:
                        data['abstract'] = line.replace('\n','').strip()
                        line = self.readblock(f)
                        #skip all other elements until encountering DOI
                        while line.find('DOI:') == -1 and line.find('PMID:') == -1 and line.find('PMCID:') == -1:
                            line = self.readblock(f)
                        data['DOI'] = line.replace('\n','').rstrip('[Indexed for MEDLINE]').strip()
                        n += 1

                        #here data is ready for processing
                        rake.extract_keywords_from_text(data['abstract'])
                        words = rake.get_ranked_phrases()
                        data['keywords'] = words[:2]
                        print(data)
                        return
                #record ends
                if n > 240276:
                    break
