# jauth
命令行下的卓智 Web 認證工具。

## 快速開始
1. 下載 `jauth.py` 並賦予可執行權限。  
```wget --no-check-certificate https://raw.githubusercontent.com/CYRO4S/jauth/master/jauth.py && chmod +x jauth.py```  
2. 提供賬號與密碼。  
```./jauth.py account [學號] [密碼]```
3. 進行認證。  
```./jauth.py connect```

## 前置需求
* 類 UNIX 作業系統，如 Linux、 FreeBSD 和 macOS。 與 Windows Linux 子系統相容。
* 現亦與 Windows 相容。
* Python 3。
* Python 3 `requests` 與 `beautifulsoup4` 庫。 使用 `pip3 install requests beautifulsoup4` 來安裝。

## 其他資訊
* 偏好設定存儲於 `~/.jauth_config`.
