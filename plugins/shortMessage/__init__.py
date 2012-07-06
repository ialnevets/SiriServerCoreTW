#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# This is a sms plugin for SiriServerCore  
# created by Eichhoernchen
#
# This file is free for private use, you need a commercial license for paid servers
#
# It's distributed under the same license as SiriServerCore
#
# You can view the license here:
# https://github.com/Eichhoernchen/SiriServerCore/blob/master/LICENSE
#
# So if you have a SiriServerCore commercial license 
# you are allowed to use this plugin commercially otherwise you are breaking the law
#
# This file can be freely modified, but this header must retain untouched
#  
# 

from plugin import *
from siriObjects.baseObjects import ObjectIsCommand
from siriObjects.contactObjects import PersonSearch, PersonSearchCompleted
from siriObjects.smsObjects import SmsSms, SmsSnippet
from siriObjects.systemObjects import SendCommands, StartRequest, \
    PersonAttribute, Person, DomainObjectCreate, DomainObjectCreateCompleted, \
    DomainObjectUpdate, DomainObjectUpdateCompleted, DomainObjectRetrieve, \
    DomainObjectRetrieveCompleted, DomainObjectCommit, DomainObjectCommitCompleted, \
    DomainObjectCancel, DomainObjectCancelCompleted
from siriObjects.uiObjects import UIDisambiguationList, UIListItem, \
    UIConfirmationOptions, ConfirmSnippet, UIConfirmSnippet, UICancelSnippet
import datetime
import random
#import pytz

responses = {
'notFound': 
    {'de-DE': u"Entschuldigung, ich konnte niemanden in deinem Telefonbuch finden der so heißt",
     'en-US': u"對不起，找不到符合的聯絡資訊"
    },
'devel':
    {'de-DE': u"Entschuldigung, aber diese Funktion befindet sich noch in der Entwicklungsphase",
     'en-US': u"對不起，功能開發中"
    },
 'select':
    {'de-DE': u"Wen genau?", 
     'en-US': u"哪一個?"
    },
'selectNumber':
    {'de-DE': u"Welche Telefonnummer für {0}",
     'en-US': u"{0} 隻電話中的哪一支"
    },
'mustRepeat': 
    {'de-DE': [u"Entschuldigung ich hab dich leider nicht verstanden."],
     'en-US': [u"對不起，我不明白你的意思，請在試一次", u"對不起，我不知道這該怎麼做，請在試一次"]
     },
'askForMessage':
    {'de-DE': [u"Was willst du schreiben?", u"Was soll drin stehen?", u"Du kannst mir jetzt diktieren!"],
     'en-US': [u"你想要傳些什麼？", u"你想要對他說什麼？", u"請告訴我傳送的內容!"]
     },
'showUpdate': 
    {'de-DE': [u"Ich hab deine Nachricht geschrieben. Willst du sie jetzt senden?", u"OK. Willst du die Nachricht jetzt senden?"],
     'en-US': [u"我已經加入你的訊息，要傳送嗎？", u"好的, 要傳送嗎?", u"我明白了, 需要我傳送出去嗎?"]
     },
'cancelSms': 
    {'de-DE': [u"OK, I schick sie nicht.", u"OK, ich hab sie verworfen"],
     'en-US': [u"好，取消傳送！", u"刪除訊息！"]
     },
'cancelFail':
    {'de-DE': [u"Sorry, aber mir ist ein Fehler beim Abbrechen passiert"],
     'en-US': [u"對不起，我無法取消傳送訊息！"]
     },
'createSmsFail':
    {'de-DE': [u"Ich konnte keine neue Nachricht anlegen, sorry"],
     'en-US': [u"我無法建立新的訊息，對不起"]
     },
'updateSmsFail':
    {'de-DE': [u"Entschuldigung ich konnte die Nachricht nicht schreiben"],
     'en-US': [u"對不起，我新增輸入你的訊息！"]
     },
'sendSms':
    {'de-DE': [u"OK, ich verschicke die Nachricht"],
     'en-US': [u"好的，我將開始傳送你的訊息"]
     },
'sendSmsFail':
    {'de-DE': [u"Umpf da ist was schief gelaufen, sorry"],
     'en-US': [u"很抱歉，有些錯誤發生了，我無法傳送你的訊息"]
     },
'clarification':
    {'de-DE': [u"Fortfahren mit senden, abbrechen, anschauen oder ändern."],
     'en-US': [u"請在次確認動作，你可以選擇傳送、取消、確認、修改訊息"]
     }
}

