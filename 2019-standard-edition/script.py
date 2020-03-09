from multiprocessing import Pool
from timeit import default_timer as timer

import numpy as np
from offices import Customer, Reply
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

filenames = ['0', '1', '2', '3', '4', '5']
filenames = ['4']
MAX_DISTANCE = 900

def getTerrainCost(t):
	# the pathfinding library interprets 0 as an obstacle
	if t is '#': return 0
	elif t is '~': return 800
	elif t is '*': return 200
	elif t is '+': return 150
	elif t is 'X': return 120
	elif t is '_': return 100
	elif t is 'H': return 70
	elif t is 'T': return 50

def findNearestStart(c, worldmap):
	upCost, rtCost, dwCost, ltCost = 999, 999, 999, 999

	if c.y-1 >= 0 and worldmap[c.y-1][c.x] != 0 and (c.x, c.y-1) not in customersCoords:
		upCost = worldmap[c.y-1][c.x]
	if c.x+1 < W and worldmap[c.y][c.x+1] != 0 and (c.x+1, c.y) not in customersCoords:
		rtCost = worldmap[c.y][c.x+1]
	if c.x+1 < H and worldmap[c.y+1][c.x] != 0 and (c.x, c.y+1) not in customersCoords:
		dwCost = worldmap[c.y+1][c.x]
	if c.x-1 >= 0 and worldmap[c.y][c.x-1] != 0 and (c.x-1, c.y) not in customersCoords:
		ltCost = worldmap[c.y][c.x-1]

	if min(upCost, rtCost, dwCost, ltCost) is upCost: return c.x, c.y-1
	elif min(upCost, rtCost, dwCost, ltCost) is rtCost: return c.x+1, c.y
	elif min(upCost, rtCost, dwCost, ltCost) is dwCost: return c.x, c.y+1
	elif min(upCost, rtCost, dwCost, ltCost) is ltCost: return c.x-1, c.y

def calcPathCostAndDirections(path, worldmap):
	cost, directions = 0, ''
	
	# path here is a list of tuples
	for i, t1 in enumerate(path[:-1]):
		t2 = path[i+1]
		if t1[0] == t2[0]:
			if t2[1] == t1[1]+1: directions += 'D'
			else: directions += 'U'
		else:
			if t2[0] == t1[0]+1: directions += 'R'
			else: directions += 'L'
		
		cost += worldmap[t2[1]][t2[0]]

	return cost, directions

def pathToOtherCustomers(c2):
	if (c2.x, c2.y) != (c.x, c.y) and np.sqrt((rX - c2.x)**2 + (rY - c2.y)**2) < MAX_DISTANCE:
		grid = Grid(matrix=worldmap)
		start = grid.node(rX, rY)
		end = grid.node(c2.x, c2.y)
		path, runs = AStarFinder(time_limit=60).find_path(start, end, grid)
		
		pathCost, dirs = calcPathCostAndDirections(path, worldmap)
		score = c2.reward - pathCost
		
		# If the customer gives me a negative score, fuck it
		if score > 0:
			print(f'\tC2:{c2.x},{c2.y}  {score}')
			c2.reached = True
			return (Reply(rX, rY, dirs), score)


totScore = 0
for filename in filenames:

	print(f'\n[{filename}] START')
	inizio = timer()

	# ===== INPUT PARSER =====
	with open(f'in/{filename}.txt') as f:
		# W = map width, H = map height, C = #customer, R = #reply
		W, H, C, R = map(int, f.readline().split())
		# Read customer headquarters
		customers = []
		for i in range(C):
			customers.append(Customer(f.readline()))
		# Read map
		worldmap = []
		for i in range(H):
			worldmap.append([getTerrainCost(c) for c in f.readline() if c is not '\n'])
	
	worldmap = np.asarray(worldmap)
	customersCoords = [(c.x, c.y) for c in customers]
	print(f'[{filename}] NC: {C} NR: {R}')

	# ===== CALC =====
	replys = []
	nR, i = 0, 0
	finalScore = 0
	while True:

		c = customers[i]
		rX, rY = findNearestStart(c, worldmap)
		# NearestStart not found
		if rX == 999 or rY == 999:
			i += 1
			continue
		
		# Find the path
		grid = Grid(matrix=worldmap)
		start = grid.node(rX, rY)
		end = grid.node(c.x, c.y)
		path, runs = AStarFinder().find_path(start, end, grid)
		
		# Calc the metrics
		pathCost, dirs = calcPathCostAndDirections(path, worldmap)
		# print(grid.grid_str(path=path, start=start, end=end))
		nearestScore = c.reward - pathCost
		
		# If the customer gives me a negative score, fuck it
		if nearestScore > 0 and nR < R:
			print(f'R:{rX},{rY}  C:{c.x},{c.y}  {nearestScore}')
			nearestReply = Reply(rX, rY, dirs)
			c.reached = True

			# From the Reply just added find the path to the other customers via multiprocessing
			pool = Pool()
			others = pool.map(pathToOtherCustomers, customers)
			pool.close()
			pool.join()

			# Get the results from the multiprocessing
			otherReplys = [o[0] for o in others if o is not None]
			otherScores = [o[1] for o in others if o is not None]
			replys = replys + [nearestReply] + otherReplys
			finalScore = finalScore + nearestScore + sum(otherScores)
			
			nR += 1
			
		# I can't add more Reply offices
		elif nR >= R:
			print('Can\'t add more reply offices')
			break
		
		i += 1
		# Cycled through all the customers as c
		if i >= C: break
	
	print(f'[{filename}] Score for all costumers: {finalScore}')


	# ===== WRITE OUTPUT =====
	with open(f'out/{filename}.txt', 'w') as f:
		for reply in replys:
			if reply.path2customer is not '':
				f.write(str(reply) + '\n')	

	print(f'[{filename}] DONE in {timer() - inizio}\n')
