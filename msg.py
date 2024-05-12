import sys

ALL_OFF = '\033[0m'
BOLD = '\033[1m'
BLUE = f'{BOLD}\033[34m'
GREEN = f'{BOLD}\033[32m'
RED = f'{BOLD}\033[31m'
YELLOW = f'{BOLD}\033[33m'

__all__ = ['plain', 'msg', 'msg2', 'ask', 'warning', 'error']


def plain(message):
    print(f'{BOLD}   {message}{ALL_OFF}')


def msg(message):
    print(f'{GREEN}==>{ALL_OFF}{BOLD} {message}{ALL_OFF}')


def msg2(message):
    print(f'{BLUE}  ->{ALL_OFF} {message}{ALL_OFF}')


def ask(message):
    print(f'{BLUE}::{ALL_OFF}{BOLD} {message}{ALL_OFF}')


def warning(message):
    print(f'{YELLOW}==> WARNING:{ALL_OFF}{BOLD} {message}{ALL_OFF}', file=sys.stderr)


def error(message):
    print(f'{RED}==> ERROR:{ALL_OFF}{BOLD} {message}{ALL_OFF}', file=sys.stderr)
