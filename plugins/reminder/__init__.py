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
import pytz
from fractions import Fraction
from pytz import timezone
from plugin import *
from siriObjects.baseObjects import ObjectIsCommand
from siriObjects.contactObjects import PersonSearch, PersonSearchCompleted
from siriObjects.reminderObjects import *
from siriObjects.systemObjects import SendCommands, StartRequest, \
	PersonAttribute, Person, DomainObjectCreate, DomainObjectCreateCompleted, \
	DomainObjectUpdate, DomainObjectUpdateCompleted, DomainObjectRetrieve, \
	DomainObjectRetrieveCompleted, DomainObjectCommit, DomainObjectCommitCompleted, \
	DomainObjectCancel, DomainObjectCancelCompleted
from siriObjects.uiObjects import UIDisambiguationList, UIListItem, \
	UIConfirmationOptions, ConfirmSnippet, UIConfirmSnippet, UICancelSnippet
from datetime import *
import random

def parse_time(self, time, language):
	tz = timezone(self.connection.assistant.timeZoneId)
	pmWords = ["pm", "tonight"]
	amWords = ["am"]
	pmSearch = re.compile(r'\b%s\b' % '\\b|\\b'.join(pmWords), re.IGNORECASE)
	amSearch = re.compile(r'\b%s\b' % '\\b|\\b'.join(amWords), re.IGNORECASE)
	m = re.match('(at)* (\d{1,2}) ([\w ]+)', str(time), re.IGNORECASE)
	hour = m.group(2)
	timehint = m.group(3)
	x = datetime.now(tz)
	if len(pmSearch.findall(time)) > 0:
		print "using PM"
		if hour == "12":
			pmtime = int(hour)
			correctTime = x.replace(hour=pmtime, minute=0, second=0, microsecond=0)
		if hour != "12":
			pmtime = int(hour) + 12
			correctTime = x.replace(hour=pmtime, minute=0, second=0, microsecond=0)
	if len(amSearch.findall(time)) > 0:
		print "using AM"
		if hour == "12":
			correctTime = x.replace(hour=23, minute=59, second=0, microsecond=0)
		if hour != "12":
			amtime = int(hour)
			correctTime = x.replace(hour=amtime, minute=0, second=0, microsecond=0)
	if correctTime < x:
		correctTime = correctTime + timedelta(days=1)
	
	return correctTime

def parse_number(s, language):
	# check for simple article usage (a, an, the)
	if re.match(res['articles'][language], s, re.IGNORECASE):
		return 1
	f = 0
	for part in s.split(' '):
		f += float(Fraction(part))
	return f


def parse_timer_length(t, language):
	seconds = None
	for m in re.finditer(res['timerLength'][language], t, re.IGNORECASE):
		seconds = seconds or 0
		unit = m.group(2)[0]
		count = parse_number(m.group(1), language)
		if unit == 'h':
			seconds += count * 3600
		elif unit == 'm':
			seconds += count * 60
		elif unit == 's':
			seconds += count
		else:
			seconds += count * 60

	return seconds

