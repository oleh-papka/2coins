import datetime


def get_current_month_dates():
    today = datetime.date.today()

    first_day = today.replace(day=1)

    next_month = today.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month.replace(day=1) - datetime.timedelta(days=1)

    return first_day, last_day
