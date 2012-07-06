#!/usr/bin/python
# -*- coding: utf-8 -*-

from OpenSSL import crypto
from SiriCore import Siri
from db import Assistant
from httpClient import AsyncOpenHttp
from siriObjects.baseObjects import ObjectIsCommand, RequestCompleted
from siriObjects.speechObjects import Phrase, Recognition, SpeechRecognized, \
    Token, Interpretation, StartSpeech, SpeechFailure, StartSpeechRequest, \
    StartSpeechDictation, FinishSpeech, SpeechPacket
from siriObjects.systemObjects import StartRequest, SendCommands, CancelRequest, \
    CancelSucceeded, GetSessionCertificate, GetSessionCertificateResponse, \
    CreateSessionInfoRequest, CommandFailed, RollbackRequest
from siriObjects.uiObjects import UIAddViews, UIAssistantUtteranceView, UIButton
import PluginManager
import flac
import json
import pprint
import speex
import sqlite3
import time
import twisted
import uuid
import twisted
import db

if db.db_type == "mysql":
    import MySQLdb.cursors

class SiriProtocolHandler(Siri):
    __not_recognized = {"de-DE": u"Entschuldigung, ich verstehe \"{0}\" nicht.", "en-US": u"對不起，我不明白 {0} 的意思", "fr-FR": u"Désolé je ne comprends pas ce que \"{0}\" veut dire."}
    __websearch = {"de-DE": u"Websuche", "en-US": u"Websearch", "fr-FR": u"Rechercher sur le Web"}
    __scheduling_interval_timeout__ = 30
    __timeout_delay = 10
    
    def __init__(self, server, peer):
        Siri.__init__(self, server, peer)
        self.lastPing = 0
        self.pong = 0
        self.plugin_lastAceId = ""
        self.current_running_plugin = None
        self.dbConnection = server.dbConnection
        self.assistant = None
        self.speech = dict()
        self.httpClient = AsyncOpenHttp(self.handle_google_data)
        self.current_google_request = None
        self.current_location = None
        self.lastPingTime = time.time()
        self.timeoutschedule = twisted.internet.reactor.callLater(SiriProtocolHandler.__scheduling_interval_timeout__, self.checkTimeout)
        
    def seconds_since_last_ping(self):
        return time.time() - self.lastPingTime
    
    def connectionLost(self, reason):
        try:
            self.timeoutschedule.cancel()
        except:
            pass
        if self.current_google_request != None:
            self.current_google_request.cancel()
        #ensure all decoder/encoder attemps are closed
        for key in self.speech.keys():
            (decoder, encoder, _) = self.speech[key]
            if decoder:
                decoder.destroy()
            if encoder:
                encoder.finish()
                encoder.destroy()
        del self.speech
        self.current_running_plugin = None
        self.dbConnection = None
        self.httpClient = None
        Siri.connectionLost(self, reason)
    
    def checkTimeout(self):
        if self.seconds_since_last_ping() > SiriProtocolHandler.__timeout_delay:
            self.logger.info("Connection timed out")
            self.transport.loseConnection() 
        else:
            self.timeoutschedule = twisted.internet.reactor.callLater(SiriProtocolHandler.__scheduling_interval_timeout__, self.checkTimeout)  
    
    def handle_google_data(self, body, requestId, dictation):
        self.current_google_request = None
        if (body != None):
            googleAnswer = json.loads(body)
            for i in xrange(0,len(googleAnswer['hypotheses'])-1):
                utterance = googleAnswer['hypotheses'][i]['utterance']
                if len(utterance) == 1:
                    utterance = utterance.upper()
                else:
                    utterance = utterance[0].upper() + utterance[1:]
                googleAnswer['hypotheses'][i]['utterance'] = utterance
            self.process_recognized_speech(googleAnswer, requestId, dictation)
        else:
            self.send_object(SpeechFailure(requestId, "No connection to Google possible"))
            self.send_object(RequestCompleted(requestId))
        
    def received_ping(self, numOfPing):
        self.pong += 1
        self.lastPing = numOfPing
        self.lastPingTime = time.time()
        self.send_pong(self.pong)
        
    def process_recognized_speech(self, googleJson, requestId, dictation):
        possible_matches = googleJson['hypotheses']
        if len(possible_matches) > 0:
            best_match = possible_matches[0]['utterance']
            best_match_confidence = possible_matches[0]['confidence']
            self.logger.info(u"Best matching result: \"{0}\" with a confidence of {1}%".format(best_match, round(float(best_match_confidence) * 100, 2)))
            # construct a SpeechRecognized
            token = Token(best_match, 0, 0, 1000.0, True, True)
            interpretation = Interpretation([token])
            phrase = Phrase(lowConfidence=False, interpretations=[interpretation])
            recognition = Recognition([phrase])
            recognized = SpeechRecognized(requestId, recognition)
            
            if not dictation:
                if self.current_running_plugin == None:
                    plugin = PluginManager.getPluginForImmediateExecution(self.assistant.assistantId, best_match, self.assistant.language, (self.send_object, self.send_plist, self.assistant, self.current_location))
                    if plugin != None:
                        plugin.refId = requestId
                        plugin.connection = self
                        self.current_running_plugin = plugin
                        self.send_object(recognized)
                        self.current_running_plugin.start()
                    else:
                        self.send_object(recognized)
                        view = UIAddViews(requestId)
                        errorText = SiriProtocolHandler.__not_recognized[self.assistant.language] if self.assistant.language in SiriProtocolHandler.__not_recognized else SiriProtocolHandler.__not_recognized["en-US"]
                        errorView = UIAssistantUtteranceView()
                        errorView.text = errorText.format(best_match)
                        errorView.speakableText = errorText.format(best_match)
                        view.views = [errorView]
                        websearchText = SiriProtocolHandler.__websearch[self.assistant.language] if self.assistant.language in SiriProtocolHandler.__websearch else SiriProtocolHandler.__websearch["en-US"]
                        button = UIButton()
                        button.text = websearchText
                        cmd = SendCommands()
                        cmd.commands = [StartRequest(utterance=u"Google搜尋{0}".format(best_match))]
                        button.commands = [cmd]
                        view.views.append(button)
                        self.send_object(view)
                        self.send_object(RequestCompleted(requestId))
                elif self.current_running_plugin.waitForResponse != None:
                    # do we need to send a speech recognized here? i.d.k
                    self.current_running_plugin.response = best_match
                    self.current_running_plugin.refId = requestId
                    self.current_running_plugin.waitForResponse.set()
                else:
                    self.send_object(recognized)
                    self.send_object(RequestCompleted(requestId))
            else:
                self.send_object(recognized)
                self.send_object(RequestCompleted(requestId))
    
    def received_plist(self, plist):
        self.logger.debug("Got packet with class: {0}".format(plist['class']))
        self.logger.debug("packet with content:\n{0}".format(pprint.pformat(plist, width=40)))
        
        # first handle speech stuff
        
        if 'refId' in plist:
            # if the following holds, this packet is an answer to a request by a plugin
            if plist['refId'] == self.plugin_lastAceId and self.current_running_plugin != None:
                if self.current_running_plugin.waitForResponse != None:
                    # just forward the object to the 
                    # don't change it's refId, further requests must reference last FinishSpeech
                    self.logger.debug("Forwarding object to plugin")
                    self.plugin_lastAceId = None
                    self.current_running_plugin.response = plist if plist['class'] != "StartRequest" else plist['properties']['utterance']
                    self.current_running_plugin.waitForResponse.set()
                    return
        
        if ObjectIsCommand(plist, StartSpeechRequest) or ObjectIsCommand(plist, StartSpeechDictation):
            self.logger.debug("New start of speech received")
            startSpeech = None
            if ObjectIsCommand(plist, StartSpeechDictation):
                dictation = True
                startSpeech = StartSpeechDictation(plist)
            else:
                dictation = False
                startSpeech = StartSpeechRequest(plist)
    
            decoder = speex.Decoder()
            encoder = flac.Encoder()
            speexUsed = False
            if startSpeech.codec == StartSpeech.CodecSpeex_WB_Quality8Value:
                decoder.initialize(mode=speex.SPEEX_MODEID_WB)
                encoder.initialize(16000, 1, 16)
                speexUsed = True
            elif startSpeech.codec == StartSpeech.CodecSpeex_NB_Quality7Value:
                decoder.initialize(mode=speex.SPEEX_MODEID_NB)
                encoder.initialize(16000, 1, 16)
                speexUsed = True
            elif startSpeech.codec == StartSpeech.CodecPCM_Mono_16Bit_8000HzValue:
                encoder.initialize(8000, 1, 16)
            elif startSpeech.codec == StartSpeech.CodecPCM_Mono_16Bit_11025HzValue:
                encoder.initialize(11025, 1, 16)
            elif startSpeech.coded == StartSpeech.CodecPCM_Mono_16Bit_16000HzValue:
                encoder.initialize(16000, 1, 16)
            elif startSpeech.coded == StartSpeech.CodecPCM_Mono_16Bit_22050HzValue:
                encoder.initialize(22050, 1, 16)
            elif startSpeech.coded == StartSpeech.CodecPCM_Mono_16Bit_32000HzValue:
                encoder.initialize(32000, 1, 16)
            # we probably need resampling for sample rates other than 16kHz...
            
            self.speech[startSpeech.aceId] = (decoder if speexUsed else None, encoder, dictation)
        
        elif ObjectIsCommand(plist, SpeechPacket):
            self.logger.debug("Decoding speech packet")
            speechPacket = SpeechPacket(plist)
            if speechPacket.refId in self.speech:
                (decoder, encoder, dictation) = self.speech[speechPacket.refId]
                if decoder:
                    pcm = decoder.decode(speechPacket.packets)
                else:
                    pcm = SpeechPacket.data # <- probably data... if pcm
                encoder.encode(pcm)
            else:
                self.logger.debug("Got a speech packet that did not match any current request")
                
        elif plist['class'] == 'StartCorrectedSpeechRequest':
            self.process_recognized_speech({u'hypotheses': [{'confidence': 1.0, 'utterance': plist['properties']['utterance']}]}, plist['aceId'], False)
    
        elif ObjectIsCommand(plist, FinishSpeech):
            self.logger.debug("End of speech received")
            finishSpeech = FinishSpeech(plist)
            if finishSpeech.refId in self.speech:
                (decoder, encoder, dictation) = self.speech[finishSpeech.refId]
                if decoder:
                    decoder.destroy()
                flacBin = None
                if encoder:
                    encoder.finish()
                    flacBin = encoder.getBinary()
                    encoder.destroy()
                del self.speech[finishSpeech.refId]
                if flacBin != None:
                    self.logger.info("Sending flac to google for recognition")
                    try:
                        self.current_google_request = self.httpClient.make_google_request(flacBin, finishSpeech.refId, dictation, language=self.assistant.language, allowCurses=True)
                    except (AttributeError, TypeError):
                        self.logger.warning("Unable to find language record for this assistant. Try turning Siri off and then back on.")
                else:
                    self.logger.info("There was no speech")
            else:
                self.logger.debug("Got a finish speech packet that did not match any current request")
                
        elif ObjectIsCommand(plist, CancelRequest):
            # this is probably called when we need to kill a plugin
            # wait for thread to finish a send
            self.logger.debug("Should cancel current request")
            cancelRequest = CancelRequest(plist)
            if cancelRequest.refId in self.speech:
                (decoder, encoder, dictation) = self.speech[cancelRequest.refId]
                if decoder:
                    decoder.destroy()
                if encoder:
                    encoder.finish()
                    encoder.destory()
                del self.speech[cancelRequest.refId]
            if self.current_google_request != None:
                self.current_google_request.cancel()
                # if a google request is running (follow up listening..., plugin might get killed there by user)
                if self.current_running_plugin != None:
                    if self.current_running_plugin.waitForResponse != None:
                        self.current_running_plugin._abortPluginRun()
                        self.current_running_plugin.waitForResponse.set()
                        
            # if a plugin is running (processing, but not waiting for data from the device we kill it)   
            if self.current_running_plugin != None:
                if self.current_running_plugin.waitForResponse == None:
                    self.current_running_plugin._abortPluginRun()     
            
            self.send_object(CancelSucceeded(cancelRequest.aceId))
            
        elif ObjectIsCommand(plist, RollbackRequest):
            pass

        elif ObjectIsCommand(plist, GetSessionCertificate):
            getSessionCertificate = GetSessionCertificate(plist)
            sessionCA_DER = crypto.dump_certificate(crypto.FILETYPE_ASN1, self.server.sessionCACert)
            sessionCert_DER = crypto.dump_certificate(crypto.FILETYPE_ASN1, self.server.sessionCert)
            response = GetSessionCertificateResponse(getSessionCertificate.aceId, sessionCA_DER, sessionCert_DER)
            self.send_object(response)

        elif ObjectIsCommand(plist, CreateSessionInfoRequest):
            # how does a positive answer look like?
            createSessionInfoRequest = CreateSessionInfoRequest(plist)
            fail = CommandFailed(createSessionInfoRequest.aceId)
            fail.reason = "Not authenticated"
            fail.errorCode = 0
            self.send_object(fail)

            #self.send_plist({"class":"SessionValidationFailed", "properties":{"errorCode":"UnsupportedHardwareVersion"}, "aceId": str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
            
        elif plist['class'] == 'CreateAssistant':
            #create a new assistant
            helper = Assistant()     
            helper.assistantId = str.upper(str(uuid.uuid4())) 
            c = self.dbConnection.cursor()
            noError = True
            try:
                if db.db_type == "mysql":
                    c.execute("INSERT INTO `assistants` (assistantId,speechId,censorSpeech,timeZoneId,language,region,firstName,nickName,date_created) values (%s,%s,%s,%s,%s,%s,%s,%s,NOW())", (helper.assistantId, helper.speechId,"","","","","",""))
                else:
                    c.execute("insert into assistants(assistantId, assistant) values (?,?)", (helper.assistantId, helper))
                self.dbConnection.commit()
            except MySQLdb.Error, e:
                noError = False
                print e
            except sqlite3.Error: 
                noError = False
            c.close()
            if noError:
                self.assistant = helper
                self.send_plist({"class": "AssistantCreated", "properties": {"speechId": str(uuid.uuid4()), "assistantId": helper.assistantId}, "group":"com.apple.ace.system", "callbacks":[], "aceId": str(uuid.uuid4()), "refId": plist['aceId']})
            else:
                self.send_plist({"class":"CommandFailed", "properties": {"reason":"Database error", "errorCode":2, "callbacks":[]}, "aceId": str(uuid.uuid4()), "refId": plist['aceId'], "group":"com.apple.ace.system"})
            
        elif plist['class'] == 'SetAssistantData':
            # fill assistant 
            if self.assistant != None:
                try:
                    c = self.dbConnection.cursor()
                    objProperties = plist['properties'] 
                    self.assistant.censorSpeech = objProperties['censorSpeech']
                    self.assistant.timeZoneId = objProperties['timeZoneId']
                    self.assistant.language = objProperties['language']
                    self.assistant.region = objProperties['region']
                    #Record the user firstName and nickName                    
                    try:                        
                        self.assistant.firstName = objProperties["meCards"][0]["properties"]["firstName"].encode("utf-8")
                    except KeyError:
                        self.assistant.firstName = u''                        
                    try:                        
                        self.assistant.nickName = objProperties["meCards"][0]["properties"]["nickName"].encode("utf-8")       
                    except KeyError:
                        self.assistant.nickName = u''
                    #Done recording
                    if db.db_type == "mysql":
                        c.execute("UPDATE `assistants` set censorSpeech=%s,timeZoneId=%s,language=%s,region=%s,firstName=%s,nickName=%s  where assistantId = %s", (self.assistant.censorSpeech,self.assistant.timeZoneId, self.assistant.language,self.assistant.region,self.assistant.firstName,self.assistant.nickName,self.assistant.assistantId))
                    else:
                        c.execute("update assistants set assistant = ? where assistantId = ?", (self.assistant, self.assistant.assistantId))
                    self.dbConnection.commit()
                    c.close()
                except:
                    self.send_plist({"class":"CommandFailed", "properties": {"reason":"Database error", "errorCode":2, "callbacks":[]}, "aceId": str(uuid.uuid4()), "refId": plist['aceId'], "group":"com.apple.ace.system"})
                    self.logger.error("Database Error on setting assistant data")
            else:
                self.send_plist({"class":"CommandFailed", "properties": {"reason":"Assistant to set data not found", "errorCode":2, "callbacks":[]}, "aceId": str(uuid.uuid4()), "refId": plist['aceId'], "group":"com.apple.ace.system"})
                self.logger.warning("Trying to set assistant data without having a valid assistant")
        elif plist['class'] == 'LoadAssistant':
            try:
                if db.db_type == "mysql":                    
                    c = self.dbConnection.cursor(MySQLdb.cursors.DictCursor)
                    c.execute("SELECT * FROM `assistants` WHERE assistantId = %s", (plist['properties']['assistantId']))
                else:
                    c = self.dbConnection.cursor()
                    c.execute("select assistant from assistants where assistantId = ?", (plist['properties']['assistantId'],))
                self.dbConnection.commit()
                result = c.fetchone()
                c.close()
                if result == None:
                    self.send_plist({"class": "AssistantNotFound", "aceId":str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
                    self.logger.warning("Assistant not found in database!!")                        
                else:
                    if db.db_type == "mysql":
                    #Load the assistant Values
                        self.assistant=Assistant()
                        self.assistant.assistantId=result["assistantId"]
                        self.assistant.speechId=result["speechId"]
                        self.assistant.censorSpeech = result["censorSpeech"]
                        self.assistant.timeZoneId = result["timeZoneId"]
                        self.assistant.language = result["language"]
                        self.assistant.region = result["region"]
                        #Load the user info
                        self.assistant.firstName=result["firstName"]
                        self.assistant.nickName=result["nickName"]
                    else:
                        self.assistant = result[0]
                    if self.assistant.language == '' or self.assistant.language == None:
                        self.logger.error ("No language is set for this assistant")
                        if db.db_type == "mysql":
                            c.execute("DELETE from `assistants` where assistantId = %s", (plist['properties']['assistantId'],))
                        else:
                            c.execute("delete from assistants where assistantId = ?", (plist['properties']['assistantId'],))
                        self.dbConnection.commit()
                        self.send_plist({"class":"CommandFailed", "properties": {"reason":"Database error Assistant not found or language settings ", "errorCode":2, "callbacks":[]}, "aceId": str(uuid.uuid4()), "refId": plist['aceId'], "group":"com.apple.ace.system"})
                    else:                        
                        self.send_plist({"class": "AssistantLoaded", "properties": {"version": "20111216-32234-branches/telluride?cnxn=293552c2-8e11-4920-9131-5f5651ce244e", "requestSync":False, "dataAnchor":"removed"}, "aceId":str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
                c.close()
            except:
                self.send_plist({"class": "AssistantNotFound", "aceId":str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
                self.logger.warning("Database error on fetching assistant")
                
        elif plist['class'] == 'DestroyAssistant':
            try:
                c = self.dbConnection.cursor()
                if db.db_type == "mysql":
                    c.execute("DELETE from `assistants` where assistantId = %s", (plist['properties']['assistantId'],))
                else:
                    c.execute("delete from assistants where assistantId = ?", (plist['properties']['assistantId'],))
                self.dbConnection.commit()
                c.close()
                self.send_plist({"class": "AssistantDestroyed", "properties": {"assistantId": plist['properties']['assistantId']}, "aceId":str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
            except:
                self.send_plist({"class": "AssistantNotFound", "aceId":str(uuid.uuid4()), "refId":plist['aceId'], "group":"com.apple.ace.system"})
                self.logger.error("Database error on deleting assistant")
                
        elif plist['class'] == 'StartRequest':
            #this should also be handeled by special plugins, so lets call the plugin handling stuff
            self.process_recognized_speech({'hypotheses': [{'utterance': plist['properties']['utterance'], 'confidence': 1.0}]}, plist['aceId'], False)
        pass