responses = {
'notFound': 
	{'de-DE': u"Entschuldigung, ich konnte niemanden in deinem Telefonbuch finden der so heißt",
	 'en-US': u"Sorry, I did not find a match in your phone book"
	},
'devel':
	{'de-DE': u"Entschuldigung, aber diese Funktion befindet sich noch in der Entwicklungsphase",
	 'en-US': u"Sorry this feature is still under development"
	},
 'select':
	{'de-DE': u"Wen genau?", 
	 'en-US': u"Which one?"
	},
'selectNumber':
	{'de-DE': u"Welche Telefonnummer für {0}",
	 'en-US': u"Which phone one for {0}"
	},
'mustRepeat': 
	{'de-DE': [u"Entschuldigung ich hab dich leider nicht verstanden."],
	 'en-US': [u"Sorry, I did not understand, please try again", u"Sorry, I don't know what you want"]
	 },
'askForMessage':
	{'de-DE': [u"Was willst du schreiben?", u"Was soll drin stehen?", u"Du kannst mir jetzt diktieren!"],
	 'en-US': [u"When should I remind you?", u"When would you like to be reminded?"]
	 },
'showUpdate': 
	{'de-DE': [u"Ich hab deine Nachricht geschrieben. Willst du sie jetzt senden?", u"OK. Willst du die Nachricht jetzt senden?"],
	 'en-US': [u"I updated your reminder. Ready to create it?", u"Ok, I got that, do you want to create it?", u"Thanks, do you want to create it now?"]
	 },
'cancelSms': 
	{'de-DE': [u"OK, I schick sie nicht.", u"OK, ich hab sie verworfen"],
	 'en-US': [u"OK, I won't create it.", u"OK, I deleted it."]
	 },
'cancelFail':
	{'de-DE': [u"Sorry, aber mir ist ein Fehler beim Abbrechen passiert"],
	 'en-US': [u"Sorry I could not properly cancel your reminder"]
	 },
'createSmsFail':
	{'de-DE': [u"Ich konnte keine neue Nachricht anlegen, sorry"],
	 'en-US': [u"I could not create a new reminder, sorry!"]
	 },
'updateSmsFail':
	{'de-DE': [u"Entschuldigung ich konnte die Nachricht nicht schreiben"],
	 'en-US': [u"Sorry, I could not update your reminder!"]
	 },
'sendSms':
	{'de-DE': [u"OK, ich verschicke die Nachricht"],
	 'en-US': [u"OK, I'll remind you!"]
	 },
'sendSmsFail':
	{'de-DE': [u"Umpf da ist was schief gelaufen, sorry"],
	 'en-US': [u"Hm something gone wrong, I could not send the message, I'm very sorry"]
	 },
'clarification':
	{'de-DE': [u"Fortfahren mit senden, abbrechen, anschauen oder ändern."],
	 'en-US': [u"Would you like to cancel, or change it?"]
	 }
}
res = {
	'articles': {
		'en-US': 'a|an|the'
	}, 'pauseTimer': {
		'en-US': '.*(pause|freeze|hold).*timer'
	}, 'resetTimer': {
		'en-US': '.*(cancel|reset|stop).*timer'
	}, 'resumeTimer': {
		'en-US': '.*(resume|thaw|continue).*timer'
	}, 'setTimer': {
		# 'en-US': '.*timer[^0-9]*(((([0-9/ ]*|a|an|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?))\s*(and)?)+)'
		'en-US': '.*in[^0-9]*(?P<length>([0-9/ ]|seconds?|secs?|minutes?|mins?|hours?|hrs?|and|the|an|a){2,})'
	}, 'showTimer': {
		'en-US': '.*(show|display|see).*timer'
	}, 'timerLength': {
		'en-US': '([0-9][0-9 /]*|an|a|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?)'
	}
}
day = {
	'articles': {
		'en-US': 'a|an|the'
	}, 'pauseTimer': {
		'en-US': '.*(pause|freeze|hold).*timer'
	}, 'resetTimer': {
		'en-US': '.*(cancel|reset|stop).*timer'
	}, 'resumeTimer': {
		'en-US': '.*(resume|thaw|continue).*timer'
	}, 'setHour': {
		# 'en-US': '.*timer[^0-9]*(((([0-9/ ]*|a|an|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?))\s*(and)?)+)'
		'en-US': '.*at(?P<hour>([0-9 /](?P<timeofday>[a-zA-Z]+?)$))'
	}, 'showTimer': {
		'en-US': '.*(show|display|see).*timer'
	}, 'timerLength': {
		'en-US': '([0-9][0-9 /]*|an|a|the)\s+(seconds?|secs?|minutes?|mins?|hours?|hrs?)'
	}
}
questions = {
'answerSEND': 
	{'de-DE': ['yes', 'senden'], # you must include yes
	 'en-US': ['yes', 'send']
	 },
'answerCANCEL':
	{'de-DE': ['cancel', 'abbrechen', 'stop', 'nein'],	# you must include cancel
	 'en-US': ['cancel', 'no', 'abort']
	 },
'answerUPDATE':
	{'de-DE': ['ändern', 'verändern'],
	 'en-US': ['change', 'update']
	 },
'answerREVIEW':
	{'de-DE': ['anschauen', 'zeigen', 'zeig'],
	 'en-US': ['review', 'view']
	 }
}

