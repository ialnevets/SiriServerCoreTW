#!/usr/bin/python
# -*- coding: utf-8 -*-

#author: AlphaBetaPhi <beta@alphabeta.ca>
#todo: check for existing alarms, delete alarms, update alarms, add original commands aka wake me up/tomorrow morning/midnight/etc.
#project: SiriServer
#commands: set an alarm for HH:MM AM/PM
# set an alarm for HH AM/PM
# set an alarm for HH AM/PM <called/labeled/named> <[word 1] [word 2] [word 3]>
#comments: feel free to email any comments/bug/updates


import re

from fractions import Fraction

from plugin import *

from siriObjects.baseObjects import AceObject, ClientBoundCommand
from siriObjects.uiObjects import AddViews, AssistantUtteranceView
from siriObjects.systemObjects import DomainObject
from siriObjects.alarmObjects import *

class alarmPlugin(Plugin):

    localizations = {
        'Alarm': {
            "settingAlarm": {
                "en-US": u"設定鬧鐘"
            }, "alarmWasSet": {
                "en-US": u"你的鬧鐘設定為 {2} {0}:{1}"
            }, "alarmSetWithLabel": {
                "en-US": u"你的鬧鐘 {0} {1} 已經設定在 {4} {2}:{3}"
            }
        }
    }

    res = {
        'setAlarm': {
            'en-US': u".*鬧鐘.*"
        }
    }

    @register("en-US", res['setAlarm']['en-US'])
    def setAlarm(self, speech, language):

        if (speech.count(u"上午") > 0 and speech.count(u"下午") and speech.count(u"早上")  and speech.count(u"晚上")  and speech.count(u"點")):
            alarmString = re.findall(ur".*鬧鐘.*(上午|下午|早上|晚上)(\s|)(一點|兩點|三點|四點|五點|六點|七點|八點|九點|十點|十一點|十二點|\d.*點)(\s|)(\d*)(.*)", speech)
        else:
            content_raw = self.ask(u"請問要設定什麼時候?")
            try:
                alarmString = re.findall(ur".*(上午|下午|早上|晚上)(\s|)(一點|兩點|三點|四點|五點|六點|七點|八點|九點|十點|十一點|十二點|\d.*點)(\s|)(\d*)(.*)", content_raw)
            except:
                self.say(u"{0}對不起我,我不理解你的意思".format(self.user_name()))
                self.say(u"請用上午九點十分 這種格式")

        alarmAMPM = alarmString[0][0]
        alarmHour = alarmString[0][2]
        alarmMinutes = alarmString[0][4]

        alarmHalfHour = alarmString[0][5]
        if alarmHalfHour == u"半":
            alarmMinutes = "30"
        elif alarmHalfHour == u"十五":
            alarmMinutes = "15"
        elif alarmHalfHour == u"二十五":
            alarmMinutes = "25"
        elif alarmHalfHour == u"三十五":
            alarmMinutes = "35"
        elif alarmHalfHour == u"四十五":
            alarmMinutes = "45"
        elif alarmHalfHour == u"五十五":
            alarmMinutes = "55"
        elif alarmHalfHour == u"十分":
            alarmMinutes = "10"
        elif alarmHalfHour == u"二十分":
            alarmMinutes = "20"
        elif alarmHalfHour == u"三十分":
            alarmMinutes = "30"
        elif alarmHalfHour == u"四十分":
            alarmMinutes = "40"
        elif alarmHalfHour == u"五十分":
            alarmMinutes = "50"



        if alarmHour == u"一點":
            alarmHour = "1"
        elif alarmHour == u"兩點":
            alarmHour = "2"
        elif alarmHour == u"三點":
            alarmHour = "3"
        elif alarmHour == u"四點":
            alarmHour = "4"
        elif alarmHour == u"五點":
            alarmHour = "5"
        elif alarmHour == u"六點":
            alarmHour = "6"
        elif alarmHour == u"七點":
            alarmHour = "7"
        elif alarmHour == u"八點":
            alarmHour = "8"
        elif alarmHour == u"九點":
            alarmHour = "9"
        elif alarmHour == u"十點":
            alarmHour = "10"
        elif alarmHour == u"十一點":
            alarmHour = "11"
        elif alarmHour == u"十二點":
            alarmHour = "12"

        alarmHour = int(re.findall("\d*",alarmHour)[0])


        alarm24Hour = alarmHour
        alarmLabelExists = None
        alarmLabel = None

        #the siri alarm object requires 24 hour clock
        if (alarmAMPM == u"下午" or alarmAMPM == u"晚上" and alarmHour != 12):
            alarm24Hour += 12

        if alarmMinutes == u"十分":
            alarmMinutes = "10"

        if alarmMinutes == None or alarmMinutes == "":
            alarmMinutes = "00"

        alarmMinutes = int(alarmMinutes)


        if alarmMinutes > 60:
            alarmMinutes = 60



        view = AddViews(self.refId, dialogPhase="Reflection")
        view.views = [
            AssistantUtteranceView(
                speakableText=alarmPlugin.localizations['Alarm']['settingAlarm'][language],
                dialogIdentifier="Alarm#settingAlarm")]
        self.sendRequestWithoutAnswer(view)

        #create the alarm
        alarm = AlarmObject(alarmLabel, int(alarmMinutes), alarm24Hour, None, 1)
        response = self.getResponseForRequest(AlarmCreate(self.refId, alarm))

        view = AddViews(self.refId, dialogPhase="Completion")

        if alarmLabel == None:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmWasSet'][language].format(alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmWasSet")
        else:
            view1 = AssistantUtteranceView(speakableText=alarmPlugin.localizations['Alarm']['alarmSetWithLabel'][language].format(alarmLabelExists, alarmLabel, alarmHour, alarmMinutes, alarmAMPM), dialogIdentifier="Alarm#alarmSetWithLabel")

        view2 = AlarmSnippet(alarms=[alarm])
        view.views = [view1, view2]
        self.sendRequestWithoutAnswer(view)
        self.complete_request()
