# make each board solvable
# add fail conditions - needs fixing
# fix win conditions
# add GUI options

import os
import sys

os.chdir(sys.path[0])
sys.path.insert(1, "P://Python Projects/assets/")

from GameObjects import *
from colors import Color

width, height = ChangeScreenSize(height + 100, height + 100)


class Pipe(Button):
	# pipe types
	START = 0
	END = 1
	VERTICAL = 2
	HORIZONTAL = 3
	UL_CURVE = 4
	UR_CURVE = 5
	DL_CURVE = 6
	DR_CURVE = 7
	VERTICAL_SLOWED = 8
	HORIZONTAL_SLOWED = 9

	FLOW_MULTIPLYER = 1
	FLOW_DIFFICULTY_RATE = 1

	pipes = OpenFile("pipes.json")

	PIPE_INTERACTION_NAMES = {
		"up":    ["VERTICAL_SLOWED", "VERTICAL",   "DL_CURVE", "DR_CURVE", "START", "END"],
		"down":  ["VERTICAL_SLOWED", "VERTICAL",   "UL_CURVE", "UR_CURVE", "START", "END"],
		"left":  ["HORIZONTAL_SLOWED", "HORIZONTAL", "DR_CURVE", "UR_CURVE", "START", "END"],
		"right": ["HORIZONTAL_SLOWED", "HORIZONTAL", "DL_CURVE", "UL_CURVE", "START", "END"]
	}

	TYPE_NAMES = {
		"START":               0,
		"END":                 1,
		"VERTICAL":            2,
		"HORIZONTAL":          3,
		"UL_CURVE":            4,
		"UR_CURVE":            5,
		"DL_CURVE":            6,
		"DR_CURVE":            7,
		"VERTICAL_SLOWED":     8,
		"HORIZONTAL_SLOWED":   9
	}

	pipe_interactions = {
		"up":    [],
		"down":  [],
		"left":  [],
		"right": []
	}

	WATER_PATH = "textures/WATER.png"

	for direction in PIPE_INTERACTION_NAMES:
		for t in PIPE_INTERACTION_NAMES[direction]:
			pipe_interactions[direction].append(TYPE_NAMES[t])

	def Random(x, y, i, j, size, parent):
		return Pipe(x, y, size, parent, index=[i, j])

	def Start(rect, parent):
		return Pipe(rect.x, rect.y, (rect.w, rect.h), parent, start=True)

	def End(rect, parent):
		return Pipe(rect.x, rect.y, (rect.w, rect.h), parent, end=True)

	def GetStartEndRot(rect, parent_rect):
		if rect.x < parent_rect.x:
			return 90
		if rect.x >= parent_rect.x + parent_rect.w:
			return 270
		if rect.y < parent_rect.y:
			return 0
		if rect.y >= parent_rect.y + parent_rect.h:
			return 180

	def ChooseType():
		sum_weight = 0
		for i in range(2, len(Pipe.pipes)):
			sum_weight += Pipe.pipes[str(i)]["weight"] * 100

		rnd = randint(2, int(sum_weight))

		for i in range(2, len(Pipe.pipes)):
			if rnd < Pipe.pipes[str(i)]["weight"] * 100:
				return i
			rnd -= Pipe.pipes[str(i)]["weight"] * 100

		return 2

	def ChooseTexture(t):
		if t == Pipe.START or t == Pipe.END:
			return Pipe.pipes[str(t)]["file_path"], None
		else:
			return Pipe.pipes[str(t)]["file_path"], Pipe.pipes[str(t)]["rotation"]

	def FillRate(pipe):
		return Pipe.pipes[str(pipe.type)]["flow_rate"]

	def FillPipe(self):
		# fix rotation
		direction = None

		if self.type != Pipe.START and self.type != Pipe.END:
			for p in self.CheckConnectedPipes():
				if p.value == 1:
					if self.rect.x - self.rect.w == p.rect.x:
						direction = "left"
					if self.rect.x + self.rect.w == p.rect.x:
						direction = "right"
					if self.rect.y - self.rect.h == p.rect.y:
						direction = "up"
					if self.rect.y + self.rect.h == p.rect.y:
						direction = "down"

		water_img = Image(self.rect, Pipe.WATER_PATH)
		filled_pipe = Image(self.rect, Pipe.pipes[str(self.type)]["file_path"])
		unfilled_pipe = Image(self.rect, self.image)

		filled_pipe.Replace((171, 171, 171), (120, 120, 120))
		filled_pipe.Replace((0, 0, 0, 0), (255, 0, 255))

		filled_pipe.image = pg.transform.rotate(filled_pipe.image, self.rotation)
		filled_pipe.image.set_colorkey((120, 120, 120))
		water_img.image.blit(filled_pipe.image, (0, 0))

		value = self.value # change for curves to fit more nicely

		if direction == "left":
			water_img = water_img.image.subsurface((0, 0, value * self.rect.w, self.rect.h))
		elif direction == "right":
			water_img = water_img.image.subsurface(((1 - value) * self.rect.w, 0, value * self.rect.w, self.rect.h))
		elif direction == "up":
			water_img = water_img.image.subsurface((0, 0, self.rect.w, value * self.rect.h))
		elif direction == "down":
			water_img = water_img.image.subsurface((0, (1 - value) * self.rect.h, self.rect.w, value * self.rect.h))
		else:
			water_img = water_img.image

		water_img.set_colorkey((255, 0, 255))
		if direction == "left":
			unfilled_pipe.image.blit(water_img, (0, 0))
		elif direction == "right":
			unfilled_pipe.image.blit(water_img, ((1 - value) * self.rect.w, 0))
		elif direction == "up":
			unfilled_pipe.image.blit(water_img, (0, 0))
		elif direction == "down":
			unfilled_pipe.image.blit(water_img, (0, (1 - value) * self.rect.h))
		else:
			unfilled_pipe.image.blit(water_img, (0, 0))

		self.image = unfilled_pipe.image

		if self.value == 1:
			self.filled = True

	def __init__(self, x, y, size, parent, **kwargs):
		super().__init__((x, y, size[0], size[1]), (lightBlack, lightBlack, lightBlack), lists=[])
		self.parent = parent
		self.type = Pipe.ChooseType()
		self.start = False
		self.end = False
		self.vis_rect = self.rect.copy()
		self.swapping = False
		self.filled = False

		self.index = [None, None]

		for key, item in kwargs.items():
			setattr(self, key, item)

		self.value = 0
		if self.start:
			self.type = Pipe.START
			self.value = 1
		if self.end:
			self.type = Pipe.END
		
		if not self.start and not self.end:
			self.onClick = self.StartSwap
			self.onRelease = self.GetPipe
		
		self.file_path, self.rotation = Pipe.ChooseTexture(self.type)
		if self.rotation == None:
			self.rotation = Pipe.GetStartEndRot(self.rect, self.parent.rect)
		self.image = pg.transform.rotate(pg.transform.scale(pg.image.load(self.file_path), (self.rect.w, self.rect.h)), self.rotation)
		self.water_img = pg.transform.scale(pg.image.load(Pipe.WATER_PATH), (self.rect.w, self.rect.h))

		self.font = pg.font.SysFont("arial", 25)

	def __str__(self):
		return f"Pipe: {self.type} | rect: {self.rect} | vis_rect: {self.vis_rect} | value: {self.value}"

	def Draw(self):
		if not self.filled:
			if self.value > 0:
				self.FillPipe()

		screen.blit(self.image, self.vis_rect)

		if self.swapping:
			self.vis_rect.x, self.vis_rect.y = pg.mouse.get_pos()
			self.vis_rect.x -= self.vis_rect.w // 2
			self.vis_rect.y -= self.vis_rect.h // 2

	def StartSwap(self):
		if self.value == 0:
			self.swapping = True

	def GetPipe(self):
		if self.parent.rect.collidepoint(pg.mouse.get_pos()):
			for row in self.parent.grid:
				for pipe in row:
					if pipe != self:
						if pipe.rect.collidepoint(pg.mouse.get_pos()):
							if pipe.value == 0 and self.value == 0:
								self.Swap(pipe)
								return

		self.vis_rect = self.rect.copy()
		self.swapping = False

	def Swap(self, pipe):
		self.swapping = False

		i1, j1 = pipe.index.copy()
		i2, j2 = self.index.copy()
		temp = self.parent.grid[i1][j1]
		self.parent.grid[i1][j1] = self.parent.grid[i2][j2]
		self.parent.grid[i2][j2] = temp
		
		temp = (self.rect.copy(), self.index.copy(), self.rect.copy())

		self.rect = pipe.rect
		pipe.rect = temp[0]

		self.index = pipe.index
		pipe.index = temp[1]

		self.vis_rect = pipe.vis_rect
		pipe.vis_rect = temp[2]

	def IncreaseValue(self, step):
		self.value = Constrain(self.value + step, 0, 1)

	def GetLeft(self):
		if self.index[0] - 1 >= 0:
			return self.parent.grid[self.index[0] - 1][self.index[1]]

		if self.rect.x - self.rect.w == self.parent.start.rect.x and self.rect.y == self.parent.start.rect.y:
			return self.parent.start

	def GetRight(self):
		if self.index[0] + 1 < self.parent.num_of_cells[0]:
			return self.parent.grid[self.index[0] + 1][self.index[1]]
		
		if self.rect.x + self.rect.w == self.parent.start.rect.x and self.rect.y == self.parent.start.rect.y:
			return self.parent.start

	def GetUp(self):
		if self.index[1] - 1 >= 0:
			return self.parent.grid[self.index[0]][self.index[1] - 1]

		if self.rect.y - self.rect.h == self.parent.start.rect.y and self.rect.x == self.parent.start.rect.x:
			return self.parent.start

	def GetDown(self):
		if self.index[1] + 1 < self.parent.num_of_cells[1]:
			return self.parent.grid[self.index[0]][self.index[1] + 1]

		if self.rect.y + self.rect.h == self.parent.start.rect.y and self.rect.x == self.parent.start.rect.x:
			return self.parent.start

	def CheckConnectedPipes(self):
		pipes = []

		for connection in Pipe.pipes[str(self.type)]["connections"]:
			func = getattr(self, f"Get{connection[0].upper() + connection[1:]}")
			if func() != None:
				if func().type in Pipe.pipe_interactions[connection]:
					pipes.append(func())

		return pipes


