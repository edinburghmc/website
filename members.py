from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from emc.auth import login_required
from emc.db import get_db

bp = Blueprint('members', __name__)

@bp.route('/contacts.html')
def contacts():

    # slightly overkill!

    # db = get_db()
    # committee = db.execute(
    #     'SELECT * FROM committee JOIN members ON committee.member = members.id JOIN committee_roles on committee.role = committee_roles.id'
    # ).fetchall()

    # ROLES = { 
    #     "PRESIDENT": committee,
    #     "MEETS_SEC": committee,
    #     "TREASURER": committee,
    #     "MEMBERSHIP": committee,
    #     "WEBMASTER": committee,
    #     "ORDINARY": [committee]}
    
    committee = None

        

    return render_template('contacts.html', committee=committee)

@bp.route('/members/list.html')
def members_list():
    pass

@bp.route('/members/my_account.html')
def profile():
    pass

# @bp.route('/meets/add', methods=('GET', 'POST'))
# # @login_required
# def create():
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('meets.index'))

#     return render_template('meets/create.html')

# def get_post(id, check_author=True):
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post

# @bp.route('/meets/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ?'
#                 ' WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('blog.index'))

#     return render_template('blog/update.html', post=post)

# @bp.route('/meets/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('blog.index'))

# @bp.route('/meets/reports.html')
# def meet_reports():
#     db = get_db()
#     reports = db.execute('SELECT meets.id AS meetid, meets.datedesc, meets.location FROM meets WHERE meets.id in (SELECT meet_reports.meetid FROM meet_reports)').fetchall()
#     return render_template('meets/reports.html', reports=reports)

# @bp.route('/meets/<int:id>/report.html')
# def meet_report(id):
#     db = get_db()
#     report = db.execute('SELECT * FROM meet_reports JOIN meets ON meet_reports.meetid = meets.id WHERE meet_reports.id = ?',(id,)).fetchone()
    
#     if report is None:
#         abort(404, f"Meet id {id} doesn't exist.")
    
#     return render_template('meets/meet_report.html', report=report)
