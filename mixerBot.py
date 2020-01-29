import requests
import json
import sys
import time

import os
import os.path
from os import path

from lomond import WebSocket
from lomond.persist import persist

#from threading import Thread
import threading

import config

def check_validity(token_info, f_refresh):
    while 1:
        if not f_refresh.is_set():
#            print((time.time() - token_info["start_time"] - token_info["expires_in"] - 10))
            if ((time.time() - token_info["start_time"] - (token_info["expires_in"] - 10))) >= 0:
                token_info["start_time"] = time.time()
                print('Tokens expired, refreshing')
                refresh(token_info)
                print('Done refreshing Tokens')
                token_info["update_token"] = True
                f_refresh.set()
            time.sleep(1)
        if f_refresh.is_set():
            time.sleep(1)
#            print("Refresh Set")
            continue

def get_code(token_info):
    code_data = {
        'client_id' : token_info["client_id"],
        'scope' : 'channel:details:self channel:analytics:self chat:chat chat:connect interactive:robot:self'
    }

    x = requests.post(token_info["auth_url"], data = code_data)
#    print(x.json())

    code = x.json()['code']
    print("Go to mixer.com/go and enter code from shotcode.txt")
    f = open("shortcode.txt", 'w+')
    f.write(code)
    f.close()
    handle = x.json()['handle']

    return True, handle

def authenticate(token_info):
    code_valid = False

    while True:

        if code_valid == False:
            code_valid, handle = get_code(token_info)

        x = requests.get('https://mixer.com/api/v1/oauth/shortcode/check/{}'.format(handle))
        x.status_code

        if x.status_code == 204:
            continue
        elif x.status_code == 403:
            print('User Denied')
            code_valid = False
            continue
        elif x.status_code == 404:
            print('Time Expired')
            code_valid = False
            continue
        elif x.status_code == 200:
            print('User Accepted')
            if path.exists('shortcode.txt') == True:
                os.remove('shortcode.txt')
                print('Shortcode.txt deleted')
            else:
                print('Shortcode.txt already deleted')
                break
            auth_code = x.json()['code']
            data = {
                'client_id' : token_info["client_id"],
                'code': '{}'.format(auth_code),
                'grant_type': 'authorization_code'
            }

            x = requests.post(token_info["token_url"], data = data)

            token_info["access_token"] = x.json()['access_token']
            token_info["refresh_token"] = x.json()['refresh_token']
            token_info["expires_in"] = x.json()['expires_in']
            print('Tokens aquired')
            f = open("token.txt", 'w+')
            f.write(token_info["refresh_token"])
            f.close()

def refresh(token_info):
    refresh_data = {
        'client_id' : token_info["client_id"],
        'refresh_token': token_info["refresh_token"],
        'grant_type': 'refresh_token'
    }

    x = requests.post(token_info["token_url"], data = refresh_data)

    token_info["access_token"] = x.json()['access_token']
    token_info["refresh_token"] = x.json()['refresh_token']
    token_info["expires_in"] = x.json()['expires_in']
    print('New Tokens aquired')


    f = open("token.txt", 'w+')
    f.write(token_info["refresh_token"])
    f.close()

