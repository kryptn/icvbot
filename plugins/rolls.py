#!/usr/bin/python
from random import randint

def roll( quant, dmax ):
   """Roll the dice and return results"""
   rolls = []
   for x in xrange( quant ):
      rolls.append( randint( 1, dmax ) )

   result = "%s for a total of %d" % (', '.join( map(lambda x: str(x), rolls) ), sum(rolls) )
   return result

def main(l, args):
   try:
      quant, dmax = args[0].split( 'd' )
      quant, dmax = int(quant), int(dmax)
   except( ValueError, IndexError ):
      return "usage example: /me rolls 2d6"

   if quant > 100 or quant < 1:
      return "You must roll between 1 and 100 dice, /me rolls 2d6"
   if dmax > 1000:
      return "Dice cannot have more than 1000 sides!"

   return roll( quant, dmax )
