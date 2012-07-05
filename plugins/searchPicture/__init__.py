#!/usr/bin/python
# -*- coding: utf-8 -*-
#displaypicture.py

#Google Image Plugin v0.2
#by Ryan Davis (neoshroom)
#feel free to add to, mess with and use this plugin with original attribution
#additional Google Image functions to add can be found at:
#https://developers.google.com/image-search/v1/jsondevguide#request_format

#usage: say "display a picture of william shakespeare" 
#(or anything else you want a picture of)

# Must be before wwwsearch plugin

import re
import urllib2, urllib
import json

from plugin import *
from plugin import __criteria_key__

from siriObjects.uiObjects import AddViews
from siriObjects.answerObjects import AnswerSnippet, AnswerObject, AnswerObjectLine

class define(Plugin):
    
    @register("en-US",u"(照片搜尋.*)|(圖片搜尋.*)|(搜尋照片.*)|(搜尋圖片.*)|(顯示圖片.*)|(顯示照片.*)")
    def displaypicture(self, speech, language, regex):

        if (language == "en-US"):
            if (speech.find(u'顯示照片') == 0):
                speech = speech.replace(u'顯示照片',' ',1)
            elif (speech.find(u"顯示圖片") == 0):
                speech = speech.replace(u"圖片",' ',1)
            elif (speech.find(u"搜尋照片") == 0):
                speech = speech.replace(u"搜尋照片",' ',1)
            elif (speech.find(u"搜尋圖片") == 0):
                speech = speech.replace(u"搜尋圖片",' ',1)
            

            speech = speech.strip()
            if speech == "":
                speech = self.ask(u"你想搜尋什麼的圖片？")

        Query = urllib.quote_plus(speech.encode("utf-8"))
        SearchURL = u'https://ajax.googleapis.com/ajax/services/search/images?v=1.0&imgsz=small|medium|large|xlarge&q=' + str(Query)
        try:

            if language == 'en-US':                
               self.say(u"這是 "+speech+u" 的圖片...")
            jsonResponse = urllib2.urlopen(SearchURL).read()
            jsonDecoded = json.JSONDecoder().decode(jsonResponse)
            ImageURL = jsonDecoded['responseData']['results'][0]['unescapedUrl']
            view = AddViews(self.refId, dialogPhase="Completion")
            ImageAnswer = AnswerObject(title=speech,lines=[AnswerObjectLine(image=ImageURL)])
            view1 = AnswerSnippet(answers=[ImageAnswer])
            view.views = [view1]
            self.sendRequestWithoutAnswer(view)
            self.complete_request()
        except (urllib2.URLError):
            self.say("Sorry, a connection to Google Images could not be established.")
            self.complete_request()