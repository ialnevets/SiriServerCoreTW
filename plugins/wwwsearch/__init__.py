#!/usr/bin/python                                                                                                                                                                   
# -*- coding: utf-8 -*-                                                                                                                                                             
import re
from plugin import *
from siriObjects.websearchObjects import WebSearch

class wwwSearch(Plugin):

    @register("en-US", u"(網頁搜尋.*)|(Google.*搜尋.*)|(Google 搜尋.*)")
    def webSearch(self, speech, language,regex):
        if (language == "en-US"):
            if (speech.find(u'網頁搜尋') == 0):
                speech = speech.replace(u'網頁搜尋', ' ',1)
            elif (speech.find(u'Google搜尋') == 0):
                speech = speech.replace(u'Google搜尋',' ',1)

            speech = speech.strip()
            if speech == "":
                speech = self.ask(u"你想搜尋什麼？")

        search = WebSearch(refId=self.refId, query=speech)
        self.sendRequestWithoutAnswer(search)
        self.complete_request()
