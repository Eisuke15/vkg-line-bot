# 開発環境で試す方法
1. `source env/bin/activate`
1. トンネリング
    ```shell
    $ ngrok http 5000
    ```
    httpsの方のurlをコピー
1. `python main.py`でサーバー起動
1. line official account manager で、設定 -> Messaging api -> Webhook url に、`"コピーしたurl"/callback`を入力


