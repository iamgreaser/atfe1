import math
import random

from constants import *

class HihatDrum(object):
	def __init__(self):
		self.offs = 0
		self.vol = 0.0
		self.last_v = 0.0
		self.playing = False

	def play(self, vol):
		self.offs = 0
		self.vol = vol
		self.playing = True

	def mix(self, buf, sz):
		if not self.playing:
			return

		for i in range(sz):
			v = (random.random()*2.0-1.0)*(0.1**(14.0*self.offs/float(MIXFREQ)/self.vol))
			self.last_v += (v-self.last_v)*0.3
			v -= self.last_v
			buf[i] += max(-1.0, min(1.0, v*1))*0.3*self.vol
			self.offs += 1


class KickDrum(object):
	def __init__(self):
		self.offs = 0
		self.playing = False

	def play(self):
		self.offs = 0
		self.playing = True

	def mix(self, buf, sz):
		if not self.playing:
			return

		for i in range(sz):
			v1  = (random.random()*2.0-1.0)
			v1 *= (0.1**(100.0*self.offs/float(MIXFREQ)))
			v2  = math.sin(math.pi*2.0*80.0*self.offs/float(MIXFREQ))
			v2 += math.sin(math.pi*2.0*70.0*self.offs/float(MIXFREQ))
			v2 *= (0.1**(8.0*self.offs/float(MIXFREQ)))
			v = v1 + v2
			v *= 0.6
			buf[i] += max(-1.0, min(1.0, v*1))*0.7
			self.offs += 1


class SnareDrum(object):
	def __init__(self):
		self.offs = 0
		self.playing = False

	def play(self):
		self.offs = 0
		self.playing = True

	def mix(self, buf, sz):
		if not self.playing:
			return

		for i in range(sz):
			v1  = (random.random()*2.0-1.0)
			v1 *= (0.1**(7.0*self.offs/float(MIXFREQ)))
			v2  = math.sin(math.pi*2.0*100.0*self.offs/float(MIXFREQ))
			v2 += math.sin(math.pi*2.0*110.0*self.offs/float(MIXFREQ))
			v2 *= (0.1**(6.0*self.offs/float(MIXFREQ)))
			v = v1 + v2
			v *= 0.6
			buf[i] += max(-1.0, min(1.0, v*1))*0.7
			self.offs += 1


class BassInstrument(object):
	def __init__(self):
		self.buffer = [0.0, 0.0]
		self.offs = 0
		self.last_v = 0.0
		self.damp = 0.9
		self.feedback = 1.0

	def play(self, note, slappiness=0.3):
		freq = 110.0*(2.0**((note-57-12)/12.0))
		self.period = int(round(MIXFREQ/freq))
		#self.buffer = [random.random()*2.0-1.0 for i in range(self.period)]
		#self.buffer = [(float(i)*2.0-1.0)/self.period for i in range(self.period)]
		AMP_P = 0.75
		AMP_N = 0.25
		self.buffer = [ 0.0
			+ (1.0-slappiness)*(AMP_P if i < self.period//4 else -AMP_N)
			+ slappiness*(random.random()*2.0-1.0)
			for i in range(self.period)]
		self.offs = 0
		self.last_v = 0.0
		self.damp = 0.7
		self.feedback = 1.0

	def stop(self):
		self.damp = 0.9
		self.feedback = 0.6

	def mix(self, buf, sz):
		idamp = (1.0-self.damp**(800.0/len(self.buffer)))
		feedback = self.feedback**(800.0/len(self.buffer))
		for i in range(sz):
			v = self.buffer[self.offs]
			self.last_v += (v - self.last_v)*idamp
			self.buffer[self.offs] = self.last_v*feedback
			v = self.last_v
			self.offs += 1
			self.offs %= len(self.buffer)
			buf[i] += v*0.7