def constellation(token_info, f_refresh):
    ws = WebSocket('wss://constellation.mixer.com')
    ws.add_header(str.encode('authorization'), str.encode('Bearer {}'.format(token_info["access_token"])))
    ws.add_header(str.encode('client-id'), str.encode(token_info["client_id"]))
    ws.add_header(str.encode('x-is-bot'), str.encode('true'))

    while 1:
        for event in persist(ws, ping_rate=30, poll=5, exit_event=f_refresh):

            if event.name == "ready":
                Method = {
                        'type': 'method',
                        'method': 'livesubscribe',
                        'params': {'events': ['channel:{}:followed'.format(token_info["channel_id"]),
                        'channel:{}:hosted'.format(token_info["channel_id"]),
                        'channel:{}:subscribed'.format(token_info["channel_id"]),
                        'channel:{}:resubShared'.format(token_info["channel_id"]),
    #                    'channel:{}:update'.format(token_info["channel_id"]),
                        'channel:{}:subscriptionGifted'.format(token_info["channel_id"]),
                        'channel:{}:skill'.format(token_info["channel_id"]),
                        ]},
                        'id': token_info["nonce"]
                    }
                ws.send_json(Method)

            elif event.name == "text":
                print(event.json)
                if event.json['type'] == 'reply':
                    print('The Server replies to you')
                    if event.json['error'] != None:
                        print('Something to see here')
                        print(event.json['error'])
                        sys.exit()
                    elif event.json['id'] != token_info["nonce"]:
                        print('Nonce Mismatch')
                        sys.exit()

                if event.json['type'] == 'event':
                    if event.json['event'] == 'hello':
                        print(' The Server greets you back')

                    elif event.json['event'] == 'live':
                        print('Something happened')
                        if event.json['data']['channel'] == 'channel:{}:followed'.format(token_info["channel_id"]):
                            if event.json['data']['payload']['following'] == True:
                                print('Someone is following you')
                                username = event.json['data']['payload']['user']['username']
                                print("Username: {}".format(username))
                                avatar_url = event.json['data']['payload']['user']['avatarUrl']
                                sparks = event.json['data']['payload']['user']['sparks']
                                print("Sparks: {}".format(sparks))
                            if event.json['data']['payload']['following'] == False:
                                print('Someone stopped following you')
                                username = event.json['data']['payload']['user']['username']
                                print(username)

                        elif event.json['data']['channel'] == 'channel:{}:hosted'.format(token_info["channel_id"]):
                            print('Someone is hosting you')

                        elif event.json['data']['channel'] == 'channel:{}:subscribed'.format(token_info["channel_id"]):
                            print('Someone has subscribed to you')

                        elif event.json['data']['channel'] == 'channel:{}:resubShared'.format(token_info["channel_id"]):
                            print('Someone has resubscribed to you')

                        elif event.json['data']['channel'] == 'channel:{}:subscriptionGifted'.format(token_info["channel_id"]):
                            print('Someone has gifted a subscription to you')

                        elif event.json['data']['channel'] == 'channel:{}:skill'.format(token_info["channel_id"]):
                            print('Someone has used a skill on you')
            elif event.name == 'pong' or event.name == 'ping' or event.name == 'poll':
                continue
            else:
                continue
                print(event.name)
        if f_refresh.is_set():
            print("Closing Websocket")
            ws.close()
            f_refresh.clear()
            continue

def main():
    start_time = time.time()
    token_info = {
        "access_token" : "lel",
        "refresh_token" : "lel",
        "expires_in" : 0.0,
        "start_time" : time.time(),
        "client_id" : config.CLIENTID,
        "channel_id" : config.CHANNELID,
        "nonce" : config.NONCE,
        "auth_url" : "https://mixer.com/api/v1/oauth/shortcode",
        "token_url" : "https://mixer.com/api/v1/oauth/token",
        "update_token" : False
    }

    f_refresh = threading.Event()

    check_alive = False
    constell_alive = False

    check = threading.Thread(target = check_validity, args = (token_info, f_refresh), daemon = True)
    constell = threading.Thread(target = constellation, args = (token_info, f_refresh), daemon = False)

    if path.exists('token.txt') == False:
        print('No previous Token found')
        authenticate(token_info)

    elif path.exists('token.txt') == True:
        print('Previous Token found, refreshing')
        f = open('token.txt', 'r')
        token_info["refresh_token"] = f.read()
        refresh(token_info)
        print('Done refreshing Tokens')

    while 1:
        if not check.isAlive():
            check.start()

        if not constell.isAlive():
            constell.start()

        time.sleep(10)
#    if not constell.isAlive():
#        print("constell dead")

#    check.start()

#    constellation(access_token, client_id)
#    while 1:
#        print('here')

#        if not constell.is_alive():
#            constell.start()


if __name__== "__main__":
  main()
