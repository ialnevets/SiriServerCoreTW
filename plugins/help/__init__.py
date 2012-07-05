#!/usr/bin/python
# -*- coding: utf-8 -*-
#by Joh Gerna thanks for help to john-dev
#updated by Mike Pissanos (gaVRoS) for SiriServerCore

import re,os

config_file="plugins.conf"
pluginPath="plugins"
from plugin import *
tline_answer_de = ''
tline_answer_en = ''

with open(config_file, "r") as fh:
    for line in fh:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        try:
            with open(pluginPath+"/"+line+"/__init__.py", "rU") as fd:
                for tline in fd:
                    tline=tline.strip()
                    if tline.startswith("@register(\"de-DE\", "):
                        tline = tline.replace('@register','').replace('(','').replace(')','').replace('\"','').replace('.','').replace('de-DE, ','').replace('[a-zA-Z0-9]+','').replace('\w','').replace('|',' oder ')
                        tline_answer_de = tline_answer_de +'\n' + "".join(tline)

                    elif tline.startswith("@register(\"en-US\", "):
                        tline = tline.replace('*','').replace('u','').replace('@register','').replace('(','').replace(')','').replace('\"','').replace('.','').replace('en-US, ','').replace('[a-zA-Z0-9]+','').replace('\w','').replace('|',' or  ')
                        tline_answer_en = tline_answer_en + '\n' + "".join(tline)
        except:
            tline = "Plugin loading failed"

class help(Plugin):
    
    @register("de-DE", "(Hilfe)|(Befehle)")
    @register("en-US", u"(.*你會做什麼.*)|(.*你會什麼.*)|(.*你能做什麼.*)|(.*你的功能.*)")
    def st_hello(self, speech, language):
        if language == 'de-DE':
            self.say("Das sind die Befehle die in Deiner Sprache verfügbar sind:")
            self.say("".join(tline_answer_de ),' ')
        else:
            self.say(u"以下是我能做的事情")
            EnabledCommnd = u"功能性項目：" + '\n' +\
                            u"傳簡訊給XXX" + '\n' +\
                            u"今天星期幾" + '\n' +\
                            u"找附近的XX or  搜尋附近的XX" + '\n' +\
                            u"XX在哪裡 or  XX怎麼走 or  XX怎麼去" + '\n' +\
                            u"新增備忘錄" + '\n' +\
                            u"打給 or  撥給 or  電話給" + '\n' +\
                            u"現在幾點 or  的時間" + '\n' +\
                            u"今天天氣 or  天氣預報" + '\n' +\
                            u"我的位置 or  我在哪" + '\n' +\
                            u"網頁搜尋 or  Google搜尋" + '\n' +\
                            u"搜尋圖片" + '\n' +\
                            u"字典搜尋XXX" + '\n' +\
                            u"頭條新聞"
            
            self.say(EnabledCommnd,u"部分功能可能會暫時失效,請見諒")
        self.complete_request()

