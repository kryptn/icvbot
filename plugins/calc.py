#!/usr/bin/python

# Created 4/8/09 by Daedalus
# http://fublag.wordpress.com
# actaeus@gmail.com

import urllib, httplib, sys

def main(argv):
    argv = ' '.join(argv[0])
    query=urllib.urlencode({'q':argv})

    start='<h2 class=r style="font-size:138%"><b>'
    end='</b>'

    google=httplib.HTTPConnection("www.google.com")
    google.request("GET","/search?"+query)
    search=google.getresponse()
    data=search.read()

    if data.find(start)==-1: return "Google Calculator results not found."
    else:
        begin=data.index(start)
        result=data[begin+len(start):begin+data[begin:].index(end)]
        result = result.replace("<font size=-2> </font>",",").replace(" &#215; 10<sup>","E").replace("</sup>","").replace("\xa0",",")
        return result, None