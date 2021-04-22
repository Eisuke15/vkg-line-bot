# 開発環境で試す方法
1. `source env/bin/activate`
1. `docker-compose up -d`でDB起動
1. `flask run`でデバッグ用のサーバー起動
1. 別のシェルでトンネリング
    ```shell
    $ ngrok http 5000
    ```
    httpsの方のurlをコピー
1. line official account manager で、設定 -> Messaging api -> Webhook url に、`"コピーしたurl"/callback`を入力


