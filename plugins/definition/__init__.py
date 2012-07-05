#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import urllib2, urllib
import json
import unicodedata
from plugin import *

class definition(Plugin):
 
    @register("en-US", u"(字典搜尋.*|搜尋字典.*|定義.*|搜尋定義.*|.*.的定義|.*的意思｜翻譯.*)")
    def define(self, speech, language, regMatched):

        if (language == "en-US"):
            
            if (speech.count(u'字典搜尋') > 0):
                speech = speech.replace(u'字典搜尋','')
            elif (speech.count(u"搜尋字典") > 0):
                speech = speech.replace(u"搜尋字典",'')
            elif (speech.count(u"定義") > 0):
                speech = speech.replace(u"定義",'')
            elif (speech.count(u"的定義") > 0):
                speech = speech.replace(u"的定義",'')
            elif (speech.count(u"搜尋定義") > 0):
                speech = speech.replace(u"搜尋定義",'')
            elif (speech.count(u"的意思") > 0):
                speech = speech.replace(u"的意思",'')
            elif (speech.count(u"翻譯") > 0):
                speech = speech.replace(u"翻譯",'')
            speech = speech.strip()
            if speech == "":
                speech = self.ask(u"你想在字典中搜尋什麼？")

        Query = urllib.quote_plus(speech.encode("utf-8"))

            
        query = self.cleanString(speech)
        query_clean = self.cleanString(speech)
        self.say(u"在字典搜尋 "+speech +u" 中...")
        url = u"http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&q=" +speech+ "&sl=zh-TW&tl=zh-TW&restrict=pr%2Cde&client=te"
        
        url=url.encode('utf-8')
        url=urllib2.unquote(url)
        print url
        definition = None
        try:
            jsonString = urllib2.urlopen(url, timeout=3).read()
            jsonString = jsonString.replace(",200,null)","").replace("dict_api.callbacks.id100(","")
            jsonString = jsonString.replace('\\x3c','').replace('\\x3d','').replace('\\x3e','').replace('\\x22','').replace('\\x26','').replace("#39;","'")
            response = json.loads(jsonString)
            definition = response["webDefinitions"][0]["entries"][0]["terms"][0]["text"]
        except:
            pass

        if definition != None:
            self.say(definition);
        else:
            if language == 'en-US':
                self.say(u"抱歉，在字典中找不到 "+query+"...")
        self.complete_request()
        
    def cleanString(self, s):
        if isinstance(s,str):
            s = unicode(s,"utf8","replace")
        s=unicodedata.normalize('NFD',s)
        return s.encode('ascii','ignore')