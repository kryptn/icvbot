  #!/usr/bin/python
import datetime


def getTime(offset=None):
	if offset:
		offset = int(offset) % 24

	if isinstance(offset, int):
		time = datetime.datetime.utcnow()
		time += datetime.timedelta(hours=offset)
	else:
		time = datetime.datetime.now()
	# for some reason strftime() produces an error so
	# I've chosen to format the time manually
	# return time.strftime('%I:%M %p')
	return formatTime(time)

def formatTime(t):
	if t.hour > 11:
		period = 'PM'
	else:
		period = 'AM'

	if t.hour % 12 == 0:
		hour = 12
	else:
		hour = t.hour % 12
	return '%d:%02d %s' % (hour, t.minute, period)

def main(l, args):
	if len(args) > 0:
		offset = args[0]
	else:
		offset = None
	return "According to my watch, the time is %s." % getTime(offset)
