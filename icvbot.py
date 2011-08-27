#!/usr/bin/env python
import sys, os, random, re, time, config, MySQLdb
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, task

pluginsFolder = "plugins"
webdir = "/home/kryptn/www/public_html/"
master = "kryptn!~kaphene@li216-42.members.linode.com"
wordlist = "wordlist.txt"
rc = 0

# import plugins.  reloads module if already imported
def cImport(name):
	name = "%s.%s" % (pluginsFolder, name)
	try:
		mod = sys.modules[name]
		reload(mod)
		return mod
	except KeyError:
		pass
	try:
		__import__(name)
		return sys.modules[name]
	except ImportError: return None

#mysql query
def query(q):
	conn = MySQLdb.connect(host=config.host,user=config.user,
									passwd=config.pword,db=config.db)
	cursor = conn.cursor()
	cursor.execute(q)
	result = cursor.fetchall()
	cursor.close()
	conn.close()
	return result

#logs to file and prints to console
def log(*args):
	s = ''.join(map(lambda x: str(x)+" ", args))
	t = time.strftime("%Y %m %d %H %M %S ", time.gmtime())+s
	f = open('botlog.txt', 'a')
	f.write(t+"\n")
	f.close()
	print t

class icvBot(irc.IRCClient):
	def __init__(self):
		self.quitPassword = None
		self.checkTask = task.LoopingCall(self.checkForum)


	#defines username and password to the server
	def _get_nickname(self):
		return self.factory.nickname
	nickname = property(_get_nickname)

	def _get_password(self):
		return self.factory.password
	password = property(_get_password)

	#starts the task loop to query the ICV database for updates
	def startForumCheckLoop(self, t=60.0):
		log("Started forum check loop")
		self.checkTask.start(t)
	
	#stops task loop
	def stopForumCheckLoop(self):
		self.checkTask.stop()

	#checks log file against current latest record
	def checkFile(self, loc, q):
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

	#queries database for the highest ID post and thread, returns message to send to channel (if any)
	def getLatestId(self):
		q = "select icv_posts.id, icv_posts.threadid, icv_posts.author, icv_threads.title from icv_posts inner join icv_threads on icv_posts.threadid=icv_threads.id order by id desc limit 1"
		r = self.checkFile('lid.txt', q)
		if r:
			return "%s posted in '%s': http://icodeviruses.com/forum.virus?seed=%s" % (r[2], r[3], str(r[1]))
		else:
			False

	def getLatestThread(self):
		q = "select id, author, title from icv_threads order by id desc limit 1"
		r = self.checkFile('lt.txt', q)
		if r:
			return "%s made a new thread named '%s': http://icodeviruses.com/forum.virus?seed=%s" % (r[1], r[2],str(r[0]))
		else:
			False

	# runs the above
	def checkForum(self):
		log("Checking Forum")
		latestId = self.getLatestId()
		latestThread = self.getLatestThread()
		if latestId:
			self.msg(self.factory.channel, latestId)
		if latestThread:
			self.msg(self.factory.channel, latestThread)

	#import [command] if existant, runs [command].main if successful
	#all plugins should return a string, and a log string (or None)
	#could easily be cleaned up
	def runCommand(self, command, *args):
		mod = cImport(command)
		if mod:
			result, logger = mod.main(args)
			if result:
				self.msg(self.factory.channel, result)
			log("Import success: ",command, args, result, logger)
		else:
			log("Import of %s failed" % (command))
			return False

	#testing a more inclusive plugin system, still doesn't work (and ATM says it's a bad idea)
	def runClass(self, command, *args):
		mod = cImport(command)
		if mod:
			c = mod.m()
			c.main()
		else:
			log("Import of %s failed" % (command))
			return False
	
	#assigns a password for admin bot control
	def assignKillPassword(self):
		if wordlist:
			f = open(wordlist, 'r')
			self.quitPassword = random.choice(f.read().split())
			f.close()
			log("Set quit password: %s" % (self.quitPassword))
			self.msg(master, "Quit password: %s" % (self.quitPassword))
	
	#finds a URL in a string.  if it does it runs urlhandler
	def findUrl(self, msg):
		urls = re.findall(r'(https?://\S+)', msg)
		if urls:
			for url in urls:
				self.runCommand('urlhandler', url)
		else:
			return False
	

	#called on sign on
	#starts forum check loop, joins given channel
	#i'm sure multi-channel is possible, but i haven't bothered to try
	def signedOn(self):
		self.startForumCheckLoop()