questions = {
'answerSEND': 
    {'de-DE': ['yes', 'senden'], # you must include yes
     'en-US': [u'yes', u"傳送"]
     },
'answerCANCEL':
    {'de-DE': ['cancel', 'abbrechen', 'stop', 'nein'],  # you must include cancel
     'en-US': [u'cancel', u'否', u'放棄', u'取消', u'不要']
     },
'answerUPDATE':
    {'de-DE': ['ändern', 'verändern'],
     'en-US': [u'修改', u'更動']
     },
'answerREVIEW':
    {'de-DE': ['anschauen', 'zeigen', 'zeig'],
     'en-US': [u'確認', u'顯示']
     }
}

snippetButtons = {
'denyText':
    {'de-DE': "Cancel",
     'en-US': u"取消"
     },
'cancelLabel':
    {'de-DE': "Cancel",
     'en-US': u"取消"
     },
'submitLabel':
    {'de-DE': "Send",
     'en-US': u"傳送"
     },
'confirmText':
    {'de-DE': "Send",
     'en-US': u"傳送"
     },
'cancelTrigger':
    {'de-DE': "Deny",
     'en-US': u"拒絕"
     }
}

speakableDemitter={
'en-US': u", or ",
'de-DE': u', oder '}


errorNumberTypes= {
'de-DE': u"Ich habe dich nicht verstanden, versuch es bitte noch einmal.",
'en-US': u"對不起，我不明白你的意思！"
}

errorNumberNotPresent= {
'de-DE': u"Ich habe diese {0} von {1} nicht, aber eine andere.",
'en-US': u"找不到 {0} 的電話於 {1}, 但是我找到另一個。"
}


numberTypesLocalized= {
'_$!<Mobile>!$_': {'en-US': u"mobile", 'de-DE': u"Handynummer"},
'iPhone': {'en-US': u"iPhone", 'de-DE': u"iPhone-Nummer"},
'_$!<Home>!$_': {'en-US': u"home", 'de-DE': u"Privatnummer"},
'_$!<Work>!$_': {'en-US': u"work", 'de-DE': u"Geschäftsnummer"},
'_$!<Main>!$_': {'en-US': u"main", 'de-DE': u"Hauptnummer"},
'_$!<HomeFAX>!$_': {'en-US': u"home fax", 'de-DE': u'private Faxnummer'},
'_$!<WorkFAX>!$_': {'en-US': u"work fax", 'de-DE': u"geschäftliche Faxnummer"},
'_$!<OtherFAX>!$_': {'en-US': u"_$!<OtherFAX>!$_", 'de-DE': u"_$!<OtherFAX>!$_"},
'_$!<Pager>!$_': {'en-US': u"pager", 'de-DE': u"Pagernummer"},
'_$!<Other>!$_':{'en-US': u"other phone", 'de-DE': u"anderes Telefon"}
}

namesToNumberTypes = {
'de-DE': {'mobile': "_$!<Mobile>!$_", 'handy': "_$!<Mobile>!$_", 'zuhause': "_$!<Home>!$_", 'privat': "_$!<Home>!$_", 'arbeit': "_$!<Work>!$_"},
'en-US': {'work': "_$!<Work>!$_",'home': "_$!<Home>!$_", 'mobile': "_$!<Mobile>!$_"}
}

