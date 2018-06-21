# jauth
Command-line web authentication utility for Joywise.  
[中文説明](https://github.com/CYRO4S/jauth/blob/master/README.md)

## Quick Start
1. Download `jauth.py` and make it executable.  
```wget --no-check-certificate https://raw.githubusercontent.com/CYRO4S/jauth/master/jauth.py && chmod +x jauth.py```  
2. Provide account & password.  
```./jauth.py account [username] [password]```  
3. Time for authentication, just do it.  
```./jauth.py connect```

## Requirements
* Machine running UNIX-like OSes, like Linux, FreeBSD and macOS. Compatible with Windows Sub-system for Linux.
* Python 3.
* Python 3 `requests` and `beautifulsoup4`. Install it by using `pip3 install requests beautifulsoup4`

## Other Information
* Settings stores at `~/.jauth_config`.
