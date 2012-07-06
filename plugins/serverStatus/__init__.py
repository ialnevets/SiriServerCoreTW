#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from datetime import date
import locale 
from plugin import *

class talkToMe(Plugin):   

    @register("en-US", u".*伺服器.*")
    def ttm_uptime_status(self, speech, language):
        uptime = os.popen("uptime").read()
        self.say(u"伺服的運轉時間")
        self.say(uptime, ' ')
        self.complete_request()     

