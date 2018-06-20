#!/usr/bin/env python3

import argparse
import os
import configparser

__VERSION__ = '1.0.0'


def bootstrap():
    parser = argparse.ArgumentParser(description='Joywise command-line authentication utility')
    subparsers = parser.add_subparsers()

    # jauth connect
    parser_connect = subparsers.add_parser('connect', aliases=['con'], help='Do the web authentication.')
    parser_connect.set_defaults(func=do_connect)

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
    pass


if __name__ == '__main__':
    bootstrap()
