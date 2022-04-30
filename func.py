# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 18:45:49 2022

@author: Sondos
"""
import numpy
import codecs, grpc, os
import invoices_pb2 as invoicesrpc, invoices_pb2_grpc as invoicesstub
import lightning_pb2 as lnrpc, lightning_pb2_grpc as lightningstub
import router_pb2 as routerrpc, router_pb2_grpc as routerstub
import sqlite3
import datetime
import pickle as cPickle
def wallet(m,ct,c):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.WalletBalanceRequest()
    response = stub.WalletBalance(request, metadata=[('macaroon', macaroon)])
    return response.confirmed_balance, response.unconfirmed_balance

import time


def open_ch(m,ct,c,x,a):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.OpenChannelRequest(
            sat_per_vbyte=60000,
            node_pubkey=codecs.decode(x, 'hex'),
            node_pubkey_string=x,
            local_funding_amount=a,
        )
    response = stub.OpenChannel(request, metadata=[('macaroon', macaroon)])
    for response in stub.OpenChannel(request, metadata=[('macaroon', macaroon)]):
            x=response
    return x

def info(m,ct,c):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.GetInfoRequest()
    response = stub.GetInfo(request, metadata=[('macaroon', macaroon)])
    return response.identity_pubkey

def chans_list(m,ct,c,x):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.ListChannelsRequest(
            active_only=False,
            public_only=False
        )
    response = stub.ListChannels(request, metadata=[('macaroon', macaroon)])
    receiver_key="\""+x+"\""
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
                    return [channel_id,capacity,local_balance,remote_balance]
        else:
            continue
        
def send_pay(m,ct,c,pay_req):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = routerstub.RouterStub(channel)
    request = routerrpc.SendPaymentRequest(
            payment_request=pay_req,
            timeout_seconds=20,
        ) 
    for response in stub.SendPayment(request, metadata=[('macaroon', macaroon)]):
            return response

def close_channel(macaroon1,cert1,channel1, chan_pt):
    macaroon = codecs.encode(open(macaroon1, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(cert1, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(channel1, ssl_creds)
    stub = lightningstub.LightningStub(channel)
    request = lnrpc.CloseChannelRequest(
        channel_point=chan_pt.channel_point,
    )      
    for response in stub.CloseChannel(request, metadata=[('macaroon', macaroon)]):
        return response
    
def settle_inv(m,ct,c,preimg):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = invoicesstub.InvoicesStub(channel)
    request = invoicesrpc.SettleInvoiceMsg(
        preimage=preimg,
    )       
    return stub.SettleInvoice(request, metadata=[('macaroon', macaroon)])

def cancel_invoice(m,ct,c,pay_hash,):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    cert = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel(c, ssl_creds)
    stub = invoicesstub.InvoicesStub(channel)
    request = invoicesrpc.CancelInvoiceMsg(
        payment_hash=pay_hash.encode(),)
    return stub.CancelInvoice(request, metadata=[('macaroon', macaroon)])
#
def Add_invoice(m,ct,c,amount,username2):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    ct = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(ct)
    channl = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channl)
    request = lnrpc.Invoice(
            memo=username2,
            value=numpy.int64(amount),
        )
    return stub.AddInvoice(request, metadata=[('macaroon', macaroon)])

def lookupinv(m,ct,c,rhash):
    macaroon = codecs.encode(open(m, 'rb').read(), 'hex')
    os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
    ct = open(ct, 'rb').read()
    ssl_creds = grpc.ssl_channel_credentials(ct)
    channl = grpc.secure_channel(c, ssl_creds)
    stub = lightningstub.LightningStub(channl)
    request = lnrpc.PaymentHash(
        r_hash=rhash,
    )
    return stub.LookupInvoice(request, metadata=[('macaroon', macaroon)])
    