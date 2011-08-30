import MySQLdb

def query(q):
   """mysql query"""
   conn = MySQLdb.connect(
      host   = config.host,
      user   = config.user, 
      passwd = config.pword,
      db     = config.db
   )
   cursor = conn.cursor()
   cursor.execute(q)
   result = cursor.fetchall()
   cursor.close()
   conn.close()
   return result

def checkFile(loc, q):
   """checks log file against current latest record"""
   result = query(q)[0]
   try:
      f = open(loc, 'r')
      record = f.read()
      f.close()
   except IOError:
      f = open(loc, 'w')
      f.write("0")
      f.close()
      record = "0"
   if result[0] > int(record):
      f = open(loc, 'w')
      f.write(str(result[0]))
      f.close()
      return result
   return False

def getLatestId():
   """
   queries database for the highest ID post and thread
   returns message to send to channel (if any)
   """

   q = """
      SELECT icv_posts.id, icv_posts.threadid,
      icv_posts.author, icv_threads.title 
      FROM icv_posts 
      INNER JOIN icv_threads 
      ON icv_posts.threadid=icv_threads.id 
      ORDER BY id DESC LIMIT 1
   """

   r = checkFile('lid.txt', q)
   if r:
      return "%s posted in '%s': http://icodeviruses.com/forum.virus?seed=%s" % (r[2], r[3], str(r[1]))
   else:
      return False

def getLatestThread():
   q = """
      SELECT id, author, title 
      FROM icv_threads 
      ORDER BY id DESC LIMIT 1
   """

   r = checkFile('lt.txt', q)
   if r:
      return "%s made a new thread named '%s': http://icodeviruses.com/forum.virus?seed=%s" % (r[1], r[2],str(r[0]))
   else:
      return False

def main(*args):
   """ Check forum for updates. Run getLatestId and getLatestThread"""
   log("Checking Forum")
   latestId = getLatestId()
   latestThread = getLatestThread()
   result = []
   if latestId:
      result.append(latestId)
   if latestThread:
      result.appendlatestThread)
   return result
