# Flask-Imovies
## 使用 Flask 製作一個簡單的電影清單網頁。


### Flask 介紹
> flask 是 python中著名的web框架，其因為輕量化，和可以讓使用者自己擴充套建的原因，讓開發小型專案的速度非常快。

### Imovies
你是否喜歡看電影，但有時候又不知道要看什麼電影?
你是否想要建立一個專屬於你的電影清單，但又不知道從和做起?
Imovies 就是來幫你解決這些問題的!
Imovies 收集了 IMDB 上熱門和TOP250的電影，並讓使用者建立一個專屬於自己的電影清單。


### 使用方式
clone 到你的電腦中 
```powershell
    $ git clone https://github.com/weijay0804/Flask-Imovies.git
```

安裝相關套件
```powershell
    $ pip install -r requirements.txt
```

#### 設定環境變數
|||
| :------------: | :---------------: |
| MAIL_USERNAME | <your_email_username> |
| MAIL_PASSWORD      | <your_email_password> |

#### 執行程式
``` powershell
    $ flask run
```

#### 備註:
如果你在 Imovies 裡註冊帳號，使用的昰gmail的話，很遺憾的 Python 的 semtplib 不支援 OAuth2 驗證，
你必許前往 <https://myaccount.google.com> 中登入，並找到 "Allow less secure" 選項並啟用，如果你有安全上的疑慮，可以建立專門用來測試的第二隻帳號。





    