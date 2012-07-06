#!/usr/bin/python
# -*- coding: utf-8 -*-

#need help? ask john-dev

import re
import urllib2, urllib
import json

from plugin import *

import urllib2
import json

BingMapAPIKey = APIKeyForAPI("google")

class newsSearch(Plugin):

    @register("de-DE", "(Wo bin ich.*)")
    @register("en-US", u"(.*頭條.*)|(.*新聞.*)")

    def newsSearch(self, speech, language):
        type = self.ask(u"頭條、世界、經濟、國際、科技、娛樂、運動、健康",u"請問要搜尋什麼類別？")
        if type == u"頭條":
            t=u'h'
        elif type == u"世界":
            t=u'w'
        elif type == u"經濟":
            t=u'b'
        elif type == u"國際":
            t=u'n'
        elif type == u"科技":
            t=u't'
        elif type == u"娛樂":
            t=u'e'
        elif type == u"運動":
            t=u's'
        elif type == u"健康":
            t=u'm'
        else:
            t=u'h'
            type=u"頭條"

        url = "https://ajax.googleapis.com/ajax/services/search/news?v=1.0&topic={0}&rsz=1&hl=zh-TW&ned=tw".format(t)
        self.say(u"搜尋中,請稍後...")
        request = urllib2.Request(url, None, {'Referer': "SiriServer"})
        response = urllib2.urlopen(request)

        results = json.load(response)
        ans = results['responseData']['results'][0]['content']
        ans.replace("<b>...</b>","")

        self.say(ans,u"以下為{0}新聞頭條".format(type))

        self.complete_request()


        #h - specifies the top headlines topic
        #w - specifies the world topic
        #b - specifies the business topic
        #n - specifies the nation topic
        #t - specifies the science and technology topic
        #el - specifies the elections topic
        #p - specifies the politics topic
        #e - specifies the entertainment topic
        #s - specifies the sports topic
        #m - specifies the health topic