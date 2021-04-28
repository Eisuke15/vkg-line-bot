







def main(week):
    load_dotenv()
    db.init_app()
    todays_day = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).weekday()
    if todays_day in week:
        option = Cancellation.query.filter_by(day_of_the_week=todays_day)
        print(option)
        if option.count() == 0:
            remindtext = "体温を入力してね" + "\n" + os.environ["SPREADSHEET_URL"]
            pushText = TextSendMessage(text=remindtext)
            for group in Group.query.all():
                line_bot_api.push_message(to=group.group_id, messages=pushText)
        else:
            db.session.delete(option.first())
            db.session.commit()

if __name__ == "__main__":
    #曜日を指定する数字列をコマンドライン引数にとる。0~6で日~土
    week = list(map(int,sys.argv[1:]))
    main(week)
