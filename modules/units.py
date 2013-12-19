#!/usr/bin/env python
'''
units.py - jenni Units Module
Copyright 2013, Michael Yanovich (yanovich.net)
Licensed under the Eiffel Forum License 2.

More info:
 * jenni: https://github.com/myano/jenni/
 * Phenny: http://inamidst.com/phenny/
'''

from modules import unicode as uc
import datetime as dt
import json
import re
import time
import web

exchange_rates = dict()
last_check = dt.datetime.now()
exchanges = ['mtgox', 'btce', 'rock', 'ripple', 'bitstamp', 'coinbase']


def btc_page():
    try:
        page = web.get('https://api.bitcoincharts.com/v1/markets.json')
    except Exception, e:
        print time.time(), e
        return False, 'Failed to reach bitcoincharts.com'
    return True, page

def btc_coinbase_page():
    try:
        page = web.get('https://coinbase.com/api/v1/currencies/exchange_rates')
    except Exception, e:
        print time.time(), e
        return False, 'Failed to reach coinbase.com'
    return True, page



def ppnum(num):
    return re.sub("(?!\..*)(\d)(?=(\d{3})+(?!\d))", r"\1,", "%.2f" % num)


def btc(jenni, input):
    '''.btc -- display the current prices for Bitcoins'''
    global exchange_rates
    global last_check
    now = dt.datetime.now()
    if (not exchange_rates) or (now - last_check > dt.timedelta(minutes=15)):
        status, page = btc_page()
        json_page = dict()
        if status:
            try:
                json_page = json.loads(page)
            except:
                #return jenni.say('I could not understand the response from the server. Please try again.')
                pass
        else:
            return jenni.reply(page)
        ## build internal state of exchange
        for each in json_page:
            if each['currency'] == 'USD':
                if 'USD' not in exchange_rates:
                    exchange_rates['USD'] = dict()
                exchange_rates['USD'][each['symbol'].replace(
                    'USD', '')] = each['close']
        last_check = dt.datetime.now()

        coinbase_status, coinbase_page = btc_coinbase_page()
        try:
            coinbase_json = json.loads(coinbase_page)
        except:
            #return jenni.say('I could not understand the response from the server. Please try again.(cb)')
            pass
        exchange_rates['USD']['coinbase'] = ppnum(float(coinbase_json['btc_to_usd']))

    response = '1 BTC (in USD) = '
    symbols = exchange_rates['USD'].keys()
    symbols.sort()
    for each in symbols:
        if each.replace('USD', '') in exchanges:
            response += '%s: %s | ' % (each, exchange_rates['USD'][each])
    response += 'lolcat (mtgox) index: $%s | ' % (ppnum(float(
        exchange_rates['USD']['mtgox']) * 160))
    response += 'Howells (mtgox) index: $%s | ' % (ppnum(float(
        exchange_rates['USD']['mtgox']) * 7500))
    response += 'last updated at: %s UTC' % (str(last_check))
    jenni.say(response)
btc.commands = ['btc']
btc.example = '.btc'
btc.rate = 5


def fbtc(jenni, input):
    try:
        page = web.get('http://thefuckingbitcoin.com/')
    except:
        return jenni.say('Could not access thefuckingbitcoin.com')
    price = re.search('<p id="lastPrice">(\S+)</p>', page)
    remarks = re.search('<p id="remark">(.*?)</p><p id="remarkL2">(.*?)</p>',
                        page)
    try:
        remarks = remarks.groups()
    except:
        return jenni.say('Could not find relevant information.')
    resp = str()
    resp += '1 BTC == %s USD. ' % price.groups()
    if remarks:
        resp += '%s %s' % (remarks[0], remarks[1])
    jenni.say(resp)
fbtc.commands = ['fbtc']
fbtc.example = '.fbtc'


if __name__ == '__main__':
    print __doc__.strip()
