import calendar, datetime, time
from time import strftime, mktime, strptime
from collections import OrderedDict
import typing

from dateutil.relativedelta import relativedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import emc.db as db
import emc.utils as utils

bp = Blueprint('index', __name__)

def get_pub_nights(future_day=None) -> typing.Tuple[float, str]:
    
    today = time.localtime() if future_day is None else time.gmtime(future_day)

    day = today.tm_mday
    month = today.tm_mon
    year = today.tm_year
        
    # this will mean that the last element of the first week of the respective month will be the first tuesday of the month
    pub = calendar.Calendar()
    pub.setfirstweekday(calendar.WEDNESDAY)
    tuesday = pub.monthdayscalendar(year, month)[0][-1]

    # pub is today!
    if day == tuesday and future_day is None:
        return datetime.datetime(year, month, tuesday).timestamp(), "Today, 8pm"
    # pub night is this month, and we haven't yet got to it
    elif day < tuesday:
        pubdate = datetime.datetime(year, month, tuesday)
    # we've already had this month's pub night
    else:
        # next month - using dateutil to deal with new years (12 + 1 would otherwise raise an error when making a date!)
        from datetime import datetime as dt

        next_month = dt.fromtimestamp(mktime(today)) + relativedelta(months=1)
        year = next_month.year
        month = next_month.month
        tuesday = pub.monthdayscalendar(year, month)[0][6]
        pubdate = dt(year, month, tuesday)

    pubmonth = time.strftime("%B", pubdate.timetuple())
    pubday = utils.prettyday(pubdate.day)
    return pubdate.timestamp(), f'{pubday} {pubmonth}, 8pm'

def events(sort=True) -> OrderedDict:

    # given changes to Dict in python 3.7, might be ok to use a normal Dict instead of OrderedDict
    events = OrderedDict()
    
    (pubsec, pubdisplay) = get_pub_nights()

    for _ in range(3):
            events[pubsec] = (pubdisplay, 'Pub night at the Red Squirrel, Lothian Road')

            # add 21 days to current pubdate (presumably because we know this is a safe number to add - minumum possible
            # number of days, i.e. between feb and march in a non-leap year)
            (pubsec, pubdisplay) = get_pub_nights(pubsec + (21 * 24 * 60 * 60))


    
    now = strftime('%Y-%m-%d')
    meets = db.get_meets(filter = f"firstnight >= '{now}' order by firstnight")

    

    for meet in meets:
        # start = mktime("%s" %strptime((meet['firstnight']), '%Y-%m-%d'))
        start = mktime(strptime(("%s" % (meet['firstnight'])), '%Y-%m-%d'))
        meetdate = utils.prettyrange(start, meet['nights'])
        meetdetails = "Meet at %s" % (utils.meet_name(meet))
        events[start] = (meetdate, meetdetails)

        # try:
        #     booking = mktime(strptime(("%s" % (meet['booking'])), '%Y-%m-%d'))
        #     if booking >= time():
        #         bookingdate = utils.prettydate(booking)
        #         events.add(booking,
        #                     ('%s, 6pm' % bookingdate, 'Bookings open for %s (%s)' % (meetdetails, meetdate)))
        # except:
        #     pass

    # return sorted(events.items()) 

    if sort:
        return OrderedDict(sorted(events.items()))

    return events

# if sorted is True else events 
        

def get_photos():
    pass

@bp.route('/')
def index():
    # only want the next 8 events for the table on the homepage (annoyingly, you can't subset even OrderedDicts by index / range)
    upcoming_events = list(events().values())[0:8]
    # subset = upcoming_events[0:8]
    # subset = {}
    # for i, v in enumerate(tuple(upcoming_events)):
    #     if i < 8: subset[v] = upcoming_events[v]
    #     else: break

    # subset = []
    # for _ in range(8):
    #     # t = list(upcoming_events)[0]
    #     t = upcoming_events.popitem(last=False)
    #     # print(t[1])
    #     subset.append(t[1])

    # subset = list(upcoming_events)

    # print(subset)

    

    return render_template('homepage.html', events=upcoming_events)
