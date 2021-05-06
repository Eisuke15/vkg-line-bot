# 開発環境で試す方法
1. postgresql、flaskデバッグサーバ、ngrokを起動
    ```sh
    $ docker-compose up
    ```

    ※ flaskのサーバではなく、gunicornで動かす場合は、`-f docker-compose.gunicorn.yml`のオプションをつける。

    ※ 初回は`--build`オプションをつける。
1. ngrok_1コンテナのコマンドライン出力から、httpsからはじまるurlを探し、コピー
1. line official account manager で、設定 -> Messaging api -> Webhook url に、`"コピーしたurl"/callback`を入力し、保存


# デプロイ
1. heroku側でデータベースのマイグレーションを行う。 `heroku run flask db upgrade`

