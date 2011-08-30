#!/usr/bin/python
import random

def roll( quant, dmax ):
   """Roll the dice and return results"""
   rolls = []
   for x in xrange( quant ):
      rolls.append( random.randint( 1, dmax ) )

   result = "%s for a total of %d" % (', '.join( map(lambda x: str(x), rolls) ), sum(rolls) )
   return result


def main( *args ):
   try:
      quant, dmax = args[0][0].split( 'd' )
      quant, dmax = int(quant), int(dmax)
   except ValueError or IndexError:
      return None

   if quant > 10 or quant < 1:
      return "You must roll 1-10 dice, example: 2d6"
   if dmax > 100:
      return "Dice cannot have more that 100 sides!"

   return roll( quant, dmax )
