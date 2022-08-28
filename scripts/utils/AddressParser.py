"""
MODIFIED FROM https://github.com/chunlaw/HKAddressParser
"""

import re
import json
import bisect
import requests
from bs4 import BeautifulSoup


def matchStr(inAddr, fieldName, inStr):
    matchedPos = None
    goodness = None

    # try striping the head of inStr till match is found
    # to deal with cases like eg. inAddr = 兆康站, inStr = 港鐵兆康站
    for i in range(0, len(inStr)):
        newInStr = inStr[i:]
        matchedPosStart = inAddr.find(newInStr)
        if matchedPosStart >= 0:
            matchedPos = (matchedPosStart, matchedPosStart + len(newInStr))
            goodness = (len(newInStr)/len(inStr) - 0.5)*2
            break

        if (len(inStr) - i) <= 3: break  # give up if remaining inStr too short
        if (i >= len(inStr) // 2): break  # give up if already stripped half

    return [(fieldName, inStr, matchedPos, goodness)]


def matchChiStreetOrVillage(inAddr, inDict):
    """
    inDict is the ChiStreet field of the ogcio result, eg.
    {'StreetName': '彌敦道',
     'BuildingNoFrom': '594'   (may be absent)
     'BuildingNoTo': '596'     (may be absent)
     },

    """
    matches = []

    key = None
    if 'StreetName' in inDict: key = 'StreetName'
    if 'VillageName' in inDict: key = 'VillageName'

    inStr = inDict[key]
    inStr = inStr.split()[-1]  # to deal with case like '屯門 青麟路'
    streetMatch = matchStr(inAddr, key, inStr)[0]
    matches.append(streetMatch)

    ogcioBNoFrom = inDict.get('BuildingNoFrom', '')
    ogcioBNoTo = inDict.get('BuildingNoTo', '')

    if not ogcioBNoFrom: return matches

    inAddrBNoSpan = None  # the position of the words in the inAddr string
    inAddrBNoFrom = ''
    inAddrBNoTo = ''

    # look for street no. after the street in inAddr
    matchedPos = streetMatch[2]
    if matchedPos != None:
        matchedPosEnd = matchedPos[1]
        inStr = inAddr[matchedPosEnd:]
        reResult = re.match('([0-9A-z]+)[至及\-]*([0-9A-z]*)號', inStr)  # this matches '591-593號QWER'
        # print("a", matchedPosEnd, inStr, reResult)
        if reResult:
            inAddrBNoSpan = tuple(matchedPosEnd + x for x in reResult.span())
            inAddrBNoFrom = reResult.groups()[0]
            inAddrBNoTo = reResult.groups()[1]

    if ogcioBNoTo == '': ogcioBNoTo = ogcioBNoFrom
    if inAddrBNoTo == '': inAddrBNoTo = inAddrBNoFrom

    # check overlap between inAddrBNoFrom-To  and ogcioBNoFrom-To
    if (ogcioBNoTo < inAddrBNoFrom or ogcioBNoFrom > inAddrBNoTo):
        inAddrBNoSpan = None  # no overlap so set the matched span to none

    if 'BuildingNoFrom' in inDict:
        goodness = 1. if inAddrBNoFrom==ogcioBNoFrom else 0.5
        matches.append(('BuildingNoFrom', ogcioBNoFrom, inAddrBNoSpan, goodness))
    if 'BuildingNoTo' in inDict:
        goodness = 1. if inAddrBNoTo == ogcioBNoTo else 0.5
        matches.append(('BuildingNoTo', ogcioBNoTo, inAddrBNoSpan, goodness))

    return matches


def matchDict(inAddr, inDict):
    matches = []
    for (k, v) in inDict.items():
        #print (k,v)
        if k == 'ChiStreet':
            matches += matchChiStreetOrVillage(inAddr, v)
        elif k == 'ChiVillage':
            matches += matchChiStreetOrVillage(inAddr, v)
        elif type(v) == dict:
            matches += matchDict(inAddr, v)
        elif type(v) == str:
            matches += matchStr(inAddr, k, v)
        # Not printing any error here
        # else:
        #     print("Unhandled content: ", k, v)
    return matches


class Similarity:
    score = 0
    inAddr = ''
    inAddrHasMatch = []
    ogcioMatches = {}

    def __repr__(self):

        outStr = ''
        outStr += "query: %s\n" % self.inAddr

        tmp = "".join([ s if self.inAddrHasMatch[i] else '?' for (i,s) in enumerate(self.inAddr)])
        outStr += "match: %s\n" % tmp

        outStr += "ogcioMatches: %s\n"% self.ogcioMatches

        outStr += "Score: %s\n" % self.score

        return outStr


def getSimilarityWithOGCIO(inAddr, ogcioResult):
    """
    :param inAddr: a string of address
    :param ogcioResult: the "ChiPremisesAddress" of OGCIO query returned json
    :return:
    """

    matches = matchDict(inAddr, ogcioResult)
    #print (matches)

    inAddrHasMatch  = [False for i in range(len(inAddr))]
    score = 0

    scoreDict = {
        'Region' : 10,
        'StreetName' : 20,
        'VillageName': 20,
        'EstateName' : 20,
        'BuildingNoFrom': 30,
        'BuildingNoTo' :30,
        'BuildingName' : 40,
    }

    for (fieldName, fieldVal, matchSpan, goodness) in matches:
        if matchSpan==None:
            score-=1
            continue

        # if fieldName not in scoreDict:
        #     print("ignored ", fieldName, fieldVal)
        #     print(ogcioResult)

        score += scoreDict.get(fieldName,0) * goodness
        for i in range(matchSpan[0],matchSpan[1]) : inAddrHasMatch[i] = True


    s = Similarity()
    s.score = score
    s.inAddr = inAddr
    s.inAddrHasMatch = inAddrHasMatch
    s.ogcioMatches = matches

    return s


class Address:
    def __init__(self, addr):
        self._inputAddr = self.removeFloor(addr)
        self._OGCIOresult = self.queryOGCIO(self._inputAddr, 20)
        if self._OGCIOresult is not None:
            self._result = self.flattenOGCIO()
        else:
            self._result = None

    def flattenOGCIO(self):
        flat_result = []
        for idx, addr in enumerate(self._OGCIOresult):
            temp = {
                'rank': idx,
                'chi': addr['Address']['PremisesAddress']['ChiPremisesAddress'],
                'eng': addr['Address']['PremisesAddress']['EngPremisesAddress'],
                'geo': addr['Address']['PremisesAddress']['GeospatialInformation'],
            }
            flat_result.append(temp)
        return(flat_result)

    def ParseAddress(self):
        for (idx, aResult) in enumerate(self._result):
            self._result[idx]['match'] = getSimilarityWithOGCIO(
                self._inputAddr, aResult['chi'])

        self._result.sort(key=lambda x: x['match'].score, reverse=True)

        # print sorted result
        # for a in self._result[:3]:
        #     print("=========")
        #     print(a)

        return self._result[0]

# class Phrases:
    def searchPhrase(self, string, phrases):
        phrases.sort(key=lambda t: t[1])
        keys = [i[1] for i in phrases]
        idx = bisect.bisect_right(keys, string)
        if (idx == 0):
            return None
        if (string == phrases[idx-1][1]):
            self._tempOGIOAddr = [
                i for i in self._tempOGIOAddr if i[1] != string]
            return phrases[idx-1]
        return None

    def getChiAddress(self):
        addr = self._inputAddr
        result = []
        start = 0
        while (start < len(addr)):
            end = len(addr)
            while (start < end):
                string = addr[start:end]
                token = self.searchPhrase(string, self._tempOGIOAddr)
                if token == None:
                    end = end - 1
                else:
                    result += [token]
                    break
            if (end == start):
                if (len(result) > 0 and result[-1][0] == '?'):
                    result[-1][1] += addr[start]
                else:
                    result += [['?', addr[start]]]
            start += len(string)
        return result

    # Get Results from OGCIO API
    def queryOGCIO(self, RequestAddress, n):
        session = requests.Session()
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en,zh-Hant",
            "Accept-Encoding": "gzip"
        }
        base_url = "https://www.als.ogcio.gov.hk/lookup?"

        r = session.get(base_url,
                        headers=headers,
                        params={
                            "q": RequestAddress,
                            "n": n
                        })

        soup = BeautifulSoup(r.content, 'html.parser')
        if 'SuggestedAddress' in json.loads(str(soup)):
            return(json.loads(str(soup))['SuggestedAddress'])
        else:
            return None

    def flattenJSON(self, data, json_items):
        for key, value in data.items():
            if type(value) is dict:
                self.flattenJSON(value, json_items)
            elif type(value) is list:
                for i in value:
                    self.flattenJSON(i, json_items)
            else:
                if key == 'StreetName' or key == 'VillageName' or key == 'EstateName':
                    if re.search('[\u4e00-\u9fff]+', value):
                        for idx, st in enumerate(value.split(" ")):
                            json_items.append((key+str(idx+1), str(st)))
                else:
                    json_items.append((key, str(value)))
        return json_items

    def removeFloor(self, inputAddress):
        return re.sub("([0-9A-z\-\s]+[樓層]|[0-9A-z號\-\s]+[舖鋪]|地[下庫]|平台).*", "", inputAddress)
