#!/usr/bin/env python3

import argparse
import os
import configparser
import requests
import getpass
import json
from bs4 import BeautifulSoup

__VERSION__ = '1.0.0'


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
    parser = BeautifulSoup(auth_page.text, 'html.parser')

    data_mac = parser.select('input[id="mac"]')[0].get('value')
    data_wlanacname = parser.select('input[id="wlanacname"]')[0].get('value')
    data_url = parser.select('input[id="url"]')[0].get('value')
    data_nasip = parser.select('input[id="nasip"]')[0].get('value')
    data_wlanuserip = parser.select('input[id="wlanuserip"]')[0].get('value')

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

    data_cookies = auth_page.cookies.get('JSESSIONID')

    cookies_data = {
        'JSESSIONID': data_cookies,
        'failCounter': '0'
    }

    # Sending authentication information
    print('(3/5) Sending authentication information...')
    host = rdr_url[7:].split('/')[0]
    str_return = session.post('http://%s/zportal/login/do' % host, data=form_data, cookies=cookies_data)
    json_return = json.loads(str_return.text)
    if not json_return['result'] == 'success':
        print('----- Failed.')
        print(json_return)
        exit(2)

    # Extract session data
    print('(4/5) Extracting session data...')
    cookies_next = {
        'JSESSIONID': data_cookies,
        'username': data_username,
        'password': data_pwd,
        'rememberPassword': 'true',
        'failCounter': '0',
        'serviceId': '',
        'userIndex': auth_page.cookies.get('userIndex')
    }
    # TODO: Set referrer
    session.get('http://%s/zportal/goToAuthResult' % host, cookies=cookies_next)

    # Saving current session
    print('(5/5) Saving current session...')
    ini = configparser.ConfigParser()
    ini.read(config_file)
    ini['last'] = {'url': rdr_url}
    with open(config_file, 'w') as f:
        ini.write(f)

    # Done
    print('Connected.')


def do_disconnect():
    # Check for Internet connection
    session = requests.Session()
    rdr = session.get('http://cdn.ralf.ren/res/portal.html').text
    if not rdr == "Success":
        print("Internet is unavailable. No need to de-authenticate.")
        exit(3)



if __name__ == '__main__':
    bootstrap()
