def shift(s, phrase):
   phrase = list(phrase)
   for x in xrange(len(phrase)):
      if ord(phrase[x]) >= 97 and ord(phrase[x]) <= 122:
         phrase[x] = f(phrase[x], s, 97)
      if ord(phrase[x]) >= 65 and ord(phrase[x]) <= 90:
         phrase[x] = f(phrase[x], s, 65)
   return ''.join(phrase)

def f(c, s, n):
   return chr((ord(c)-n+s)%26+n)

def main(l, args):
   print args
   return shift(int(args[0]), ' '.join(args[1:]))
