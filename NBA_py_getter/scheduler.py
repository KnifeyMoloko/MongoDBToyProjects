from datetime import datetime, timedelta, time
from subprocess import Popen


class Scheduler:
    def __init__(self, s_year=None, s_month=None, s_day=None, e_year=None, e_month=None, e_day=None):
        self.start_year = s_year
        self.start_month = s_month
        self.start_day = s_day
        self.end_year = e_year
        self.end_month = e_month
        self.end_day = e_day
        self.start_date = datetime(year=self.start_year, month=self.start_month, day=self.start_day)
        self.end_date = datetime(year=self.end_year, month=self.end_month, day=self.end_day)

    def __getattr__(self, item):
        return item

    def get_start(self):
        return self.start_date

    def get_end(self):
        return self.end_date

    def get_dates(self):
        return self.start_date, self.end_date

    def enumerate_dates(self):
        strt = self.get_start()
        end = self.get_end()
        current = strt
        dates = []

        while current <= end:
            dates.append(current.strftime('%Y-%m-%d'))
            nxt = current + timedelta(days=1)
            current = nxt
        return dates

    def run_process(self, command):
        """

        :param command: command line string with a {} left for inserting the date
        :return:
        """
        dates = self.enumerate_dates()
        for d in dates:
            cmd = command.format(d)
            Popen(cmd, shell=True).wait(timeout=180)




#sched = Scheduler(2019, 4, 11, 2019, 4, 15)
#sched.run_process()

