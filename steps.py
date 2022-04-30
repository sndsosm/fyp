# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 18:27:23 2022

@author: Sondos
"""

import sqlite3
import datetime

import codecs, grpc, os
import lightning_pb2 as lnrpc, lightning_pb2_grpc as lightningstub
import pickle as cPickle
print("Opened database successfully")
import pickle as cPickle
name='lnd_db.db'
conn = sqlite3.connect(name)
from all_functions import *
#
#create_database(name)
Create_User(Name="Alice",cert=r'C:\Users\Sondos\.polar\networks\6\volumes\lnd\alice\tls.cert',macaroon=r'C:\Users\Sondos\.polar\networks\6\volumes\lnd\alice\data\chain\bitcoin\regtest\admin.macaroon',channel='127.0.0.1:10003')
Create_User(Name='Bob',cert=r'C:\Users\Sondos\Desktop\fyp\All Functions\bob\tls.cert',macaroon=r'C:\Users\Sondos\Desktop\fyp\All Functions\bob\admin.macaroon',channel='127.0.0.1:10004')
Create_User(Name='Carol',cert=r'C:\Users\Sondos\.polar\networks\6\volumes\lnd\carol\tls.cert',macaroon=r'C:\Users\Sondos\.polar\networks\6\volumes\lnd\carol\data\chain\bitcoin\regtest\admin.macaroon',channel='127.0.0.1:10005')
#
#OPEN_CHANNEL('Bob','Alice',500000)
#ADD_INVOICE('Alice',1000,'Bob')
#cursor=conn.cursor()
#lst1=cursor.execute("select * from invoics",)
##conn.commit()
#print(cursor.fetchall())
#SEND_PAYMENT('Alice','Bob')
#SETTLE_INVOICE(b'v%L+\xdc"\xf2$\xe7_t:\xb3H\x91\xeb\xe0\no\xdb\xaf\xff\xa19G\xce\xf1 $\xf1[\x90')
#print(s)
#CLOSE_CHANNEL('Bob','Alice')
#print(cPickle.loads(b"\x80\x04\x95d\x00\x00\x00\x00\x00\x00\x00\x8c\rlightning_pb2\x94\x8c\x11ChannelOpenUpdate\x94\x93\x94)R\x94}\x94\x8c\nserialized\x94C&\n$\n ,\x05\x8d\xcf\x8bY\xb2\xbc&)\xf0_\xe6\xd5\x08h\xf4\xff\xc7\xa3\x97\x02\xaf\xef\x15\xf2\xc2]/r'\x87\x18\x01\x94sb."))