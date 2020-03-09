class Customer:
	x = None
	y = None
	reward = None
	reached = False

	def __init__(self, line):
		self.x = int(line.split()[0])
		self.y = int(line.split()[1])
		self.reward = int(line.split()[2])

	def __str__(self):
		return f'x: {self.x}, y: {self.y}, r: {self.reward}'

class Reply:
	x = None
	y = None
	path2customer = None

	def __init__(self, x, y, directions):
		self.x = x
		self.y = y
		self.path2customer = directions

	def __str__(self):
		return f'{self.x} {self.y} {self.path2customer}'