class shortMessaging(Plugin):
    
    def finalSend(self, sms, language):
        
        commitCMD = DomainObjectCommit(self.refId)
        commitCMD.identifier = SmsSms()
        commitCMD.identifier.identifier = sms.identifier
        
        answer = self.getResponseForRequest(commitCMD)
        if ObjectIsCommand(answer, DomainObjectCommitCompleted):
            answer = DomainObjectCommitCompleted(answer)
            # update the sms object with current identifier and time stamp
            sms.identifier = answer.identifier
            # the timestamp should be timezone aware
            # we could use the pytz lib for that
            # get the timezone from the assistant
            # and supply it to pytz which we can
            # supply to now()
            sms.dateSent = datetime.datetime.now() 
            # tell the user we sent the sms
            createAnchor = UIAddViews(self.refId)
            createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmedValue
            
            # create a view to ask for the message
            askCreateView = UIAssistantUtteranceView()
            askCreateView.dialogIdentifier = "CreateSms#sentSMS"
            askCreateView.text = askCreateView.speakableText = random.choice(responses['sendSms'][language])
            askCreateView.listenAfterSpeaking = False
            
           
            snippet = SmsSnippet()
            snippet.smss = [sms]
            
            createAnchor.views = [askCreateView, snippet]
            
            self.sendRequestWithoutAnswer(createAnchor)
            self.complete_request()
        else:
            self.say(random.choice(responses['sendSmsFail'][language]))
            self.complete_request()
            
            
    def createSmsSnippet(self, sms, addConfirmationOptions, dialogIdentifier, text, language):
        createAnchor = UIAddViews(self.refId)
        createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmationValue
        
        # create a view to ask for the message
        askCreateView = UIAssistantUtteranceView()
        askCreateView.dialogIdentifier = dialogIdentifier
        askCreateView.text = askCreateView.speakableText = text
        askCreateView.listenAfterSpeaking = True
        
        # create a snippet for the sms
        snippet = SmsSnippet()
        if addConfirmationOptions:
            # create some confirmation options
            conf = UIConfirmSnippet({})
            conf.requestId = self.refId
            
            confOpts = UIConfirmationOptions()
            confOpts.submitCommands = [SendCommands([conf, StartRequest(False, "^smsConfirmation^=^yes^")])]
            confOpts.confirmCommands = confOpts.submitCommands
            
            cancel = UICancelSnippet({})
            cancel.requestId = self.refId
            
            confOpts.cancelCommands = [SendCommands([cancel, StartRequest(False, "^smsConfirmation^=^cancel^")])]
            confOpts.denyCommands = confOpts.cancelCommands
            
            confOpts.denyText = snippetButtons['denyText'][language]
            confOpts.cancelLabel = snippetButtons['cancelLabel'][language]
            confOpts.submitLabel = snippetButtons['submitLabel'][language]
            confOpts.confirmText = snippetButtons['confirmText'][language]
            confOpts.cancelTrigger = snippetButtons['cancelTrigger'][language]
            
            snippet.confirmationOptions = confOpts
            
        snippet.smss = [sms]
        
        createAnchor.views = [askCreateView, snippet]
        
        return createAnchor
            
    def createNewMessage(self, phone, person):
        # create a new domain object the sms...
        x = SmsSms()
        x.recipients = [phone.number]
        msgRecipient = PersonAttribute()
        msgRecipient.object = Person()
        msgRecipient.object.identifier = person.identifier
        msgRecipient.data = phone.number
        msgRecipient.displayText = person.fullName
        x.msgRecipients = [msgRecipient]
        x.outgoing = True
        answer = self.getResponseForRequest(DomainObjectCreate(self.refId, x))
        if ObjectIsCommand(answer, DomainObjectCreateCompleted):
            answer = DomainObjectCreateCompleted(answer)
            x = SmsSms()
            x.outgoing = True
            x.identifier = answer.identifier
            return x
        else:
            return None
        
    def getSmssForIdentifier(self, identifier):
        # fetch the current version
        retrieveCMD = DomainObjectRetrieve(self.refId)
        x = SmsSms()
        x.identifier = identifier
        retrieveCMD.identifiers = [x]
        answer = self.getResponseForRequest(retrieveCMD)
        if ObjectIsCommand(answer, DomainObjectRetrieveCompleted):
            answer = DomainObjectRetrieveCompleted(answer)
            if len(answer.objects) > 1:
                self.logger.warning("I do not support multiple messages!")
            result = SmsSms()
            result.initializeFromPlist(answer.objects[0].to_plist())
            return result
        else:
            return None
        
    def askAndSetMessage(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, False, "CreateSms#smsMissingMessage", random.choice(responses['askForMessage'][language]), language)

        smsText = self.getResponseForRequest(createAnchor)
        # update the domain object
        
        updateCMD = DomainObjectUpdate(self.refId)
        updateCMD.identifier = sms
        updateCMD.addFields = SmsSms()
        updateCMD.setFields = SmsSms()
        updateCMD.setFields.message = smsText
        updateCMD.removeFields = SmsSms()
        
        answer = self.getResponseForRequest(updateCMD)
        if ObjectIsCommand(answer, DomainObjectUpdateCompleted):
            return sms
        else:
            return None
            
    def showUpdateAndAskToSend(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, True, "CreateSms#updatedMessageBody", random.choice(responses['showUpdate'][language]), language)
        
        response = self.getResponseForRequest(createAnchor)
        match = re.match("\^smsConfirmation\^=\^(?P<answer>.*)\^", response)
        if match:
            response = match.group('answer')
        
        return response
    
    def cancelSms(self, sms, language):
        # cancel the sms
        cancelCMD = DomainObjectCancel(self.refId)
        cancelCMD.identifier = SmsSms()
        cancelCMD.identifier.identifier = sms.identifier
        
        answer = self.getResponseForRequest(cancelCMD)
        if ObjectIsCommand(answer, DomainObjectCancelCompleted):
            createAnchor = UIAddViews(self.refId)
            createAnchor.dialogPhase = createAnchor.DialogPhaseCanceledValue
            cancelView = UIAssistantUtteranceView()
            cancelView.dialogIdentifier = "CreateSms#wontSendSms"
            cancelView.text = cancelView.speakableText = random.choice(responses['cancelSms'][language])
            createAnchor.views = [cancelView]
            
            self.sendRequestWithoutAnswer(createAnchor)
            self.complete_request()
        else:
            self.say(random.choice(responses['cancelFail'][language]))
            self.complete_request()
    
    def askForClarification(self, sms, language):
        createAnchor = self.createSmsSnippet(sms, True, "CreateSms#notReadyToSendSms", random.choice(responses['clarification'][language]), language)
        
        response = self.getResponseForRequest(createAnchor)
        match = re.match("\^smsConfirmation\^=\^(?P<answer>.*)\^", response)
        if match:
            response = match.group('answer')
            
        return response
        
    def message(self, phone, person, language):
        smsObj = self.createNewMessage(phone, person)
        if smsObj == None:
            self.say(random.choice(responses['createSmsFail'][language]))
            self.complete_request()
            return
        smsObj = self.askAndSetMessage(smsObj, language)
        if smsObj == None:
            self.say(random.choice(responses['updateSmsFail'][language]))
            self.complete_request()
            return
        satisfied = False
        state = "SHOW"
        
        # lets define a small state machine 
        while not satisfied:
            smsObj = self.getSmssForIdentifier(smsObj.identifier)
            if smsObj == None:
                self.say(u"對不起，我搞丟你的簡訊了")
                self.complete_request()
                return
            
            if state == "SHOW":
                instruction = self.showUpdateAndAskToSend(smsObj, language).strip().lower()
                self.logger.info(u"## SHOW ## {0} ##########".format(instruction))
                if any(k in instruction for k in (questions['answerSEND'][language])):
                    state = "SEND"
                    continue
                if any(k in instruction for k in (questions['answerCANCEL'][language])):
                    state = "CLARIFY"
                    continue
                self.say(random.choice(responses['mustRepeat'][language]))
                continue
            
            elif state == "WRITE":
                smsObj = self.askAndSetMessage(smsObj, language)
                if smsObj == None:
                    self.say(random.choice(responses['updateSmsFail'][language]))
                    self.complete_request()
                    return
                state = "SHOW"
                continue
            
            elif state == "CLARIFY":
                instruction = self.askForClarification(smsObj, language).strip().lower()
                self.logger.info(u"## CLARIFY ## {0} ##########".format(instruction))
                if any(k in instruction for k in (questions['answerSEND'][language])):
                    state = "SEND"
                    continue
                if any(k in instruction for k in (questions['answerCANCEL'][language])):
                    state = "CANCEL"
                    continue
                if any(k in instruction for k in (questions['answerUPDATE'][language])):
                    state = "WRITE"
                    continue
                if any(k in instruction for k in (questions['answerREVIEW'][language])):
                    state = "SHOW"
                    continue
                self.say(random.choice(responses['mustRepeat'][language]))
                continue
            
            elif state == "CANCEL":
                self.cancelSms(smsObj, language)
                satisfied = True
                continue
            
            elif state == "SEND":
                self.finalSend(smsObj, language)
                satisfied = True
                continue
        
    def searchUserByName(self, personToLookup):
        search = PersonSearch(self.refId)
        search.scope = PersonSearch.ScopeLocalValue
        search.name = personToLookup
        answerObj = self.getResponseForRequest(search)
        if ObjectIsCommand(answerObj, PersonSearchCompleted):
            answer = PersonSearchCompleted(answerObj)
            return answer.results if answer.results != None else []
        else:
            raise StopPluginExecution("Unknown response: {0}".format(answerObj))
        return []
        
    def findPhoneForNumberType(self, person, numberType, language):         
        # first check if a specific number was already requested
        phoneToMessage = None
        if numberType != None:
            # try to find the phone that fits the numberType
            phoneToMessage = filter(lambda x: x.label == numberType, person.phones)
        else:
            favPhones = filter(lambda y: y.favoriteVoice if hasattr(y, "favoriteVoice") else False, person.phones)
            if len(favPhones) == 1:
                phoneToMessage = favPhones[0]
        if phoneToMessage == None:
            # lets check if there is more than one number
            if len(person.phones) == 1:
                if numberType != None:
                    self.say(errorNumberNotPresent.format(numberTypesLocalized[numberType][language], person.fullName))
                phoneToMessage = person.phones[0]
            else:
                # damn we need to ask the user which one he wants...
                while(phoneToMessage == None):
                    root = UIAddViews(self.refId)
                    root.dialogPhase = root.DialogPhaseClarificationValue
                    
                    utterance = UIAssistantUtteranceView()
                    utterance.dialogIdentifier = "ContactDataResolutionDucs#foundAmbiguousPhoneNumberForContact"
                    utterance.speakableText = utterance.text = responses['selectNumber'][language].format(person.fullName)
                    utterance.listenAfterSpeaking = True
                    
                    root.views = [utterance]
                    
                    lst = UIDisambiguationList()
                    lst.items = []
                    lst.speakableSelectionResponse = "OK!"
                    lst.listenAfterSpeaking = True
                    lst.selectionResponse = "OK"
                    root.views.append(lst)
                    for phone in person.phones:
                        numberType = phone.label
                        item = UIListItem()
                        item.title = ""
                        item.text = u"{0}: {1}".format(numberTypesLocalized[numberType][language], phone.number)
                        item.selectionText = item.text
                        item.speakableText = u"{0}  ".format(numberTypesLocalized[numberType][language])
                        item.object = phone
                        item.commands = [SendCommands(commands=[StartRequest(handsFree=False, utterance=numberTypesLocalized[numberType][language])])]
                        lst.items.append(item)
                        
                    answer = self.getResponseForRequest(root)
                    numberType = self.getNumberTypeForName(answer, language)
                    if numberType != None:
                        matches = filter(lambda x: x.label == numberType, person.phones)
                        if len(matches) == 1:
                            phoneToMessage = matches[0]
                        else:
                            self.say(errorNumberTypes[language])
                    else:
                        self.say(errorNumberTypes[language])
        return phoneToMessage
    
    def getNumberTypeForName(self, name, language):
        # q&d
        if name != None:
            if name.lower() in namesToNumberTypes[language]:
                return namesToNumberTypes[language][name.lower()]
            else:
                for key in numberTypesLocalized.keys():
                    if numberTypesLocalized[key][language].lower() == name.lower():
                        return numberTypesLocalized[key][language]
        return None
        
    def presentPossibleUsers(self, persons, language):
        root = UIAddViews(self.refId)
        root.dialogPhase = root.DialogPhaseClarificationValue
        utterance = UIAssistantUtteranceView()
        utterance.dialogIdentifier = "ContactDataResolutionDucs#disambiguateContact"
        utterance.text = responses['select'][language]
        utterance.speakableText = responses['select'][language] 
        utterance.listenAfterSpeaking = True
        root.views = [utterance]
        # create a list with all the possibilities 
        lst = UIDisambiguationList()
        lst.items = []
        lst.speakableSelectionResponse = "OK!"
        lst.listenAfterSpeaking = True
        lst.selectionResponse = "OK"
        root.views.append(lst)
        for person in persons:
            item = UIListItem()
            item.object = person 
            item.selectionResponse = person.fullName
            item.selectionText = person.fullName
            item.title = person.fullName
            item.commands = [SendCommands([StartRequest(False, "^phoneCallContactId^=^urn:ace:{0}".format(person.identifier))])]
            lst.items.append(item)
        return root
    
    #@register("en-US", "(Write|Send)( a)?( new)? (message|sms) to (?P<recipient>[\w ]+?)$")
    @register("en-US", u"(.*傳.*訊(.*))")
    @register("de-DE", "(Sende|Schreib.)( eine)?( neue)? (Nachricht|sms) an (?P<recipient>[\w ]+?)$")
    def sendSMS(self, speech, lang, regex):
        self.logger.info(u"####### ShortMessage Start Here ##########")
        recipient = re.findall(ur".*傳.*給(.*)",speech)
        if recipient == []:
            recipient = self.ask(u"請問要傳給誰？")
        else:
            recipient = recipient[0]
        
        possibleRecipients = self.searchUserByName(recipient)
        personToMessage = None
        if len(possibleRecipients) > 0:
            if len(possibleRecipients) == 1:
                personToMessage = possibleRecipients[0]
            else:
                identifierRegex = re.compile("\^phoneCallContactId\^=\^urn:ace:(?P<identifier>.*)")
                #  multiple users, ask user to select
                while(personToMessage == None):
                    strUserToMessage = self.getResponseForRequest(self.presentPossibleUsers(possibleRecipients, lang))
                    self.logger.debug(strUserToMessage)
                    # maybe the user clicked...
                    identifier = identifierRegex.match(strUserToMessage)
                    if identifier:
                        strUserToMessage = identifier.group('identifier')
                        self.logger.debug(strUserToMessage)
                    for person in possibleRecipients:
                        if person.fullName == strUserToMessage or person.identifier == strUserToMessage:
                            personToMessage = person
                    if personToMessage == None:
                        # we obviously did not understand him.. but probably he refined his request... call again...
                        self.say(errorNumberTypes[lang])
                    
            if personToMessage != None:
                self.message(self.findPhoneForNumberType(personToMessage, None, lang), personToMessage, lang)
                self.complete_request()
                #return # complete_request is done there
        self.say(responses['notFound'][lang])                         
        self.complete_request()
        