#		self.assignKillPassword()
		self.join(self.factory.channel)
		log("Signed on as %s." % (self.factory.nickname,))

	#called when kicked from channel
	#50% chance of revenge kicking when rejoining
	def kickedFrom(self, channel, kicker, message):
		log("Kicked by %s: %s" % (kicker, message))
		self.join(self.factory.channel)
		if random.random() < 0.5:
			d = task.deferLater(reactor, 3.0, self.kick, self.factory.channel, kicker)
			d.addCallback(log, "Kicked %s" % (kicker))
			log("Queue'd kick of %s" % (kicker))
		log("Rejoined")

	#called when a user is kicked
	#25% chance of replying "Oh shit!"
	#easily expandable
	def userKicked(self, kickee, channel, kicker, message):
		if random.random() < 0.25:
			self.msg(self.factory.channel, "Oh shit!")
			log("%s was kicked from %s and I replied" % (kickee, channel))

	#called when finished joining a channel
	def joined(self, channel):
		log("Joined %s." % (channel,))

	#called when a user leaves the channel
	#2% chance
	def userLeft(self, user, channel):
		if random.random() < 0.02:
			self.msg(self.factory.channel, "But, I love you! :(")
	
	#called when the topic updates (and unfortunately when the bot joins the channel)
	#needs cleaning up
	def topicUpdated(self, user, channel, newTopic):
		f = open('topic.txt', 'a')
		t = time.strftime("%Y.%m.%d %H:%M:%S ", time.gmtime())
		f.write(t+"%s changed the topic in %s: %s \n" % (user, channel, newTopic))
		f.close()
		if webdir: os.system("cp topic.txt "+webdir)
		log("Updated topic log")

	#called on message recieved from channel or PM
	#ignored from non-users, and when it doesn't start with the bot name
	#first parses for admin commands (needs to be expanded)
	#then parses for the first word after the bots name and tries to import and run that command
	#example: SirVirii: plugin-name some arguments
	#         |ignored |command    |args
	#if none of the above, parse the message for a url
	def privmsg(self, user, channel, msg):
		if not user:
			return
		log("Recieved message: ",user, channel, msg)
		if self.factory.nickname in msg.split()[0]:
			trash, msg = msg.split(None, 1)
			if user == master:
				if msg == "quit":  #shuts down the bot
					reactor.stop()
				if msg == "restart":  #restarts the bot
					global rc
					rc = 9
					reactor.stop()
				if msg == "test":  #testing the class plugin system that ATM doesn't like
					self.runClass('mytest')
			prefix = "%s: " % (user.split('!', 1)[0],)
			command, args = msg.split(' ')[0], msg.split(' ')[1:]
			self.runCommand(command, args)
		else: 
			self.findUrl(msg)


class icvBotFactory(protocol.ClientFactory):
	protocol = icvBot

	#uses protocol to 
	def __init__(self, channel, nickname='SirVirii', password=None):
		self.channel = channel
		self.nickname = nickname
		self.password = password
	
	#called on disconnect, attempts to reconnect
	def clientConnectionLost(self, connector, reason):
		log("Lost connection (%s), reconnecting." % (reason,))
		connector.connect()

	#called on failed connection.  Obvious.
	def clientConnectionFailed(self, connector, reason):
		log("Could not connect: %s" % (reason,))


#runs bot
if __name__ == "__main__":
	try:
		chan = sys.argv[1]
		nick = sys.argv[2]
	except IndexError:
		print "error.  'python bot.py channel nickname <password>"
	try: passwd = sys.argv[3]
	except IndexError:
		passwd = None
	reactor.connectTCP('irc.freenode.net', 6667, icvBotFactory("#"+chan,nick,passwd))
	reactor.run()
	print rc
	sys.exit(rc)