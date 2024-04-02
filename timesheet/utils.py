from datetime import datetime, timedelta
from django.utils import timezone



def get_week_nums_and_days_of_the_year(year):
    dt = {}
    for i in range(1, 54):
        start_of_year = datetime(year, 1, 1)
        start_of_week = start_of_year - timedelta(days=start_of_year.weekday()) + timedelta(weeks=i - 1)
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
        dates = [date for date in dates if date.year == year]
        # dt[i] = dates
        if not dates:
            pass
        else:
            dt[i] = dates
    return dt



# def get_week_nums_and_days_till_today(year, week):
#     dt = {}
#     for i in range(1, week+1):
#         first_day = datetime(year, 1, 1)
#         start_of_year = first_day - timedelta(days=first_day.weekday())
#         start_of_week = start_of_year + timedelta(weeks=i - 1)
#         dates = [start_of_week + timedelta(days=i) for i in range(7)]
#         # dt[i] = dates
#         if start_of_week.year != year:
#             dates = [date for date in dates if date.year == year]
#         if not dates:
#             pass
#         else:
#             dt[i] = dates
#     return dt

def get_week_nums_and_days_till_today(year, week):
    dt = {}
    for i in range(1, week+1):
        start_of_year = datetime(year, 1, 1)
        start_of_week = start_of_year - timedelta(days=start_of_year.weekday()) + timedelta(weeks=i - 1)
        dates = [start_of_week + timedelta(days=i) for i in range(7)]
        dates = [date for date in dates if date.year == year]
        # dt[i] = dates
        if not dates:
            pass
        else:
            dt[i] = dates
    return dt




# def get_all_days_of_the_week(year, week):
#     first_day_of_week = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()
#     dates_of_week = [first_day_of_week + timedelta(days=i) for i in range(7)]
#     return dates_of_week

def get_all_days_of_the_week(year, week):
    start_of_year = datetime(year, 1, 1)
    first_day_of_week = start_of_year - timedelta(days=start_of_year.weekday()) + timedelta(weeks=week - 1)
    dates_of_week = [first_day_of_week + timedelta(days=i) for i in range(7)]
    dates_of_week = [date for date in dates_of_week if date.year == year]
    return dates_of_week




# def get_current_and_previous_week_days(year, week):
#     if week == 1:
#         first_day_of_week = datetime.strptime(f'{year}-W{week}-1', '%Y-W%W-%w').date()
#         dates_of_week = [first_day_of_week + timedelta(days=i) for i in range(7)]
#         if first_day_of_week.year != year:
#             dates_of_week = [date for date in dates_of_week if date.year == year]
#         return dates_of_week
#     else:
#         dt = {}
#         if week >= 2 and week <= 53:
#             for i in range(week-1, week+1):
#                 first_day = datetime.strptime(f'{year}-W{i}-1', '%Y-W%W-%w').date()
#                 dates = [first_day + timedelta(days=i) for i in range(7)]
#                 # dt[i] = dates
#                 if first_day.year != year:
#                     dates = [date for date in dates if date.year == year]
#                 if not dates:
#                     pass
#                 else:
#                     dt[i] = dates
#         else:
#             pass
#         return dt


def get_current_and_previous_week_days(year, week):
    if week == 1:
        start_of_year = datetime(year, 1, 1)
        first_day_of_week = start_of_year - timedelta(days=start_of_year.weekday())
        dates_of_week = [first_day_of_week + timedelta(days=i) for i in range(7)]
        dates_of_week = [date for date in dates_of_week if date.year == year]
        return dates_of_week
    else:
        dt = {}
        if 2 <= week <= 53:
            for i in range(week-1, week+1):
                start_of_year = datetime(year, 1, 1)
                first_day_of_week = start_of_year - timedelta(days=start_of_year.weekday()) + timedelta(weeks=i - 1)
                dates = [first_day_of_week + timedelta(days=i) for i in range(7)]
                dates = [date for date in dates if date.year == year]
                dt[i] = dates
        return dt






def get_days_between_dates(start_date, end_date):
    try:
        # start_date = datetime.strptime(start_date, '%Y-%m-%d')
        # end_date = datetime.strptime(end_date, '%Y-%m-%d')

        days_between = []

        current_date = start_date
        while current_date <= end_date:
            days_between.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return days_between
    except Exception as e:
        return None



def get_number_of_days_btw_dates(start_date, end_date):
    try:
        # start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # difference = end_date - start_date
        # total_days = difference.days
        # return total_days
        difference = end_date - start_date
        return difference.days
    except Exception as e:
        return None




def check_date_format(dateone):
    try:
        check_one = datetime.strptime(dateone, "%Y-%m-%d").date()
        return check_one
    except Exception as e:
        return None
