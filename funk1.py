#!/usr/bin/env python3 --

import array
import itertools
import math
import random
import subprocess
import sys
import time

GLOBAL_VOL = 0.2

MIXFREQ = 48000
SLICELEN = MIXFREQ//50
BIGLEN = SLICELEN*16*7*2

BASE_NOTES = [v+0 for v in [
	54, 54, 54, 54,
	54, 54, 54, 54,
	54, 54, 59, 61,
	54, 54, 59, 61,
	#52, 52, 54, 54,
	#56, 56, 57, 59,
	#54, 54, 59, 61,
	#54, 54, 59, 61,
]]
BASE_NOTE = 52

fp = subprocess.Popen(["play", "-ts16", "-r"+str(MIXFREQ), "-c1", "-"], stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)

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

	def play(self, note):
		freq = 110.0*(2.0**((note+BASE_NOTE-57-12)/12.0))
		self.period = int(round(MIXFREQ/freq))
		#self.buffer = [random.random()*2.0-1.0 for i in range(self.period)]
		#self.buffer = [(float(i)*2.0-1.0)/self.period for i in range(self.period)]
		AMP_P = 0.75
		AMP_N = 0.25
		self.buffer = [ 0.0
			+ 0.7*(AMP_P if i < self.period//4 else -AMP_N)
			+ 0.3*(random.random()*2.0-1.0)
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

TICK_STEPS = [0, 5, 9, 12]

OFF = "OFF"

SOURCE_2 = [
	[  0, ..., OFF, ...],
	[  2, ..., OFF, ...],
	[  3, ..., OFF, ...],
	[  5, ..., OFF, ...],
	[  7, ..., OFF, ...],
	[ 10, ..., OFF, ...],
	[ -2, ...,   0, OFF],
	[ -2, ...,  -1, OFF],
	[  0, ...,  -2, OFF],
	[  2, ...,   3, OFF],
	[  3, ...,   2, OFF],
	[  3, ...,   5, OFF],
	[  5, ...,   3, OFF],
	[  5, ...,   7, OFF],
	[  7, ...,   5, OFF],
	[ 10, ...,   7, OFF],
	[ 10, ...,  12, OFF],
]
SOURCE_3 = [
	[OFF, ...,   0, ..., OFF, ...],
	[OFF, ..., ..., ...,   0, OFF],
	[  0, ..., OFF, ..., ..., ...],
	[  0, ..., OFF, ..., ..., ...],
	[  0, OFF,   0, ..., OFF, ...],
	[  0, ..., OFF, ...,   0, OFF],
	[  0, OFF,  10, ...,  12, OFF],
	[  2, OFF,   3, ...,   5, OFF],
	[  3, OFF,   5, ...,   7, OFF],
	[  3, OFF,   2, ...,  -2, OFF],
	[  7, OFF,   5, ...,   2, OFF],
	[ 10, OFF,   7, ...,   5, OFF],
	[  7, OFF,  10, ...,   7, OFF],
	[  5, OFF,   7, ...,   5, OFF],
	[  5, OFF,  10, ...,  12, OFF],
	[  7, OFF,  10, ...,  12, OFF],
	[ 12, OFF,  15, ...,  14, OFF],
	[  0, OFF,  -2, ...,  -1, OFF],
	[  5, ..., OFF, ...,   7, OFF],
	[  7, ..., OFF, ...,   5, OFF],
	[OFF, ...,   5, ...,   7, OFF],
	[OFF, ...,   3, ...,  -2, OFF],
	[  7, OFF,   5, ..., ..., OFF],
]
SOURCE_4 = [
	[OFF, ...,   0, ..., OFF, ..., ..., ...],
	[OFF, ...,   0, ..., OFF, ..., ..., ...],
	[OFF, ..., ..., ...,   0, ..., OFF, ...],
	[OFF, ..., ..., ...,   0, ..., OFF, ...],
	[  0, ..., OFF, ..., ..., ..., ..., ...],
	[  0, ..., OFF, ...,   0, ..., OFF, ...],
	[  0, ..., OFF, ...,   0, ...,   0, OFF],
	[  0, ..., OFF, ..., ..., ...,   0, OFF],
	[  0, ..., OFF, ...,  12, ..., OFF, ...],
	[  0, ..., OFF, ...,  10, ...,  12, OFF],
	[  0, ...,   5, OFF,   7, ...,  10, OFF],
	[  7, OFF, ..., ...,   5, ..., ..., OFF],
	[  5, OFF, ..., ...,   7, ..., ..., OFF],
	[  0, OFF,   2, ...,   3, OFF, ..., ...],
	[  0, OFF,   3, ...,   5, OFF, ..., ...],
	[  0, OFF,   3, ...,   2, OFF, ..., ...],
	[  0, OFF,   5, ...,   3, OFF, ..., ...],
	[  3, ...,   2, OFF,  -2, ...,  -1, OFF],
	[  0, OFF,   2, ...,   0, ..., OFF, ...],
	[  0, OFF,  -2, ...,   0, ..., OFF, ...],
]

SOURCES = {
	2: lambda : random.choice(SOURCE_2),
	3: lambda : random.choice(SOURCE_3),
	4: lambda : random.choice(SOURCE_4),
}

PATTERN_PATTERN = [
	#4, 4, 4, 4,
	#4, 3, 2, 4, 3,
	#4, 3, 3, 3, 3,
	4, 3, 3, 4, 2,
	#4, 4, 3, 3, 2,
	#4, 4, 3, 2, 3,
	#4, 2, 3, 2, 3, 2,
	#4, 3, 3, 2, 2, 2,
	#4, 2, 2, 4, 2, 2,
]
pat = []

def pat_starts_with_base(p):
	return [v for v in p if v != OFF and v != ...][0] == 0

def gen_base_pat():
	pat = []
	for sz in PATTERN_PATTERN:
		while True:
			p = SOURCES[sz]()
			puniqnote = [n for n in p if n != OFF and n != ...]
			puniqnote = set(puniqnote)
			if len(puniqnote) > 1: continue
			if pat or pat_starts_with_base(p): break
		pat += p
	assert len(pat) == 32

	return pat

def reverse_pat(pat):
	in_pat = pat
	pat = []
	last_note = None
	for n in in_pat:
		if n == ...:
			pat.append(n)
		elif n == OFF:
			assert last_note != None
			pat.append(last_note)
			last_note = None
		else:
			#assert last_note == None
			pat.append(last_note if last_note is not None else OFF)
			last_note = n

	return pat[1:][::-1] + [OFF]


def mutate_pat(pat, min_idx=0, max_idx=None):
	pat = list(pat)
	max_idx = max_idx if max_idx is not None else len(PATTERN_PATTERN)-1

	idx = random.randint(min_idx, max_idx)
	offs = sum(PATTERN_PATTERN[:idx])
	sz = PATTERN_PATTERN[idx]
	lpat = pat[offs*2:(offs+sz)*2]
	while True:
		pat = pat[:offs*2] + SOURCES[sz]() + pat[(offs+sz)*2:]
		if pat_starts_with_base(pat):
			break

	npat = pat[offs*2:(offs+sz)*2]
	print("%d:%d: %s -> %s" % (
		offs, sz, lpat, npat
	))
	assert len(pat) == 32
	return pat

patA = gen_base_pat()
patAp = patA
patB = patA
patC = patA

bass = BassInstrument()
d_kick = KickDrum()
d_snare = SnareDrum()
d_hihat = HihatDrum()
gtick = 0
pat = None

HIHAT_VOL_GROOVE = [
	1.0, 0.6, 0.7, 0.6,
	0.8, 0.6, 0.7, 0.6,
	0.9, 0.6, 0.7, 0.6,
	0.8, 0.6, 0.7, 0.6,
]
while True:
	tick = (gtick%14)
	row = (gtick//14)

	if row%8 == 0 and tick == 0:
		BASE_NOTE = BASE_NOTES[(row//8)%len(BASE_NOTES)]
		if row%32 == 0:
			if row != 0 and (row//32)%2 == 0:
				PATTERN_PATTERN = []
				accum = 0
				plrem = 16
				while plrem > 5:
					v = random.choice([2,3,4])
					PATTERN_PATTERN.append(v)
					plrem -= v
				if plrem == 5:
					v = random.choice([2,3])
					PATTERN_PATTERN.append(v)
					PATTERN_PATTERN.append(5-v)
				else:
					PATTERN_PATTERN.append(plrem)
					
				random.shuffle(PATTERN_PATTERN)
				assert sum(PATTERN_PATTERN) == 16

			print(row//32, PATTERN_PATTERN)
			#PATTERN_PATTERN = []
			#random.shuffle(PATTERN_PATTERN)
			PATTERN_ACCUM = list(itertools.accumulate(PATTERN_PATTERN))
			PATTERN_ACCUM = [0] + PATTERN_ACCUM

			#patA = patC
			patA = patB
			if row != 0 and (row//32)%2 == 0:
				patA = mutate_pat(patA)
				patA = mutate_pat(patA)
			#patA = reverse_pat(patA)
			#patA = mutate_pat(patA, max_idx=0)

			patAp = mutate_pat(patA, min_idx=0, max_idx=len(PATTERN_PATTERN)-1)
			patB = mutate_pat(patA, min_idx=2)
			patB = mutate_pat(patB, min_idx=len(PATTERN_PATTERN)-1)
			patC = mutate_pat(patA)
			patC = mutate_pat(patC)
			patC = mutate_pat(patC)
			patC = mutate_pat(patC)

		pat = [patA, patB, patAp, patC][(row%32)//8]

	for (i, v,) in enumerate(TICK_STEPS):
		if tick == v:
			n = pat[i+(row%8)*4]
			#print(row%8, i, v, n)
			if n == OFF:
				bass.stop()
			elif n != ...:
				bass.play(n)
				#if n == 0: d_kick.play()

	if True:
		#if row%2 == 0 and tick == 0: d_kick.play()
		if row%8 in [0, 2, 6] and tick == 0: d_kick.play()
		if row%8 in [3, 4] and tick == TICK_STEPS[2]: d_kick.play()
		if row%4 == 2 and tick == 0: d_snare.play()
	else:
		if tick == TICK_STEPS[0] and ((row%8)*2+0) in PATTERN_ACCUM[0::2]: d_kick.play()
		if tick == TICK_STEPS[2] and ((row%8)*2+1) in PATTERN_ACCUM[0::2]: d_kick.play()
		if tick == TICK_STEPS[0] and ((row%8)*2+0) in PATTERN_ACCUM[1::2]: d_snare.play()
		if tick == TICK_STEPS[2] and ((row%8)*2+1) in PATTERN_ACCUM[1::2]: d_snare.play()

	if tick == 0:
		d_hihat.play(HIHAT_VOL_GROOVE[(row%8)*2+0])
	elif tick == TICK_STEPS[2]:
		d_hihat.play(HIHAT_VOL_GROOVE[(row%8)*2+1])

	a_len = SLICELEN
	L = [0.0 for i in range(SLICELEN)]
	A = array.array("h")
	d_kick.mix(L, len(L))
	d_snare.mix(L, len(L))
	d_hihat.mix(L, len(L))
	bass.mix(L, len(L))
	A.fromlist([int(round(max(-1.0, min(1.0, v*GLOBAL_VOL))*32000.0)) for v in L])
	fp.stdin.write(A.tobytes())

	gtick += 1

# flush with silence because fuck you is why
fp.stdin.write(b"\x00"*2*MIXFREQ)

fp.stdin.flush()
fp.stdin.close()
fp.wait()

