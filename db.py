# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:28:11 2024

@author: Jerry
"""

from supabase import create_client, Client
import os

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def error(e):
    print(f"exception: \n{e}\n" )
    return None

def promo_subscribed_users():
    try:
        res = supabase.table('users').select("*").eq('promo_subscribed', True).execute()
        if len(res.data) > 0:
            return res.data
        return None
    except Exception as e:
        return error(e)
    
def get_user_points(chatid):
    try:
        res = supabase.table('users').select("points").eq('chatid', chatid).execute()
        if len(res.data) > 0:
            return res.data[0]['points']
        return None
    except Exception as e:
        return error(e)

def get_user(chatid):
    try:
        res = supabase.table('users').select("*").eq('chatid', chatid).execute()
        if len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        return error(e)

def get_order(oid):
    try:
        res = supabase.table('orders').select("*").eq('id', oid).execute()
        if len(res.data) > 0:
            return res.data[0]
        return None
    except Exception as e:
        return error(e)

def get_all_orders():
    try:
        res = supabase.table('orders').select("*").execute() #.not_eq('payment_status', 'submitted').execute()
        return res.data
    except Exception as e:
        return error(e)

