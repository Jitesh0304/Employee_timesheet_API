from datetime import datetime, timedelta


def get_days_between_dates(start_date, end_date):
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

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
        difference =  - start_date
        return difference.days
    except Exception as e:
        return None