snippetButtons = {
'denyText':
	{'de-DE': "Cancel",
	 'en-US': "Cancel"
	 },
'cancelLabel':
	{'de-DE': "Cancel",
	 'en-US': "Cancel"
	 },
'submitLabel':
	{'de-DE': "Confirm",
	 'en-US': "Confirm"
	 },
'confirmText':
	{'de-DE': "Confirm",
	 'en-US': "Confirm"
	 },
'cancelTrigger':
	{'de-DE': "Deny",
	 'en-US': "Deny"
	 }
}

speakableDemitter={
'en-US': u", or ",
'de-DE': u', oder '}


errorNumberTypes= {
'de-DE': u"Ich habe dich nicht verstanden, versuch es bitte noch einmal.",
'en-US': u"Sorry, I did not understand, please try again."
}

errorNumberNotPresent= {
'de-DE': u"Ich habe diese {0} von {1} nicht, aber eine andere.",
'en-US': u"Sorry, I don't have a {0} number from {1}, but another."
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
		commitCMD.identifier = ReminderObject()
		commitCMD.identifier.identifier = sms.identifier
		
		answer = self.getResponseForRequest(commitCMD)
		if ObjectIsCommand(answer, DomainObjectCommitCompleted):
			answer = DomainObjectCommitCompleted(answer)
			# update the reminder object with current identifier and time stamp
			sms.identifier = answer.identifier
			lists = ReminderListObject()
			lists.name = "Reminders"
			sms.lists = lists
			# tell the user we created the reminder
			createAnchor = UIAddViews(self.refId)
			createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmedValue
			
			# create a view to ask for the message
			askCreateView = UIAssistantUtteranceView()
			askCreateView.dialogIdentifier = "CreateSms#sentSMS"
			askCreateView.text = askCreateView.speakableText = random.choice(responses['sendSms'][language])
			askCreateView.listenAfterSpeaking = False
			
		   
			snippet = ReminderSnippet()
			snippet.reminders = [sms]
			
			createAnchor.views = [askCreateView, snippet]
			
			self.sendRequestWithoutAnswer(createAnchor)
			self.complete_request()
		else:
			self.say(random.choice(responses['sendSmsFail'][language]))
			self.complete_request()
			
			
	def createSmsSnippet(self, sms, addConfirmationOptions, dialogIdentifier, text, language):
		createAnchor = UIAddViews(self.refId)
		createAnchor.dialogPhase = createAnchor.DialogPhaseConfirmationValue
		
		# create a view to ask for the time
		askCreateView = UIAssistantUtteranceView()
		askCreateView.dialogIdentifier = dialogIdentifier
		askCreateView.text = askCreateView.speakableText = text
		askCreateView.listenAfterSpeaking = True
		# create a snippet for the reminder
		snippet = ReminderSnippet()
		if addConfirmationOptions:
			# create some confirmation options
			conf = UIConfirmSnippet({})
			conf.requestId = self.refId
			
			confOpts = UIConfirmationOptions()
			confOpts.submitCommands = [SendCommands([conf, StartRequest(False, "^smsConfirmation^=^yes^")])]
			confOpts.confirmCommands = confOpts.submitCommands
			
			cancel = UICancelSnippet({})
			cancel.requestId = self.refId
			
			confOpts.cancelCommands = [SendCommands([cancel, StartRequest(False, "^smsConfirmation^=^cancel^, ^no^")])]
			confOpts.denyCommands = confOpts.cancelCommands
			
			confOpts.denyText = snippetButtons['denyText'][language]
			confOpts.cancelLabel = snippetButtons['cancelLabel'][language]
			confOpts.submitLabel = snippetButtons['submitLabel'][language]
			confOpts.confirmText = snippetButtons['confirmText'][language]
			confOpts.cancelTrigger = snippetButtons['cancelTrigger'][language]
			
			snippet.confirmationOptions = confOpts
			
		snippet.reminders = [sms]
		
		createAnchor.views = [askCreateView, snippet]
		
		return createAnchor
			
	def createNewMessage(self, content):
		# create a new domain object the sms...
		x = ReminderObject()
		x.important = False
		x.completed = False
		x.subject = content
		answer = self.getResponseForRequest(DomainObjectCreate(self.refId, x))
		if ObjectIsCommand(answer, DomainObjectCreateCompleted):
			answer = DomainObjectCreateCompleted(answer)
			x = ReminderObject()
			x.identifier = answer.identifier
			return x
		else:
			return None
		
	def getSmssForIdentifier(self, identifier):
		# fetch the current version
		retrieveCMD = DomainObjectRetrieve(self.refId)
		x = ReminderObject()
		x.identifier = identifier
		retrieveCMD.identifiers = [x]
		answer = self.getResponseForRequest(retrieveCMD)
		if ObjectIsCommand(answer, DomainObjectRetrieveCompleted):
			answer = DomainObjectRetrieveCompleted(answer)
			if len(answer.objects) > 1:
				self.logger.warning("I do not support multiple messages!")
			result = ReminderObject()
			result.initializeFromPlist(answer.objects[0].to_plist())
			return result
		else:
			return None
		
	def askAndSetMessage(self, sms, language):
		createAnchor = self.createSmsSnippet(sms, False, "CreateSms#smsMissingMessage", random.choice(responses['askForMessage'][language]), language)
		time = self.getResponseForRequest(createAnchor)
		tz = timezone(self.connection.assistant.timeZoneId)
		Date = datetime.now(tz)
		EndDate = None
		if "in" in time.lower():
			m = re.match(res['setTimer'][language], time, re.IGNORECASE)
			if m == None:
				self.say("Sorry, that\'s not a valid time.")
				self.complete_request()
				return
			timer_length = m.group('length')
			offsetlength = parse_timer_length(timer_length, language)
			offset = ReminderDateTimeTriggerOffset()
			offset.offsetValue = offsetlength
			offset.offsetTimeUnit = "Second"
			EndDate = Date + timedelta(seconds=offsetlength)
			trig = ReminderDateTimeTrigger()
			trig.timeZoneId = self.connection.assistant.timeZoneId
			trig.relativeTimeOffset = offset
		if "at" in time.lower():
			hourtoset = parse_time(self, time, language)
			EndDate = hourtoset
			trig = ReminderDateTimeTrigger()
			trig.timeZoneId = self.connection.assistant.timeZoneId
			trig.date = hourtoset
		if EndDate == None:
			self.say("Sorry, I didn\'t understand that")
			self.complete_request()
			return			
		# update the domain object		 
	 
		updateCMD = DomainObjectUpdate(self.refId)
		updateCMD.identifier = sms		  
		updateCMD.setFields = ReminderObject()
		updateCMD.setFields.trigger = trig
		updateCMD.setFields.important = False
		updateCMD.setFields.dueDate = EndDate
		updateCMD.setFields.completed = False
		updateCMD.setFields.dueDateTimeZoneId = trig.timeZoneId
		
		
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
		cancelCMD.identifier = ReminderObject()
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
		
	def message(self, content, language):
		smsObj = self.createNewMessage(content)
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
				self.say(u"Sorry I lost your sms.")
				self.complete_request()
				return
			
			if state == "SHOW":
				instruction = self.showUpdateAndAskToSend(smsObj, language).strip().lower()
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
	
	@register("en-US", u".*提醒.*")
	def sendSMS(self, speech, lang, regex):
		#提醒我明天要看棒球
		reminderStr = re.findall(u".*提醒(.*)",speech)[0]
		
		if reminderStr.count(u'我') > 0:
			reminderStr = reminderStr.replace("我","")

		self.logger.info("## Reminder # {0} #".format(speech))
		if reminderStr != None:
			self.message(reminderStr, lang)
			self.complete_request()
			return
		self.say(responses['notFound'][lang])						  
		self.complete_request()




