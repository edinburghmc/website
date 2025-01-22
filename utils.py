from time import (
    localtime,
    strftime
)

# Returns a suffixed day of the month
def prettyday(d):
    suffix = {1:'st',2:'nd',3:'rd'}.get(d%20, 'th')
    return f"{d}{suffix}"

# Take a date and return month and year
def prettymonth(start):
    startfields = localtime(start)

    rc = strftime("%B %Y", startfields)
    return rc

# Take a date and return a string representation
def prettydate(start, display_year=False, display_month=True):
    rc = ""
    startfields = localtime(start)

    if display_month:
        rc = "%s %s" % (prettyday(startfields[2]), strftime("%B", startfields))
    if display_year:
        rc = "%s %s" % (rc, strftime("%Y", startfields))
    return rc

# Take a start date and number of days, and return a string describing the
# date range.
def prettyrange(start, length, display_year=False):
    startfields = localtime(start)
    endfields = localtime(start + (length * 60 * 60 * 24))

    rc = prettyday(startfields[2])
    if startfields[1] != endfields[1]:
        rc = "%s %s" % (rc, strftime("%B", startfields))
    if startfields[0] != endfields[0] and display_year:
        rc = "%s %s" % (rc, strftime("%Y", startfields))

    rc = "%s to %s %s" % (rc, prettyday(endfields[2]), strftime("%B", endfields))
    if display_year:
        rc = "%s %s" % (rc, strftime("%Y", endfields))
    return rc

# Construct the name of a meet from the accommodation and the location
def meet_name(meet):
    meetname = meet['accommodation']
    if meet['location'] is not None and meet['location'] != '' and meet['location'] != meetname:
        meetname = "%s, %s" % (meetname, meet['location'])

    return meetname


# def author_name(row):
#     author = row["authorname"]
#     try:
#         author = authors[row["authorid"]]
#     except:
#         try:
#             author_row = get_db_row('members', "id = %s" % (row["authorid"]), fields="display_name")
#             author = author_row["display_name"]
#             authors[row["authorid"]] = author
#         except:
#             pass

#     return author