class Board:
	allBoards = []

	# in seconds
	# determined by difficulty 
	FLOW_DELAY = 5
	START_TIME = dt.datetime.now()
	FILE_PATH = "textures/BOARD.png"

	def __init__(self, rect, num_of_cells, **kwargs):
		self.rect = pg.Rect(rect)
		self.num_of_cells = num_of_cells
		self.cell_size = [self.rect.w // self.num_of_cells[0], self.rect.h // self.num_of_cells[1]]
		
		self.image = pg.transform.scale(pg.image.load(Board.FILE_PATH), (width, height))

		for key, item in kwargs.items():
			setattr(self, key, item)

		self.Restart()

		self.font = pg.font.SysFont("arial", 32)

		self.finish_btn = Button((self.rect.x + self.rect.w + 10, self.rect.y + self.rect.h + 10, self.cell_size[0] - 10, self.cell_size[1] - 10),
		 (darkGray, darkWhite, lightBlue), text="Finish", onClick=self.Finish)

		self.restart_btn = Button((self.rect.x - self.cell_size[0], self.rect.y - self.cell_size[1], self.cell_size[0] - 10, self.cell_size[1] - 10),
		 (darkGray, darkWhite, lightBlue), text="Restart", onClick=self.Restart)

		self.difficulty_btn = Button((self.rect.x + self.rect.w + 10, self.rect.y - self.cell_size[1], self.cell_size[0] - 10, self.cell_size[1] - 10), 
		 (darkGray, darkWhite, lightBlue), text="Change\nDifficulty\n1", onClick=self.ChangeDifficulty, textData={"fontSize": 16, "alignText": "top"})

		self.difficulty = 1

		Board.allBoards.append(self)

	def Draw(self):
		DrawRectOutline(white, (self.rect.x - 1, self.rect.y - 1, self.rect.w + 2, self.rect.h + 2))

		# screen.blit(self.image, (0, 0))

		self.finish_btn.Draw()
		self.restart_btn.Draw()

		swapping_pipe = None
		for row in self.grid:
			for pipe in row:
				pipe.Draw()
				if pipe.swapping:
					swapping_pipe = pipe

				self.Update(pipe)

		if swapping_pipe != None:
			swapping_pipe.Draw()

		self.start.Draw()
		self.end.Draw()
		
		self.CheckWin(self.GetStartEndPipe(self.end))

	def HandleEvent(self, event):
		for row in self.grid:
			for pipe in row:
				pipe.HandleEvent(event)

	def Update(self, pipe):
		if (dt.datetime.now() - Board.START_TIME).seconds >= Board.FLOW_DELAY:
			for p in pipe.CheckConnectedPipes():
				if p.value == 1:
					pipe.IncreaseValue(Pipe.FillRate(pipe) * Pipe.FLOW_MULTIPLYER * Pipe.FLOW_DIFFICULTY_RATE)
					self.CheckFail(pipe)
					break
	
	def CheckWin(self, pipe):
		if pipe[0].value == 1:
			if pipe[1] in Pipe.pipes[str(self.end.type)]["connections"]:
				self.end.IncreaseValue(Pipe.FillRate(self.end) * Pipe.FLOW_MULTIPLYER * Pipe.FLOW_DIFFICULTY_RATE)
				if self.end.value == 1:
					print("win")

	def CheckFail(self, pipe):
		if pipe.value == 1:
			connected_pipes = pipe.CheckConnectedPipes()

	def GetStartEndPipe(self, p):
		for row in self.grid:
			for pipe in row:
				rect = p.rect.copy()
				rect.x -= rect.w
				if rect.colliderect(pipe.rect):
					return pipe, "left"
				rect = p.rect.copy()
				rect.x += rect.w
				if rect.colliderect(pipe.rect):
					return pipe, "right"
				rect = p.rect.copy()
				rect.y -= rect.h
				if rect.colliderect(pipe.rect):
					return pipe, "up"
				rect = p.rect.copy()
				rect.y += rect.h
				if rect.colliderect(pipe.rect):
					return pipe, "down"

	def Finish(self):
		Pipe.FLOW_MULTIPLYER = 10

	def Restart(self):
		self.grid = [[Pipe.Random(self.rect.x + (x * self.cell_size[0]), self.rect.y + (y * self.cell_size[1]), x, y, self.cell_size, self) for y in range(self.rect.h // self.cell_size[1])] for x in range(self.rect.w // self.cell_size[0])]

		#                 board side     cell position
		start_pos = [randint(0, 3), randint(0, self.num_of_cells[0] - 1)]
		end_pos = [randint(0, 3), randint(0, self.num_of_cells[0] - 1)]
		while end_pos[0] == start_pos[0]:
			end_pos = [randint(0, 3), randint(0, self.num_of_cells[0] - 1)]

		# improve this
		if start_pos[0] == 0:
			start_rect = (self.rect.x + start_pos[1] * self.cell_size[0], self.rect.y - self.cell_size[1], self.cell_size[0], self.cell_size[1])
		if start_pos[0] == 1:
			start_rect = (self.rect.x + start_pos[1] * self.cell_size[0], self.rect.y + self.rect.h, self.cell_size[0], self.cell_size[1])
		if start_pos[0] == 2:
			start_rect = (self.rect.x - self.cell_size[0], self.rect.y + start_pos[1] * self.cell_size[1], self.cell_size[0], self.cell_size[1])
		if start_pos[0] == 3:
			start_rect = (self.rect.x + self.rect.w, self.rect.y + start_pos[1] * self.cell_size[1], self.cell_size[0], self.cell_size[1])
		
		if end_pos[0] == 0:
			end_rect = (self.rect.x + end_pos[1] * self.cell_size[0], self.rect.y - self.cell_size[1], self.cell_size[0], self.cell_size[1])
		if end_pos[0] == 1:
			end_rect = (self.rect.x + end_pos[1] * self.cell_size[0], self.rect.y + self.rect.h, self.cell_size[0], self.cell_size[1])
		if end_pos[0] == 2:
			end_rect = (self.rect.x - self.cell_size[0], self.rect.y + end_pos[1] * self.cell_size[1], self.cell_size[0], self.cell_size[1])
		if end_pos[0] == 3:
			end_rect = (self.rect.x + self.rect.w, self.rect.y + end_pos[1] * self.cell_size[1], self.cell_size[0], self.cell_size[1])
		

		self.start = Pipe.Start(pg.Rect(start_rect), self)
		self.end = Pipe.End(pg.Rect(end_rect), self)

		Pipe.FLOW_MULTIPLYER = 1
		Board.START_TIME = dt.datetime.now()

	def ChangeDifficulty(self):
		if self.difficulty + 1 > 3:
			self.difficulty = 1
		else:
			self.difficulty += 1

		Pipe.FLOW_DIFFICULTY_RATE = self.difficulty

		self.difficulty_btn.UpdateText(f"Change\nDifficulty\n{self.difficulty}")


def DrawLoop():
	screen.fill(lightBlack)

	DrawAllGUIObjects()

	for board in Board.allBoards:
		board.Draw()

	pg.display.update()


def HandleEvents(event):
	HandleGui(event)

	if event.type == pg.KEYDOWN:
		if event.key == pg.K_SPACE:
			print(clock.get_fps())

	for board in Board.allBoards:
		board.HandleEvent(event)


Board((width // 2 - 300, height // 2 - 300, 600, 600), (6, 6))


while RUNNING:
	clock.tick_busy_loop(FPS)
	deltaTime = clock.get_time()
	for event in pg.event.get():
		if event.type == pg.QUIT:
			RUNNING = False
		if event.type == pg.KEYDOWN:
			if event.key == pg.K_ESCAPE:
				RUNNING = False

		HandleEvents(event)

	DrawLoop()
