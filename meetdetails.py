import datetime as dt

from . import db

class MeetDetails:

    def __init__(self, meet):
        self.meetid = meet['id']

    @property
    def _meet_name(self):
        pass

    @property
    def starttime():
        return None
    
    @property
    def prettydate():
        pass

    def prettymonth():
        pass

    @property
    def meet_organiser():
        return("name", "id")

    @property
    def has_meet_report():
        pass

class MeetReport(MeetDetails):

    def __init__(self):
        pass

    def neighbouring_meets(self):
        pass

    @property
    def report(self):
        report = dict()
        return report