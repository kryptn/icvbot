import urllib2, random, xml.dom.minidom, re, twitter
from xml.sax.saxutils import unescape
from BeautifulSoup import BeautifulSoup

def getTwitterCrawl(statusId):
   api = twitter.Api()
   nextid, stream = statusId, list()
   while nextid:
      status = api.GetStatus(nextid)
      stream.append(str(status.user.screen_name +": "+ status.text))
      nextid = status.in_reply_to_status_id
   return stream[::-1]
   

def getYoutubeComment(vidid):
   response = urllib2.urlopen("http://gdata.youtube.com/feeds/api/videos/%s/comments" % (vidid)).read()
   dom = xml.dom.minidom.parseString(response)
   entries = dom.getElementsByTagName("content")
   randIndex = random.randint(11,20)
   if len(entries) >= randIndex:
      comment = ''
      entry = entries[randIndex]
      for node in entry.childNodes:
         if node.nodeType == node.TEXT_NODE:
            comment = comment+node.data
      return ' '.join(str(comment).split())
   return None

def main(arg):
   yt = re.findall(r"\b(?P<url>http://[\w\.]*youtube\.com/[\w\?&]*v=(?P<vidid>[\w-]*))", arg[0])
   tw = re.findall(r"\bhttp[s]?://[\w\.]*twitter.com/#!/[\w]*/status/(?P<id>[\d]*)", arg[0])
   if yt and random.random() < 0.25:
      title = getYoutubeComment(yt[0][1])
      if title:
         return title
   if tw:
      crawl = getTwitterCrawl(tw[0])
      if crawl:
         return crawl
   try:
      f = urllib2.urlopen(arg[0])
      doc = f.read()
      f.close()
      soup = BeautifulSoup(doc)
      try:
         title = "Title: "+unescape(' '.join(str(soup.head.title.string).split()))
      except AttributeError:
         title = None
   except urllib2.URLError:
      title = None
   return title
