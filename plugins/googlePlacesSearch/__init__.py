#!/usr/bin/python
# -*- coding: utf-8 -*-
# by Alex 'apexad' Martin
# help from: muhkuh0815 & gaVRos

import re
import urllib2, urllib
import json
import random
import math

from plugin import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.systemObjects import GetRequestOrigin,Location
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.localsearchObjects import Business, MapItem, MapItemSnippet, Rating

googleplaces_api_key = APIKeyForAPI("google")
 
class googlePlacesSearch(Plugin):
     @register("en-GB", "(find|show|where).* (nearest|nearby|closest) (.*)")
     @register("en-US", u"(搜尋|找附近|搜尋附近|尋找最近).*(.*)")
     def googleplaces_search(self, speech, language, regex):
          self.say(u"搜尋中",' ')
          mapGetLocation = self.getCurrentLocation()
          latitude= mapGetLocation.latitude
          longitude= mapGetLocation.longitude
          Title = re.findall(u"(找附近|搜尋附近).*(.*)",speech)[0][1]   ##regex.group(regex.lastindex).strip()

          if Title.count(u'的') > 0:
               Title = Title.replace(u"的","")

          if Title.count(u"seven") > 0 or Title.count(u"統一") > 0:
              Title = u"7-11"
          Query = urllib.quote_plus(str(Title.encode("utf-8")))
          random_results = random.randint(2,15)
          googleurl = "https://maps.googleapis.com/maps/api/place/search/json?location={0},{1}&radius=5000&name={2}&sensor=true&key={3}".format(latitude,longitude,str(Query),str(googleplaces_api_key))
          print googleurl
          try:
               jsonString = urllib2.urlopen(googleurl, timeout=20).read()
          except:
               jsonString = None
          if jsonString != None:
               response = json.loads(jsonString)
               if (response['status'] == 'OK') and (len(response['results'])):
                    googleplaces_results = []
                    for result in response['results']:
                         if "rating" in result:
                              avg_rating = result["rating"]
                         else:
                              avg_rating = 0.0
                         rating = Rating(value=avg_rating, providerId='Google Places', count=0)
                         details = Business(totalNumberOfReviews=0,name=result['name'],rating=rating)
                         if (len(googleplaces_results) < random_results):
                              mapitem = MapItem(label=result['name'], street=result['vicinity'], latitude=result['geometry']['location']['lat'], longitude=result['geometry']['location']['lng'])
                              mapitem.detail = details
                              googleplaces_results.append(mapitem)
                         else:
                              break
                    mapsnippet = MapItemSnippet(items=googleplaces_results)
                    count_min = min(len(response['results']),random_results)
                    count_max = max(len(response['results']),random_results)
                    view = AddViews(self.refId, dialogPhase="Completion")
                    if Title == u"7-11":
                        Title = u"Seven Eleven"
                    view.views = [AssistantUtteranceView(speakableText=u'我找到 '+str(count_max)+u' 個 '+ Title +u' 其中 '+str(count_min)+u' 個非常靠近你:', dialogIdentifier="googlePlacesMap"), mapsnippet]
                    self.sendRequestWithoutAnswer(view)
               else:
                    self.say(u"很抱歉，在你附近找不到"+Title)
          else:
               self.say(u"很抱歉，在你附近找不到"+Title)
          self.complete_request()

    
     @register("en-US", u"(.*在哪裡|.*怎麼走|.*怎麼去)")
     def googleplaces_WhereIs(self, speech, language, regex):
          self.say(u"搜尋中",' ')
          mapGetLocation = self.getCurrentLocation()
          latitude= mapGetLocation.latitude
          longitude= mapGetLocation.longitude
          Title = re.findall(u"([\s\S]*)(在哪裡|怎麼走|怎麼去)",speech)[0][0]  ##regex.group(regex.lastindex).strip()
          Query = urllib.quote_plus(str(Title.encode("utf-8")))
          random_results = random.randint(2,15)
          googleurl = "https://maps.googleapis.com/maps/api/place/search/json?location={0},{1}&radius=7000000&name={2}&sensor=true&key={3}".format(latitude,longitude,str(Query),str(googleplaces_api_key))
          print googleurl
          try:
               jsonString = urllib2.urlopen(googleurl, timeout=20).read()
          except:
               jsonString = None
          if jsonString != None:
               response = json.loads(jsonString)
               if (response['status'] == 'OK') and (len(response['results'])):
                    googleplaces_results = []
                    for result in response['results']:
                         if "rating" in result:
                              avg_rating = result["rating"]
                         else:
                              avg_rating = 0.0
                         rating = Rating(value=avg_rating, providerId='Google Places', count=0)
                         details = Business(totalNumberOfReviews=0,name=result['name'],rating=rating)
                         if (len(googleplaces_results) < 1):
                              mapitem = MapItem(label=result['name'], street=result['vicinity'], latitude=result['geometry']['location']['lat'], longitude=result['geometry']['location']['lng'])
                              mapitem.detail = details
                              googleplaces_results.append(mapitem)
                         else:
                              break
                    mapsnippet = MapItemSnippet(userCurrentLocation=False, items=googleplaces_results)
                    view = AddViews(self.refId, dialogPhase="Completion")
                    view.views = [AssistantUtteranceView(speakableText = Title + u'顯示於地圖:', dialogIdentifier="googlePlacesMap"), mapsnippet]
                    self.sendRequestWithoutAnswer(view)
               else:
                    self.say(u"很抱歉，在你附近找不到"+Title)
          else:
               self.say(u"很抱歉，在你附近找不到"+Title)
          self.complete_request()