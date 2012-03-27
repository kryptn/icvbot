  #!/usr/bin/python
import datetime


def main(*argv):
    time = datetime.datetime.now().strftime('%I:%M %p')
    return "According to my watch, the time is %s." % time
