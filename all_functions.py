# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 18:16:48 2022

@author: Sondos
"""
import codecs, grpc, os
import invoices_pb2 as invoicesrpc, invoices_pb2_grpc as invoicesstub
import lightning_pb2 as lnrpc, lightning_pb2_grpc as lightningstub
import router_pb2 as routerrpc, router_pb2_grpc as routerstub
import sqlite3
import datetime

import pickle as cPickle
name='lnd_db.db'
def create_database(name):
    conn = sqlite3.connect(name)
    conn.execute('''CREATE TABLE USER
             (username           TEXT  PRIMARY KEY  NOT NULL,
             cert TEXT      NOT NULL,
             macaroon TEXT     NOT NULL,
             channel TEXT     NOT NULL,
             pubkey INT Not NULL,
             CONF_BALANCE  INT  NOT NULL,
             UNCONF_BALANCE  INT  NOT NULL)''')
    #
    #
    ##         
    conn.execute('''CREATE TABLE CHANNELS
             (CHANNEL_ID INT NOT NULL,
             ID_SENDER TEXT     NOT NULL,
             ID_RECEIVER TEXT    NOT NULL,
             CAPACITY INT NOT NULL,
             LOCAL_BALANCE INT NOT NULL,
             REMOTE_BALANCE INT NOT NULL,
             CHANNEL_POINT BLOB NOT NULL,
             PRIMARY KEY (CHANNEL_ID, CHANNEL_POINT, ID_SENDER, ID_RECEIVER),
             FOREIGN KEY (ID_SENDER) REFERENCES USER(username),
             FOREIGN KEY (ID_RECEIVER) REFERENCES USER(username))''')
    
    conn.execute('''CREATE TABLE TRANSACTIONS
             (DATE    TEXT        NOT NULL,
             ID_SENDER TEXT     NOT NULL,
             ID_RECEIVER TEXT    NOT NULL,
             AMOUNT INT NOT NULL,
             PAYMENT_PREIMAGE TEXT NOT NULL,
             PAYMENT_REQUEST TEXT     NOT NULL,
             PRIMARY KEY (DATE, ID_SENDER, ID_RECEIVER),
             FOREIGN KEY (ID_SENDER) REFERENCES USER(ID),
             FOREIGN KEY (ID_RECEIVER) REFERENCES USER(ID))''')
           
           
    conn.execute('''CREATE TABLE INVOICES
             (DATE    TEXT        NOT NULL,
             ID_SENDER INT     NOT NULL,
             ID_RECEIVER INT     NOT NULL,
             PAYMENT_REQUEST TEXT     NOT NULL,
             PAYMENT_HASH TEXT     NOT NULL,
             PRE_IMAGE TEXT     NOT NULL,
             AMOUNT INT NOT NULL,
             PRIMARY KEY (DATE, ID_SENDER, PAYMENT_REQUEST),
             FOREIGN KEY (ID_SENDER) REFERENCES USER(ID),
             FOREIGN KEY (PAYMENT_REQUEST) REFERENCES USER(ID))''')
                 
    print("Tables created successfully")
    
from func import *

def Create_User(Name,cert,macaroon,channel):
    Balance=0
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    pubkey=info(macaroon,cert,channel)
    balances=wallet(macaroon,cert,channel)
    lst= cursor.execute("insert into USER VALUES (?,?,?,?,?,?,?)", (Name,cert,macaroon,channel,pubkey,balances[0],balances[1]))
    conn.commit()
    cursor.close()

def Update_Balance_Positive(ID, Amount):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst=cursor.execute("select BALANCE from USER where ID = ?", (ID,))
    bal=cursor.fetchall()
    Balance0=bal[0][0]
    Balance1=Balance0+Amount
    lst1= cursor.execute("UPDATE USER SET BALANCE=? WHERE ID=?;", (Balance1, ID))
    conn.commit() 
    cursor.close()

 
def Update_Balance_Negative(ID, Amount):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst=cursor.execute("select BALANCE from USER where ID = ?", (ID,))
    bal=cursor.fetchall()
    Balance0=bal[0][0]
    Balance1=Balance0-Amount
    lst1= cursor.execute("UPDATE USER SET BALANCE=? WHERE ID=?;", (Balance1, ID))
    conn.commit() 
    cursor.close()
    
def Update_User_Balance(username1):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon=user1[0][2]
    cert=user1[0][1]
    channel=user1[0][3]
    balances=Get_Balance(cert,macaroon,channel)
    print(type(balances[0]))
    print(balances[1])
    lst2= cursor.execute("UPDATE USER SET CONF_BALANCE=? , UNCONF_BALANCE=? WHERE username=?;", (balances[0],balances[1],username1))
    conn.commit() 
    cursor.close()
def Get_Balance(cert,macaroon,channel):
    macaroon = codecs.encode(open(macaroon, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(cert, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(channel, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.WalletBalanceRequest()
    response = stub.WalletBalance(request, metadata=[('macaroon', macaroon)])
    return response.confirmed_balance, response.unconfirmed_balance


def Transaction(ID_Sender,ID_Receiver, Amount):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    Date= datetime.datetime.now()
    lst= cursor.execute("insert into TRANSACTIONS VALUES (?,?,?,?)", (Date,ID_Sender,ID_Receiver[0][0], Amount[0][0]))
    Update_Balance_Negative(ID_Sender,Amount[0][0])
    Update_Balance_Positive(ID_Receiver[0][0],Amount[0][0])
    cursor.close()

def Get_Sent_Trans(ID_Sender):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst=cursor.execute("select * from INVOICES where ID_SENDER = ?", (ID_Sender,))
    trans=cursor.fetchall()
    conn.commit()
    cursor.close()

    return trans

def Get_Received_Trans(ID_Receiver):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst=cursor.execute("select * from TRANSACTIONS where ID_RECEIVER = ?", (ID_Receiver,))
    trans=cursor.fetchall()
    conn.commit()
    cursor.close()
    return trans


def ADDINVOICE(ID_Sender,PAYMENT_REQUEST, Amount):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    Date= datetime.datetime.now()
    lst= cursor.execute("insert into INVOICES VALUES (?,?,?,?)", (Date,ID_Sender,PAYMENT_REQUEST, Amount))
    conn.commit()
    cursor.close()

def PAYINVOICE(ID_SENDER,PAYMENT_REQUEST):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    Date= datetime.datetime.now()
    lst= cursor.execute("SELECT ID_SENDER FROM INVOICES where PAYMENT_REQUEST =?", (PAYMENT_REQUEST,))
    ID=cursor.fetchall()
    lst1= cursor.execute("SELECT AMOUNT FROM INVOICES where PAYMENT_REQUEST =?", (PAYMENT_REQUEST,))
    amount=cursor.fetchall()
    Transaction(ID_SENDER, ID,amount)
    lst2= cursor.execute("DELETE FROM INVOICES where PAYMENT_REQUEST =?", (PAYMENT_REQUEST,))
    conn.commit()  
    cursor.close()

def ADD_INVOICE(username1,amount,username2):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    response = Add_invoice(macaroon1,cert1,channel1,amount,username2)
    rhash=response.r_hash
    r=lookupinv(macaroon1,cert1,channel1,rhash)
    Date= datetime.datetime.now()
    lst3= cursor.execute("INSERT into INVOICES VALUES (?,?,?,?,?,?,?)", (Date,username2,username1,r.payment_request,r.r_hash,r.r_preimage,amount,))
    conn.commit()  
    cursor.close()

def OPEN_CHANNEL(username1,username2,amount):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    lst2=cursor.execute("select * from USER where username = ?", (username2,))
    user2=cursor.fetchall()
    macaroon2=user2[0][2]
    cert2=user2[0][1]
    channel2=user2[0][3]
    pubkey2=user2[0][4]
    response=open_ch(macaroon1,cert1,channel1,pubkey2,500000)
    chan_pt=cPickle.dumps(response.chan_open, cPickle.HIGHEST_PROTOCOL)
    chan=chans_list(macaroon1,cert1,channel1,pubkey2)
    lst3= cursor.execute("INSERT into CHANNELS VALUES (?,?,?,?,?,?,?)", (chan[0],username1,username2,chan[1],chan[2],chan[3],sqlite3.Binary(chan_pt)))
    conn.commit()  
    cursor.close()

def CANCEL_INVOICE(username1):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    lst1=cursor.execute("select * from INVOICES where ID_RECEIVER = ?", (username1,))
    invoice=cursor.fetchall()
    pay_hash=invoice[0][3]
    cancel=cancel_invoice(macaroon1,cert1,channel1,pay_hash)
    Date= datetime.datetime.now()
    lst3= cursor.execute("DELETE from INVOICES where ID_RECEIVER =? ", (username1,))
    conn.commit()  
    cursor.close()

def SEND_PAYMENT(username1,username2):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    lst2=cursor.execute("select * from USER where username = ?", (username2,))
    user2=cursor.fetchall()
    macaroon2=user2[0][2]
    cert2=user2[0][1]
    channel2=user2[0][3]
    pubkey2=user2[0][4]
    lst3=cursor.execute("select * from INVOICES where ID_SENDER = ? AND ID_RECEIVER=?", (username2,username1,))
    invoice=cursor.fetchall()
    amount=invoice[0][6]
    pay_req=invoice[0][3]
    pay_hash=invoice[0][4]
    preimg=invoice[0][5]
    response=send_pay(macaroon2,cert2,channel2,pay_req)
    r=lookupinv(macaroon1,cert1,channel1,pay_hash)
    while (r.state!=1):
        r=lookupinv(macaroon1,cert1,channel1,pay_hash)
        if (r.state==1):
            
            Update_User_Balance(username1)
            Update_User_Balance(username2)
            lst4= cursor.execute("DELETE from INVOICES where PAYMENT_REQUEST=?", (pay_req,))
            conn.commit()
            Date= datetime.datetime.now()
            lst5=cursor.execute("INSERT into TRANSACTIONS VALUES (?,?,?,?,?,?)", (Date,username2,username1,amount,r.r_preimage,pay_req,))
            conn.commit()  
            SETTLE_INVOICE(preimg)
            cursor.close()

def SETTLE_INVOICE(preimg):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst=cursor.execute("select * from transactionS where PAYMENT_PREIMAGE=?", (preimg,))
    users=cursor.fetchall()
    user2=users[0][2]
#    preimg=users[0][6]
    lst1=cursor.execute("select * from USER where username = ?", (user2,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    response = settle_inv(macaroon1,cert1,channel1,preimg)
    return response
    
def CHANNEL_INFO(username1,username2):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    pubkey1=user1[0][4]
    lst2=cursor.execute("select * from USER where username = ?", (username2,))
    user2=cursor.fetchall()
    macaroon2=user2[0][2]
    cert2=user2[0][1]
    channel2=user2[0][3]
    pubkey2=user2[0][4]
    macaroon = codecs.encode(open(macaroon1, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(cert1, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(channel1, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.ListChannelsRequest(
            active_only=False,
            public_only=False
        )
    response = stub.ListChannels(request, metadata=[('macaroon', macaroon)])
    receiver_key="\""+pubkey2+"\""
    d=[]
    for i in range (len(response.channels)):
        b=str(response.channels[i])
        b=b.splitlines()
        for i in range(len(b[0:16])):
                y=b[i].split(": ")
                b[i]=y[1]
        if (b[1]==receiver_key):
                    channel_id=int(b[3])
                    capacity=int(b[4])
                    local_balance=int(b[5])
                    remote_balance=int(b[6])
                    cursor.close()
                    return [channel_id,capacity,local_balance,remote_balance]
        else:
            continue

def CLOSE_CHANNEL(username1,username2):
    conn = sqlite3.connect(name)
    cursor=conn.cursor()
    lst1=cursor.execute("select * from USER where username = ?", (username1,))
    user1=cursor.fetchall()
    macaroon1=user1[0][2]
    cert1=user1[0][1]
    channel1=user1[0][3]
    lst2=cursor.execute("select * from USER where username = ?", (username2,))
    user2=cursor.fetchall()
    macaroon2=user2[0][2]
    cert2=user2[0][1]
    channel2=user2[0][3]
    lst2=cursor.execute("select * from CHANNELS where ID_SENDER = ? AND ID_RECEIVER=?", (username1,username2,))
    channel_close=cursor.fetchall()
#    print(channel_close[0][6])
    chan_id=channel_close[0][0]
    chan_pt=cPickle.loads(channel_close[0][6])
    s=close_channel(macaroon1,cert1,channel1, chan_pt)
    Update_User_Balance(username1)
    Update_User_Balance(username2)
    lst3= cursor.execute("DELETE FROM CHANNELS where CHANNEL_ID=?", (chan_id,))
    conn.commit()  
    cursor.close()