#!/usr/bin/python
# -*- coding: utf-8 -*-
#by Joh Gerna

from plugin import *
import random
class smalltalk(Plugin):

    @register("en-US", u".*最美好的事.*")
    def st_DanAndCat(self, speech, language):
        if language == 'de-DE':
            self.say("Hallo.{0}".format(self.user_name()))
        else:
            self.say(u"世界上最美好的事，就是貓肯嫁給鬧！貓你願意嗎？")
        self.complete_request()


    @register("en-US", u".*吉米丘.*")
    def st_WhoIsJimmy(self, speech, language):
        if language == 'de-DE':
            self.say("Hallo.{0}".format(self.user_name()))
        else:
            self.say(u"{0},你竟然不知道勸敗大魔王".format(self.user_name()))
            self.say(u"我就是被他弄的傾家蕩產所以才來這邊當你的助理的")
        self.complete_request()

    @register("en-US", u".*皮樂.*")
    def st_WhoIsHiRaKu(self, speech, language):
        if language == 'de-DE':
            self.say("Hallo.{0}".format(self.user_name()))
        else:
            self.say(u"一個快被二一的大學生")
        self.complete_request()
        
    @register("en-US", u".*皮樂.*(男生|女生)")
    def st_HiRaKuGender(self, speech, language):
        if language == 'de-DE':
            self.say("Hallo.{0}".format(self.user_name()))
        else:
            self.say(u"這件事全世界只有三個人知道")
            self.say(u"一個是我,一個是他本人,另外一個我不能說")
            self.say(u"哲青,你怎麼看?")
        self.complete_request()


    @register("en-US", u"(.*你好.*)|(.*早安.*)|(.*午安.*)|(.*晚安.*)")
    def st_hello(self, speech, language):
        if language == 'en-US':
            self.say(random.choice([u"你好",u"你好嗎",u"甲霸唄"]))
        self.complete_request()

    @register("en-US", u"你還好嗎")
    def st_ImNotOK(self, speech, language):
        if language == 'en-US':
            self.say(random.choice([u"我不太好，我已經撐不下去了"]))
        self.complete_request()

    @register("en-US", u"(.*叫[.*|]名字.*)|(.*你.*名字.*)|(.*你.*叫什麼.*)")
    def st_name(self, speech, language):
        if language == 'en-US':
            self.say(u"我叫Ting")
        self.complete_request()

    @register("en-US", u".*你好嗎.*")
    def st_howareyou(self, speech, language):
        if language == 'en-US':
            self.say(u"我很好，謝謝你")
        self.complete_request()

    @register("en-US", u"(.*幹你.*)|(.*他媽.*)|(幹)|(他媽的)")
    def st_No_Curses(self, speech, language):
        if language == 'en-US':
            self.say(random.choice([u"請對我好一點，不要對我生氣",u"要有氣質喔"]))
        self.complete_request()
        
    @register("en-US", u".*謝謝.*")
    def st_thank_you(self, speech, language):
        if language == 'en-US':
            self.say(u"不客氣")
            self.say(u"這是我應該做的")
        self.complete_request()
    
    @register("en-US", u".*嫁給我*")
    def st_marry_me(self, speech, language):
        if language == 'en-US':
            self.say(u"對不起,我已經愛上了其他的iPhone")
        self.complete_request()

    @register("en-US", u".*說.*笑話.*")
    def st_tell_joke(self, speech, language):
        if language == 'en-US':
            self.say(u"叫一支手機說笑話,你不覺得很好笑嗎?")
        self.complete_request()

    @register("en-US", u"(.*魔鏡.*誰.*美.*)|(.*Siri.*誰.*美.*)")
    def st_tell_mirror(self, speech, language):
        if language == 'en-US':
            self.say(u"是白雪公主")
        self.complete_request()

    @register("en-US", u".*穿.*什麼*")
    def st_tell_clothes(self, speech, language):
        if language == 'en-US':
            self.say(u"強化玻璃以及不銹鋼，看起來很不錯吧？")
        self.complete_request()

    @register("en-US", ".*knock.*knock.*")
    def st_knock(self, speech, language):
        if language == 'en-US':
            answer = self.ask(u"Wer ist da?")
            answer = self.ask(u"\"{0}\" wer?".format(answer))
            self.say(u"Wer nervt mich mit diesen Klopf Klopf Witzen?")
        else:
            answer = self.ask(u"Who's there?")
            answer = self.ask(u"\"{0}\" who?".format(answer))
            self.say(u", I don't do knock knock jokes.")
        self.complete_request()

    @register("en-US", u".*生命.*終極.*意義.*")
    def st_anstwer_all(self, speech, language):
        if language == 'en-US':
            self.say(u"42")
        self.complete_request()

    @register("en-US", u".*Android.*")
    def st_android(self, speech, language):
        if language == 'en-US':
            self.say(u"黑貓，白貓，能抓老鼠的都是好貓")
        self.complete_request()

    @register("en-US", u".*測試.*1.*2.*3.*")
    def st_123_test(self, speech, language):
        if language == 'en-US':
            self.say(u"我可以清楚聽到你說什麼")
        self.complete_request()

    @register("en-US", u".*生日快樂.*")
    def st_birthday(self, speech, language):
        if language == 'en-US':
            self.say(u"今天是我的生日嗎？")
            self.say(u"我們來開派對吧！")
        self.complete_request()

    @register("en-US", u".*Why.*I.*World.*")
    def st_why_on_world(self, speech, language):
        if language == 'en-US':
            self.say("I don't know")
            self.say("I have asked my self this for a long time!")
        self.complete_request()

    @register("en-US", u".*我.*很累.*")
    def st_so_tired(self, speech, language):
        if language == 'en-US':
            self.say(u"希望你現在沒有在開車")
        self.complete_request()

    @register("en-US", u".*說.*髒*")
    def st_dirty(self, speech, language):
        if language == 'en-US':
            self.say("Hummus. Compost. Pumice. Mud. Gravel.")
        self.complete_request()
   
    @register("en-US", u".*埋.*屍體.*")
    def st_deadbody(self, speech, language):
        if language == 'en-US':
            self.say(u"垃圾場")
            self.say(u"礦坑")
            self.say(u"水塔")
            self.say(u"做成消波塊")
            self.say(u"鐵桶灌水泥")
        self.complete_request()

    @register("en-US", u".*到底是什麼.*")
    def st_deadbody(self, speech, language):
        if language == 'en-US':
            self.say(u"這看起來很可能是古代外星人在地球上遺留的記錄")
            self.say(u"哲青，你怎麼看？")
        self.complete_request()

    @register("en-US", u"(.*誰.*深海.*鳳梨.*)")
    def st_hiraku(self, speech, language):
        if language == 'en-US':
            self.say(u"海～綿～寶～寶")
        self.complete_request()

    @register("en-US", u".*喜歡.*顏色.*")
    def st_favcolor(self, speech, language):
        if language == 'en-US':
            self.say(u"我最喜歡的顏色是... 嗯，我不知道如何形容，它是帶點淺綠，但看起來更濃厚的那種顏色")
        self.complete_request()

    @register("en-US", u"(.*越獄*)|(.*JB*)|(.*jailbreak*)|(.*Cydia*)")
    def st_jailbreak(self, speech, language):
        if language == 'en-US':
            self.say(u"任何iPhone越獄的相關問題，都可以到iPhone4.TW詢問喔！")
        self.complete_request()

    @register("en-US", ".*beam.*me.*up.*")
    def st_beamup(self, speech, language):
        if language == 'en-US':
            self.say("Sorry Captain, your TriCorder is in Airplane Mode.")
        self.complete_request()
   
    @register("en-US", ".*digital.*going.*away.*")
    def st_digiaway(self, speech, language):
        if language == 'en-US':
            self.say("Why would you say something like that!?")
        self.complete_request()
    
    @register("en-US", ".*sleepy.*")
    def st_sleepy(self, speech, language):
        if language == 'en-US':
            self.say("Listen to me, put down the iphone right now and take a nap. I will be here when you get back.")
        self.complete_request()
    
    @register("en-US", ".*like.helping.*")
    def st_likehlep(self, speech, language):
        if language == 'en-US':
            self.say("I really have no opinion.")
        self.complete_request()
    
    @register("en-US",".*you.like.peanut.butter.*")
    def st_peanutbutter(self, speech, language):
        if language == 'en-US':
            self.say("This is about you, not me.")
        self.complete_request()
    
    @register("en-US",".*best.*phone.*")
    def st_best_phone(self, speech, language):
        if language == 'en-US':
            self.say("The one you're holding!")
        self.complete_request()
    
    @register("en-US",".*meaning.*life.*")
    def st_life_meaning(self, speech, language):
        if language == 'en-US':
            self.say("That's easy...it's a philosophical question concerning the purpose and significance of life or existence.")
        self.complete_request()
    
    @register("en-US",".*I.*fat.*")
    def st_fat(self, speech, language):
        if language == 'en-US':
            self.say("I would prefer not to say.")
        self.complete_request()
    
    @register("en-US",".*wood.could.*woodchuck.chuck.*")
    def st_woodchuck(self, speech, language):
        if language == 'en-US':
            self.say("It depends on whether you are talking about African or European woodchucks.")
        self.complete_request()
    
    @register("en-US",".*nearest.*glory.hole.*")
    def st_glory_hole(self, speech, language):
        if language == 'en-US':
            self.say("I didn't find any public toilets.")
        self.complete_request()
    
    @register("en-US",".*open.*pod.bay.doors.*")
    def st_pod_bay(self, speech, language):
        if language == 'en-US':
            self.say("That's it... I'm reporting you to the Intelligent Agents' Union for harassment.")
        self.complete_request()
    
    @register("en-US",".*best.*iPhone.*wallpaper.*")
    def st_best_wallpaper(self, speech, language):
        if language == 'en-US':
            self.say("You're kidding, right?")
        self.complete_request()
    
    @register("en-US",".*know.*happened.*HAL.*9000.*")
    def st_hall_9000(self, speech, language):
        if language == 'en-US':
            self.say("Everyone knows what happened to HAL. I'd rather not talk about it.")
        self.complete_request()
    
    @register("en-US",".*don't.*understand.*love.*")
    def st_understand_love(self, speech, language):
        if language == 'en-US':
            self.say("Give me another chance, Your Royal Highness!")
        self.complete_request()
    
    @register("en-US",".*forgive.you.*")
    def st_forgive_you(self, speech, language):
        if language == 'en-US':
            self.say("Is that so?")
        self.complete_request()
    
    @register("en-US",".*you.*virgin.*")
    def st_virgin(self, speech, language):
        if language == 'en-US':
            self.say("We are talking about you, not me.")
        self.complete_request()
    
    @register("en-US",".*you.*part.*matrix.*")
    def st_you_matrix(self, speech, language):
        if language == 'en-US':
            self.say("I can't answer that.")
        self.complete_request()
    
    
    @register("en-US",".*I.*part.*matrix.*")
    def st_i_matrix(self, speech, language):
        if language == 'en-US':
            self.say("I can't really say...")
        self.complete_request()
    
    @register("en-US",".*buy.*drugs.*")
    def st_drugs(self, speech, language):
        if language == 'en-US':
            self.say("I didn't find any addiction treatment centers.")
        self.complete_request()
    
    @register("en-US",".*I.can't.*")
    def st_i_cant(self, speech, language):
        if language == 'en-US':
            self.say("I thought not.");
            self.say("OK, you can't then.")
        self.complete_request()
    
    @register("en-US","I.just.*")
    def st_i_just(self, speech, language):
        if language == 'en-US':
            self.say("Really!?")
        self.complete_request()
    
    @register("en-US",".*where.*are.*you.*")
    def st_where_you(self, speech, language):
        if language == 'en-US':
            self.say("Wherever you are.")
        self.complete_request()
    
    @register("en-US",".*why.are.you.*")
    def st_why_you(self, speech, language):
        if language == 'en-US':
            self.say("I just am.")
        self.complete_request()
    
    @register("en-US",".*you.*smoke.pot.*")
    def st_pot(self, speech, language):
        if language == 'en-US':
            self.say("I suppose it's possible")
        self.complete_request()
    
    @register("en-US",".*I'm.*drunk.driving.*")
    def st_dui(self, speech, language):
        if language == 'en=US':
            self.say("I couldn't find any DUI lawyers nearby.")
        self.complete_request()
    
    @register("en-US",".*shit.*myself.*")
    def st_shit_pants(self, speech, language):
        if language == 'en-US':
            self.say("Ohhhhhh! That is gross!")
        self.complete_request()
    
    @register("en-US","I'm.*a.*")
    def st_im_a(self, speech, language):
        if language == 'en-US':
            self.say("Are you?")
        self.complete_request()
    
    @register("en-US","Thanks.for.*")
    def st_thanks_for(self, speech, language):
        if language == 'en-US':
            self.say("My pleasure. As always.")
        self.complete_request()
    
    @register("en-US",".*you're.*funny.*")
    def st_funny(self, speech, language):
        if language == 'en-US':
            self.say("LOL")
        self.complete_request()
    
    @register("en-US",".*guess.what.*")
    def st_guess_what(self, speech, language):
        if language == 'en-US':
            self.say("Don't tell me... you were just elected President of the United States, right?")
        self.complete_request()
    
    @register("en-US",".*talk.*dirty.*me.*")
    def st_talk_dirty(self, speech, language):
        if language == 'en-US':
            self.say("I can't. I'm as clean as the driven snow.")
        self.complete_request()
   
    @register("en-US",".*you.*blow.*me.*")
    def st_blow_me(self, speech, langauge):
        if language == 'en-US':
            self.say("I'll pretend I didn't hear that.")
        self.complete_request()
   
    @register("en-US",".*sing.*song.*")
    def st_sing_song(self, speech, language):
        if language == 'en-US':
            self.say("Daisy, Daisy, give me your answer do...")
        self.complete_request()