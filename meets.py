from collections import OrderedDict
from time import mktime, strftime, strptime, time, localtime
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

import emc.utils as utils
from emc.auth import login_required
from emc.db import get_db

bp = Blueprint('meets', __name__)

def is_null(val):
    if val is None or val == "":
        return True
    else:
        return False

def updated_meets():

    # Create a table of recent updates (anything less than a week old).
    then = strftime('%Y-%m-%d', localtime(time() - 60 * 60 * 24 * 7))

    db = get_db()

    rows = db.execute(f"""SELECT updates.meetid, updates.lastupdate, updates.changedesc, updates.userid FROM updates JOIN meets ON  
                    updates.meetid = meets.id WHERE updates.lastupdate >= '{then}' order by updates.lastupdate desc""")


    updates = OrderedDict()

    for update in rows:

        # Get the user name
        # username = display_name("%s" % update['userid'])
        username = "bob"
        if username == "":
            continue

        desc = update['changedesc']

        # Don't show meetreport stuff on meets page
        if desc != 'Meet added':
            continue

        # Create the meetname
        try:
            meet = db.execute(f"SELECT * FROM meets WHERE id = '{update['meetid']}'").fetchone()
            meetname = utils.meet_name(meet)
        except Exception as e:
            print(e)
            updates["error"] = True
            # myabe use flask flash here?
            # updates = "%s<tr><td>Error in meetid:</td><td>%s</td></tr>" % (updates, update['meetid'])
            continue

        # Beautify the date
        date1 = mktime(strptime(("%s" % (update['lastupdate'])), '%Y-%m-%d'))
        date = utils.prettydate(date1, display_year=False, display_month=True)

        # if (row % 2) == 0:
        #     thisclass = "lightrow"
        # else:
        #     thisclass = "darkrow"

        # updates = '%s<tr class="%s"><td>On %s:</td><td style="padding-left:15">New %s meet added by %s</td></tr>' \
        #               % (updates, thisclass, date, meetname, username)

        row_update = {}
        row_update['date'] = date
        row_update['meetname'] = meetname
        row_update['user'] = username
        
        # %s:</td><td style="padding-left:15">New %s meet added by %s</td></tr>' \
        #               % (updates, thisclass, date, meetname, username)

        print(row_update)
        # use unix time stamp as dict key
        updates[date1] = row_update
        # row += 1

    return updates

