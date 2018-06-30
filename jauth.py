#!/usr/bin/env python3

import argparse
import os
import configparser
import requests
import getpass
import json
from bs4 import BeautifulSoup

__VERSION__ = '1.0.0'
UA_STRING = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
            'AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Chrome/67.0.3396.87 ' \
            'Safari/537.36'

def bootstrap():
    parser = argparse.ArgumentParser(description='Joywise command-line authentication utility')
    subparsers = parser.add_subparsers()

    # jauth connect
    parser_connect = subparsers.add_parser('connect', aliases=['con'], help='Do the web authentication.')
    parser_connect.set_defaults(func=do_connect)

    # jauth disconnect
    parser_disconnect = subparsers.add_parser('disconnect', aliases=['dis'], help='De-authenticate and disconnect from'
                                                                                  'Internet.')
    parser_disconnect.set_defaults(func=do_disconnect)

    # jauth account
    parser_account = subparsers.add_parser('account', aliases=['acc'], help='Set-up the account for authentication.')
    parser_account.add_argument('username', type=str, help='Account for authentication.')
    parser_account.add_argument('password', type=str, help='Password of the account.')
    parser_account.set_defaults(func=do_account)

    # jauth version
    parser_version = subparsers.add_parser('version', aliases=['ver'], help="Show jauth's version.")
    parser_version.set_defaults(func=do_version)

    # Parse the arguments
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()
        exit(0)


def do_version(args):
    print('jauth %s' % __VERSION__)


def do_account(args):
    ini = configparser.ConfigParser()
    ini['account'] = {'username': args.username, 'password': args.password}

    config_file = os.path.join(os.path.expanduser('~'), ".jauth_config")
    with open(config_file, 'w') as f:
        ini.write(f)
        print('Account saved:')
        print('Username: %s' % args.username)
        print('Password: %s' % args.password)


def do_connect(args):

    # Redirect to authentication page
    session = requests.Session()
    rdr = session.get('http://cdn.ralf.ren/res/portal.html').text
    if rdr == "Success":
        print("Internet is available. No authentication needed.")
        exit(1)
    rdr_url = rdr[32:-12]
    print('(1/5) Redirecting to authentication page...')
    auth_page = session.get(rdr_url)

    # Gather form data for authentication
    print('(2/5) Gathering form data for authentication...')
    parser_auth = BeautifulSoup(auth_page.text, 'html.parser')

    data_mac = parser_auth.select('input[id="mac"]')[0].get('value')
    data_wlanacname = parser_auth.select('input[id="wlanacname"]')[0].get('value')
    data_url = parser_auth.select('input[id="url"]')[0].get('value')
    data_nasip = parser_auth.select('input[id="nasip"]')[0].get('value')
    data_wlanuserip = parser_auth.select('input[id="wlanuserip"]')[0].get('value')

    data_username = ''
    data_pwd = ''
    config_file = os.path.join(os.path.expanduser('~'), ".jauth_config")
    if not os.path.exists(config_file):
        data_username = input('----- Account for authentication:')
        data_pwd = getpass.getpass('----- Password of the account:')
    else:
        ini = configparser.ConfigParser()
        ini.read(config_file)
        data_username = ini.get('account', 'username')
        data_pwd = ini.get('account', 'password')

    form_data = {
        "qrCodeId": "请输入编号",
        "username": data_username,
        "pwd": data_pwd,
        "validCode": "验证码",
        "validCodeFlag": "false",
        "ssid": "",
        "mac": data_mac,
        "t": "wireless-v2",
        "wlanacname": data_wlanacname,
        "url": data_url,
        "nasip": data_nasip,
        "wlanuserip": data_wlanuserip
    }

    data_jsessionid = auth_page.cookies.get('JSESSIONID')
    cookies_data = {
        'JSESSIONID': data_jsessionid,
        'failCounter': '0'
    }

    headers_data = {
        'User-Agent': UA_STRING
    }

    # Sending authentication information
    print('(3/5) Sending authentication information...')
    host = rdr_url[7:].split('/')[0]
    auth_return = session.post('http://%s/zportal/login/do' % host,
                               data=form_data, cookies=cookies_data, headers=headers_data)
    json_return = json.loads(auth_return.text)
    if not json_return['result'] == 'success':
        print('----- Failed.')
        print(json_return)
        exit(2)

    # Extract session data
    print('(4/5) Extracting session data...')

    data_userindex = auth_return.cookies.get('userIndex')
    cookies_next = {
        'JSESSIONID': data_jsessionid,
        'username': data_username,
        'password': data_pwd,
        'rememberPassword': 'true',
        'failCounter': '0',
        'serviceId': '',
        'userIndex': data_userindex
    }

    success_page = session.get('http://%s/zportal/goToAuthResult' % host, cookies=cookies_next)
    parser_extract = BeautifulSoup(success_page.text, 'html.parser')

    data_userip = parser_extract.select('input[name="userIp"]')[0].get('value')
    data_deviceip = parser_extract.select('input[name="deviceIp"]')[0].get('value')
    data_usermac = parser_extract.select('input[id="userMac"]')[0].get('value')

    # Saving current session
    print('(5/5) Saving current session...')
    ini = configparser.ConfigParser()
    ini.read(config_file)

    ini['last'] = {
        # 'url': rdr_url,
        'host': host,
        'jsessionid': data_jsessionid,
        'userindex': data_userindex,
        'userip': data_userip,
        'deviceip': data_deviceip,
        'usermac': data_usermac
    }

    with open(config_file, 'w') as f:
        ini.write(f)

    # Done
    print('Connected.')


def do_disconnect(args):

    # Check for Internet connection
    session = requests.Session()
    rdr = session.get('http://cdn.ralf.ren/res/portal.html').text
    if not rdr == "Success":
        print("Internet is unavailable. No need to de-authenticate.")
        exit(3)

    # Building de-authentication data
    print('(1/2) Building de-authentication data...')
    config_file = os.path.join(os.path.expanduser('~'), ".jauth_config")
    if not os.path.exists(config_file):
        print('Configuration file not exist.')
        exit(4)

    ini = configparser.ConfigParser()
    ini.read(config_file)

    form_data = {
        "userName": ini.get('account', 'username'),
        "userIp": ini.get('last', 'userip'),
        "deviceIp": ini.get('last', 'deviceip'),
        "service.id": "",
        "autoLoginFlag": "false",
        "userMac": ini.get('last', 'usermac'),
        "operationType": "",
        "isMacFastAuth": "false"
    }

    cookies_data = {
        'JSESSIONID': ini.get('last', 'jsessionid'),
        'username': ini.get('account', 'username'),
        'password': ini.get('account', 'password'),
        'rememberPassword': 'true',
        'failCounter': '0',
        'serviceId': '',
        'userIndex': ini.get('last', 'userindex')
    }

    headers_data = {
        'User-Agent': UA_STRING
    }

    # Sending de-authentication data
    print('(2/2) Sending de-authentication data...')
    session = requests.Session()
    deauth_return = session.post('http://%s/zportal/logout' % ini.get('last', 'host'),
                                 data=form_data, cookies=cookies_data, headers=headers_data)

    parser_deauth = BeautifulSoup(deauth_return.text, 'html.parser')
    login_button_text = parser_deauth.select('button[id="relogin"]')[0].text.strip()

    if not login_button_text == '继续上网':
        print('----- Failed.')
        exit(5)

    # Done.
    print('Disconnected.')


if __name__ == '__main__':
    bootstrap()
