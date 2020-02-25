import dateutil.parser
import datetime

def parse_date(date_str, eacsd_date=False):
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        date = dateutil.parser.parse(date_str, fuzzy=True, dayfirst=True)

    if eacsd_date:
        out_date_str = datetime.datetime.strftime(date, '%d%b%Y')
    else:
        out_date_str = datetime.datetime.strftime(date, '%d/%m/%Y')
    return out_date_str
