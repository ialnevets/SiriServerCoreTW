#!/usr/bin/python
# -*- coding: utf-8 -*-

from uuid import uuid4
import cPickle
import logging
import sqlite3
import base64
import uuid

db_type = "mysql"
#db_type = "sqlite"

__database__ = "database.sqlite3"
__mysql_host__ = "localhost"
__mysql_user__ = "root"
__mysql_password__ = ""
__mysql_database__ = "server1010"

if db_type!="mysql" and db_type!="mysql":
    db_type!="sqlite"

if db_type == "mysql":
    try:
        import MySQLdb

    except:
        print "You must install MySQLdb to use MySQL with SiriServer. Try python-mysql or easy_install"
        exit()
else:
    try:
        import sqlite3
    except:
        print "You must install SQLITE to use SQLITE with SiriServer. Try python-mysql or easy_install"
        exit()


def setup():
    conn = getConnection()
    c = conn.cursor()
    if db_type == "mysql":
        c.execute("CREATE DATABASE IF NOT EXISTS server1010 DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;")
        c.execute("CREATE TABLE IF NOT EXISTS `assistants` (`id` int(255) unsigned NOT NULL AUTO_INCREMENT,`assistantId` text NOT NULL,`speechId` text,`censorSpeech` text NOT NULL,`timeZoneId` text NOT NULL,`language` text NOT NULL,`region` text NOT NULL,`firstName` text NOT NULL,`nickName` text NOT NULL,`date_created` datetime NOT NULL, PRIMARY KEY (`id`)) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;")
    else:
        c.execute("""
            create table if not exists assistants(assistantId text primary key, assistant assi)
            """)
    conn.commit()
    c.close()
    conn.close()

def getConnection():
    try:
        if db_type == "mysql":
            print "################ Using MySQL ################"
            return MySQLdb.connect(__mysql_host__, __mysql_user__, __mysql_password__, __mysql_database__, use_unicode=True,charset='utf8')
        else:
            print "################ Using sqlite3 ################"
            return sqlite3.connect(__database__, detect_types=sqlite3.PARSE_DECLTYPES, timeout=10.0, check_same_thread=False)
    except sqlite3.Error.OperationalError as e:
        logging.getLogger().error("Connecting to the internal database timed out, there are probably to many connections accessing the database")
        logging.getLogger().error(e)
    return None

class Assistant(object):
    def __init__(self):
        self.assistantId = None
        self.speechId= None    
        self.censorSpeech = None
        self.timeZoneId = None
        self.language = None
        self.region = None
        self.nickName = u''
        self.firstName=u''

if db_type == "sqlite":
    def adaptAssistant(assistant):
        return cPickle.dumps(assistant)

    def convertAssistant(fromDB):
        return cPickle.loads(fromDB)

    sqlite3.register_adapter(Assistant, adaptAssistant)
    sqlite3.register_converter("assi", convertAssistant)
