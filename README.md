# 開発環境で試す方法
1. `source env/bin/activate`
1. `gunicorn main:app`でサーバー起動
1. 別のシェルでトンネリング
    ```shell
    $ ngrok http 8000
    ```
    httpsの方のurlをコピー
1. line official account manager で、設定 -> Messaging api -> Webhook url に、`"コピーしたurl"/callback`を入力