def upcoming_meets():

    now = strftime('%Y-%m-%d')

    db = get_db()
    meets = db.execute(f"""
            SELECT * 
            FROM meets JOIN members 
                ON contactid = members.id
            WHERE firstnight >= '{now}' order by firstnight    
                """).fetchall()
    

    events = {}

    # storing prettyfied info
    for meet in meets:
        start = mktime(strptime(("%s" % (meet['firstnight'])), '%Y-%m-%d'))
        date_info = {}
        date_info["dates"] = utils.prettyrange(start, meet['nights'])

        details = {}

        # text description of a (special) time of year to state in meets' list, e.g. Easter
        desc = meet['datedesc']
        if desc and desc != "":
            date_info["datedesc"] = desc

        BOOKING_STATUS = False

        try:
            booking = mktime(strptime(("%s" % (meet['booking'])), '%Y-%m-%d'))
            # Hack which adds on 18 hours to booking so that Booking Now appears at 6pm!
            booking = booking + (18.0 * 60.0 * 60.0)
            if booking > time():
                # date_info.append("<em>(booking opens %s)</em>" % (utils.prettydate(booking)))
                date_info["booking_date"] = utils.prettydate(booking)
            else:
                # date_info.append("<strong>Booking now</strong>")
                BOOKING_STATUS = True
                
        except:
            # date_info.append("<strong>Booking now</strong>")
            BOOKING_STATUS = True

        date_info["booking_status"] = BOOKING_STATUS
        details["date_info"] = date_info

        # Second cell is accommodation (with link) and location
        location = {}
        location["accommodation_name"] = meet['accommodation']
        link = meet['link']

        # accommodation.link = True

        # if is_null(link):
        #     # cell.append(meet['accommodation'])
        #     accommodation.link = False
        # else:
        #     cell.append('<a href="%s">%s</a>' % (link, meet['accommodation']))
        #     accommodation.link = meet['link']
        
        location["link"] = False if is_null(link) else link
        
        meet_location = meet['location']
        if meet_location and meet_location != '':
            location["location"] = meet_location

        details["location"] = location

        # Third call is meet type, plus fee in italics
        accommodation = {}
        accommodation["type"] = meet['accommodationtype']

        fee = meet['fee']
        if not is_null(fee):
            # this is from the original code; it adds a line break if there's extra text after the cost; I've never seen it used in actual use on the website
            # cell.append('<em>Meet fee &#163;%s</em>' % (re.sub('^(\d+) +([^ ])', r'\1<br>\2', fee)))
            #
            # ...however, this seems a lot simpler?! I hope I'm not missing something vital
            fee_split = fee.split(maxsplit=1)
            try:
                accommodation["cost_value"] = fee_split[0]
            except:
                pass
            try:
                accommodation["cost_detail"] = fee_split[1]
            except:
                pass

        details['accommodation'] = accommodation

        # Fourth cell is the number of places (plus camping details)
        db_places = meet['places']
        cell = []

        places = {} 

        if is_null(db_places):
            places["places_str"] = "Unlimited"
        elif re.match('^\\d+$', db_places): # regex checks to see if it's only a digit - if so, we need to append the string "places"
            places["places_str"] = f"{db_places} places"
        else:
            places["places_str"] = db_places

        campingplaces = meet['campingplaces']
        campingfee = meet['campingfee']

        # places["camping_places"] = meet['campingplaces']
        # places["camping_fee"] = meet['campingfee'] #yes, this is here, not in the fee cell(!)

        if not is_null(campingplaces) and not is_null(campingfee):
            # cell.append('<i>(%s camping spaces available for &#163;%s)</i>' % (campingplaces, campingfee))
            places["camping_info"] = f"({campingplaces} camping spaces available for &#163;{campingfee})"
        elif not is_null(campingplaces):
            # cell.append('<i>(%s camping spaces available)</i>' % campingplaces)
            places["camping_info"] = f"({campingplaces} camping spaces available)"
        elif not is_null(campingfee):
            # cell.append('<i>(Camping available for &#163;%s)</i>' % campingfee)
            places["camping_info"] = f"(Camping available for &#163;{campingfee})"

        details['nplaces'] = places

        # Fifth cell is the contact
        # contact = User(row=meet)
        name = meet['display_name']
        # number = contact.get_mobile_phone()
        details['contact'] = name

        events[start] = details

    return events

@bp.route('/meets.html')
def meets():

    updates = updated_meets()
    events = upcoming_meets()

    return render_template('meets/index.html', meets=events, updates=updates)

@bp.route('/meets/add', methods=('GET', 'POST'))
# @login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('meets.index'))

    return render_template('meets/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/meets/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/meets/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/meets/reports.html')
