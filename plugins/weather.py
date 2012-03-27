#!/usr/bin/python
import pywapi
import string


def main(l, argv):
    argv = ' '.join(argv)
    try:
        google_result = pywapi.get_weather_from_google(argv)
        condition = string.lower(google_result['current_conditions']['condition'])
        temp = google_result['current_conditions']['temp_f']
        city = google_result['forecast_information']['city']
        result = 'It is currently %s and %sF in %s.' % (condition, temp, city)
    except Exception:
        result = 'Invalid location'

    return result.encode('ascii', 'replace')
