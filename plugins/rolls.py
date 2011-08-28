#!/usr/bin/python
import random


def main(*args):
   try:
      quant, dmax = args[0][0].split('d')
      results = []
      for x in xrange(int(quant)):
         results.append(random.randint(1,int(dmax)))
      result = "%s for a total of %d" % (', '.join(map(lambda x: str(x), results)), sum(results))
      return result
   except IndexError:
      return None
   except ValueError:
      return None
