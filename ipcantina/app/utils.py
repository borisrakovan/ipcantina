from datetime import date, timedelta, datetime, time
from app import app

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class DateUtils():
    @staticmethod
    def deadline_passed(dt):
        if dt.weekday == 0:
            deadline_date = dt
            deadline_time = 9
            deadline = datetime.combine(deadline_date, deadline_time)
            return datetime.now() > deadline

        # deadline_date = dt - timedelta(days=1)
        deadline_date = DateUtils.prev_working_day(dt)
        deadline_time = time(hour=app.config['ORDER_DEADLINE_HOUR'])
        deadline = datetime.combine(deadline_date, deadline_time)
        return datetime.now() > deadline

    # @staticmethod
    # def get_num_passed_days():
    #     today = datetime.today()
    #     weekday = today.weekday()
    #
    #     passed = weekday + 1
    #     if today.hour >= app.config['ORDER_DEADLINE_HOUR']:
    #         passed += 1
    #         if weekday == 4:
    #             passed = 0
    #
    #     return passed % 7 if weekday != 5 else 0

    @staticmethod
    def prev_working_day(day):
        if day.weekday() == 6:
            return day - timedelta(days=2)
        elif day.weekday() == 0:
            return day - timedelta(days=3)

        return day - timedelta(days=1)

    @staticmethod
    def next_working_day(day):
        if day.weekday() >= 4:
            return day + timedelta(days=7-day.weekday())

        return day + timedelta(days=1)

    @staticmethod
    def affected_week_monday():
        today = date.today()
        hour = datetime.now().hour
        if today.weekday() > 3 or (today.weekday() == 3 and hour >= 15):
            # next monday
            return today + timedelta(days=7-today.weekday())
        else:
            # current week's monday
            return DateUtils.monday_date()

    @staticmethod
    def affected_week_friday():
        return DateUtils.affected_week_monday() + timedelta(days=4)

    @staticmethod
    def svk_strings():
        return ["Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok"]

    @staticmethod
    def monday_to_friday_str():
        return "{} - {}".format(DateUtils.to_string(DateUtils.affected_week_monday()),
                                DateUtils.to_string(DateUtils.affected_week_friday()))

    @staticmethod
    def monday_date():
        today = date.today()
        return today - timedelta(days=today.weekday())

    # @staticmethod
    # def friday_date():
    #     today = date.today()
    #     return today + timedelta(days=4-today.weekday())

    @staticmethod
    def date_from_int(val):
        return DateUtils.affected_week_monday() + timedelta(days=val)

    @staticmethod
    def to_string(dt):
        return "{}.{}.".format(dt.day, dt.month)

    @staticmethod
    def svk_from_int(val):
        if val == 0:
            return "Pondelok"
        if val == 1:
            return "Utorok"
        if val == 2:
            return "Streda"
        if val == 3:
            return "Štvrtok"
        if val == 4:
            return "Piatok"