def meet_reports():
    db = get_db()
    # meets = db.execute("""SELECT meets.id AS meetid, meets.firstnight, meets.accommodation, meets.datedesc, meets.location 
    #                         FROM meets WHERE meets.id in (SELECT meettext.meetid FROM meettext)
    #                      ORDER BY meets.firstnight DESC""").fetchall()
    
    meets = db.execute("""SELECT meets.id as meetid, meets.firstnight, meets.accommodation, meets.datedesc, meets.location, 
                            meettext.id as textids
                            FROM meets JOIN meettext ON meets.id = meettext.meetid
                         ORDER BY meets.firstnight DESC""").fetchall()
    
    editlinks = False

    meet_reports = {}

    for meet in meets:

        meet_details = {}

        start = mktime(strptime(("%s" % (meet['firstnight'])), '%Y-%m-%d'))
        if start > time() and editlinks is False:
            continue
        
        # cell = utils.prettymonth(start)
        # if editlinks == "":
        #     tds.append(cell)
        # else:
        #     tds.append('<a href="meetedit?id=%s">%s</a>' % (meet["id"], cell))
        
        meet_name = utils.meet_name(meet)

        if not is_null(meet['datedesc']):
            meet_name = f"{meet_name} ({meet['datedesc']})"


        user = None
        tds = None
        # Third cell is a link to the meet report
        if user and is_null(meet['textids']):
            # There's no meet report.  For the webmaster and the meet contact, give
            # the opportunity to add one.  Otherwise, the chance to nag!

            if start < time():
                # Meet has happened
                if user.get_val('id') == meet['contactid']:
                    # The user is the organiser. Let them add a meet
                    tds.append('<a href="meetreportedit%s-0">Add meet report</a>' % (meet['id']))
                elif user.get_val('class') != 'O':
                    # The user is on the current committee. Let them add the meet.
                    if start > time() - (365 * 24 * 60 * 60):
                        tds.append(
                            '<a href="meetreportedit%s-0">Add meet report</a><br>'
                            '<a href="meetreportprod?id=%s">Request&nbsp;meet&nbsp;report</a><br>(from %s)' % (
                                meet['id'], meet['id'], display_name(meet['contactid'])))
                    else:
                        tds.append('<a href="meetreportedit%s-0">Add meet report</a>' % (meet['id']))
                else:
                    # Just a member. Let them nag if the meet was in the last year.
                    if start > time() - (365 * 24 * 60 * 60):
                        tds.append(
                            '<a href="meetreportprod?id=%s">Request&nbsp;meet&nbsp;report</a><br>(from %s)' % (
                                meet['id'], display_name(meet['contactid'])))
                    else:
                        tds.append('&nbsp;')
            else:
                # Meet is in the future.  No point linking to a report.
                tds.append('&nbsp;')
        # else:  # Not logged in...
        #     if not is_null(meet['textids']):
        #         # tds.append('<a href="meetreport%s">Read</a>' % (meet['id']))
        #         meet_report = True
        #     else:
        #         tds.append('&nbsp;')

        meet_report = False if is_null(meet['textids']) else True

        
        meet_details['id'] = meet['meetid']
        meet_details['date'] = utils.prettymonth(start)
        meet_details["name"] = meet_name
        meet_details["meet_report"] = meet_report

        meet_reports[start] = meet_details

    return render_template('meets/reports.html', reports=meet_reports)

@bp.route('/meets/<int:id>/report.html')
def meet_report(id):

    db = get_db()
    # report = db.execute('SELECT * FROM meettext JOIN meets ON meettext.meetid = meets.id WHERE meettext.id = ?',(id,)).fetchone()
    meet = db.execute('SELECT * FROM meettext JOIN meets ON meettext.meetid = meets.id WHERE meetid = ?',(id,)).fetchone()

    if meet is None:
        abort(404, f"Meet id {id} doesn't exist.")
    

# title

    time = []
    start = mktime(strptime(("%s" % (meet['firstnight'])), '%Y-%m-%d'))
    if meet['nights']:
        time.append(utils.prettyrange(start, meet['nights'], display_year=True))
    else:
        time.append(utils.prettyrange(start, 2, display_year=True))

    time.append(' - %s' % meet['accommodation'])
    location = meet['location']
    if location and location != '' and location != meet['accommodation']:
        time.append(', %s' % location)

    if not is_null(meet['datedesc']):
        time.append(" (%s)" % (meet['datedesc']))


    # author = db.author_name(meet)
    author = meet["authorname"]

    report = {}
    report["text"] = meet['data']
    report["time"] = "".join(time)
    report["author"] = author




    return render_template('meets/meet_report.html', report=report)
