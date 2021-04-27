# 開発環境で試す方法
1. 仮想環境に入る `source env/bin/activate`
1. バックグラウンドでDB起動 `docker-compose up -d`
1. デバッグ用のサーバー起動 `python manage.py`
1. 別のシェルでトンネリング
    ```shell
    $ ngrok http 5000
    ```
    httpsの方のurlをコピー
1. line official account manager で、設定 -> Messaging api -> Webhook url に、`"コピーしたurl"/callback`を入力


