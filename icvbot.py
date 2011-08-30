#!/usr/bin/env python
import sys, os, random, re, time, config, MySQLdb
from types import *
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor, task

pluginsFolder = "plugins"
webdir = "/home/kryptn/www/public_html/"
master = "kryptn!~kaphene@li216-42.members.linode.com"
wordlist = "wordlist.txt"
rc = 0

def cImport(name):
	"""import plugins.  reloads module if already imported"""
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

def log(*args):
	"""logs to file and prints to console"""
	s = ''.join(map(lambda x: str(x)+" ", args))
	t = time.strftime("%Y %m %d %H %M %S ", time.gmtime())+s
	f = open('botlog.txt', 'a')
	f.write(t+"\n")
	f.close()
	print t

class icvBot(irc.IRCClient):
	def __init__(self):
		self.quitPassword = None
		self.checkTask = task.LoopingCall(self.runCommand, 'checkforum')

	def _get_nickname(self):
		"""define username"""
		return self.factory.nickname

	nickname = property(_get_nickname)

	def _get_password(self):
		"""define password"""
		return self.factory.password

	password = property(_get_password)

	def startForumCheckLoop(self, t=60.0):
		"""starts the task loop to query the ICV database for updates"""
		log("Started forum check loop")
		self.checkTask.start(t)
	
	def stopForumCheckLoop(self):
		"""stops task loop"""
		self.checkTask.stop()

	def handleResponse(self, *args):
		"""handle plugin responses"""
		if len(args) > 1:
			log(args[1])
		response = args[0]
		if type(response) is StringType:
			response = [response]
		if type(response) is ListType:
			for rmsg in response:
				log(rmsg)
				self.msg(self.factory.channel, rmsg)

	def runCommand(self, command, *args):
		"""
		import [command] if existant, runs [command].main if successful
		all plugins should return one of the following:
		 * a string
		 * a string, a log string
		 * a list of strings
		 * a list of strings, a log string
		"""
		mod = cImport(command)
		if mod:
			result = mod.main(args)
			log("Import success: ",command, args, result)
			if result:
				self.handleResponse(result)
		else:
			log("Import of %s failed" % (command))
			return False

	def runClass(self, command, *args):
		"""
		testing a more inclusive plugin system, 
		still doesn't work (and ATM says it's a bad idea)
		"""
		mod = cImport(command)
		if mod:
			c = mod.m()
			c.main()
		else:
			log("Import of %s failed" % (command))
			return False
	
	def assignKillPassword(self):
		"""assigns a password for admin bot control"""
		if wordlist:
			f = open(wordlist, 'r')
			self.quitPassword = random.choice(f.read().split())
			f.close()
			log("Set quit password: %s" % (self.quitPassword))
			self.msg(master, "Quit password: %s" % (self.quitPassword))
	
	def findUrl(self, msg):
		"""
		Attempt to find a URL in a string.
		Run urlhandler on success
		"""
		urls = re.findall(r'(https?://\S+)', msg)
		if urls:
			for url in urls:
				self.runCommand('urlhandler', url)
		else:
			return False

	def signedOn(self):
		"""	
		called on sign on
		Starts forum check loop, joins given channel
		I'm sure multi-channel is possible, but i haven't bothered to try
		"""
		self.startForumCheckLoop()
		#self.assignKillPassword()
		self.join(self.factory.channel)
		log("Signed on as %s." % (self.factory.nickname,))

	def kickedFrom(self, channel, kicker, message):
		"""
		called when kicked from channel
		50% chance of revenge kicking when rejoining
		"""
		log("Kicked by %s: %s" % (kicker, message))
		self.join(self.factory.channel)
		if random.random() < 0.5:
			d = task.deferLater(reactor, 3.0, self.kick, self.factory.channel, kicker)
			d.addCallback(log, "Kicked %s" % (kicker))
			log("Queue'd kick of %s" % (kicker))
		log("Rejoined")

	def userKicked(self, kickee, channel, kicker, message):
		"""
		called when a user is kicked
		25% chance of replying "Oh shit!"
		easily expandable
		"""
		if random.random() < 0.25:
			self.msg(self.factory.channel, "Oh shit!")
			log("%s was kicked from %s and I replied" % (kickee, channel))

	def joined(self, channel):
		"""called when finished joining a channel"""
		log("Joined %s." % (channel,))

	def userLeft(self, user, channel):
		"""
		called when a user leaves the channel
		2% chance
		"""
		if random.random() < 0.02:
			self.msg(self.factory.channel, "But, I love you! :(")
	
	def topicUpdated(self, user, channel, newTopic):
		"""
		called when the topic updates (and unfortunately when the bot joins the channel)
		needs cleaning up
		"""
		f = open('topic.txt', 'a')
		t = time.strftime("%Y.%m.%d %H:%M:%S ", time.gmtime())
		f.write(t+"%s changed the topic in %s: %s \n" % (user, channel, newTopic))
		f.close()
		if webdir: os.system("cp topic.txt "+webdir)
		log("Updated topic log")

	def privmsg(self, user, channel, msg):
		"""
		called on message recieved from channel or PM
		ignored from non-users, and when it doesn't start with the bot name
		first parses for admin commands (needs to be expanded)
		then parses for the first word after the bots name and tries to import and run that command
		example: SirVirii: plugin-name some arguments
		         |ignored |command    |args
		if none of the above, parse the message for a url
		"""
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
				if msg == "update":
					os.system("git pull")
				if msg == "test":  #testing the class plugin system that ATM doesn't like
					self.runClass('mytest')
			prefix = "%s: " % (user.split('!', 1)[0],)
			command, args = msg.split(' ')[0], msg.split(' ')[1:]
			self.runCommand(command, args)
		else: 
			self.findUrl(msg)

	def action(self, user, channel, data):
		log("Recieved action: ",user, channel, data)
		command, args = data.split(None, 1)
		self.runCommand(command, args)

class icvBotFactory(protocol.ClientFactory):
	protocol = icvBot

	def __init__(self, channel, nickname='SirVirii', password=None):
		"""uses protocol to"""
		self.channel = channel
		self.nickname = nickname
		self.password = password
	
	def clientConnectionLost(self, connector, reason):
		"""called on disconnect, attempts to reconnect"""
		log("Lost connection (%s), reconnecting." % (reason,))
		connector.connect()

	def clientConnectionFailed(self, connector, reason):
		"""called on failed connection.  Obvious."""
		log("Could not connect: %s" % (reason,))


"""This next area parses cli and runs the bot!"""

if __name__ == "__main__":
	try:
		chan = sys.argv[1]
		nick = sys.argv[2]
        	if not chan.startswith( '#' ): chan = '#' + chan
	except IndexError:
		sys.exit( "usage: python bot.py channel nickname <password>" )
	try: passwd = sys.argv[3]
	except IndexError:
		passwd = None
	reactor.connectTCP('irc.freenode.net', 6667, icvBotFactory(chan,nick,passwd))
	reactor.run()
	print rc
	sys.exit(rc)
