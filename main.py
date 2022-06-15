import pygame, math, random
pygame.init()

screenRes = (800, 800)
screen = pygame.display.set_mode(screenRes)
pygame.display.set_caption("Game")
font = pygame.font.SysFont("Arial", 14)
fpsFont = pygame.font.SysFont("Lucida Console", 20)
running = True
currentlyHighlighted = 0
clock = pygame.time.Clock()

class Planet():
	AU = 149.6e6 * 1000
	G = 6.67428e-11

	def __init__(self, pos, radius, color, mass, velY, sun = False, velX = 0):
		self.pos = pos
		self.velX = velX
		self.velY = velY

		self.radius = radius
		self.color = color
		self.mass = mass

		self.sun = sun
		self.toSun = 0

		self.orbitPath = []
		self.focused = False

	def draw(self, planetList):
		self.changePositions(planetList)

		self.drawPosX = self.pos[0] * SCALE + screenRes[0] / 2 + posShiftX
		self.drawPosY = self.pos[1] * SCALE + screenRes[1] / 2 + posShiftY

		self.orbitPath.append(self.pos)

		orbitPoints = [(point[0] * SCALE + screenRes[0] / 2 + posShiftX,
		                point[1] * SCALE + screenRes[1] / 2 + posShiftY)
						for point in self.orbitPath]

		if len(self.orbitPath) > 1: pygame.draw.lines(screen, tuple(color / 3 for color in self.color), False, orbitPoints, 2)

		pygame.draw.circle(screen, self.color, (self.drawPosX, self.drawPosY), self.radius / ((250 / self.AU) / SCALE))

		if self.focused:
			pygame.draw.circle(screen, (255, 0, 0), (self.drawPosX, self.drawPosY), self.radius / ((250 / self.AU) / SCALE), 3)

	def calculateForce(self, planet):
		temp = (planet.pos[0] - self.pos[0], planet.pos[1] - self.pos[1])
		self.distance = math.sqrt(temp[0] ** 2 + temp[1] ** 2)

		if planet.sun: self.toSun = self.distance

		try: forceC = self.G * planet.mass * self.mass / self.distance ** 2
		except ZeroDivisionError: return (0, 0)
		theta = math.atan2(temp[1], temp[0])

		return math.cos(theta) * forceC, math.sin(theta) * forceC

	def changePositions(self, planetList):
		totalForceX = totalForceY = 0

		for planet in planetList:
			if planet == self: continue

			forceX, forceY = self.calculateForce(planet)

			totalForceX += forceX
			totalForceY += forceY

		self.velX += totalForceX / self.mass * TIMESTEP
		self.velY += totalForceY / self.mass * TIMESTEP

		self.pos = (self.pos[0] + self.velX * TIMESTEP, self.pos[1] + self.velY * TIMESTEP)

planets = {
	"Sun":     Planet((0, 0), 30, (255, 255, 0), 1.98892 * 10**30, 0, True),
	"Mercury": Planet((0.387 * Planet.AU, 0), 8, (80, 78, 81), 3.30 * 10**23, -47400),
	"Venus":   Planet((0.723 * Planet.AU, 0), 14, (255, 255, 255), 4.8685 * 10**24, -35020),
	"Earth":   Planet((-Planet.AU, 0), 16, (100, 149, 237), 5.9742 * 10**24, 29783),
	"Mars":    Planet((-1.524 * Planet.AU, 0), 12, (188, 39, 50), 6.39 * 10**23, 24077),
	"Jupiter": Planet((5.204 * Planet.AU, 0), 176, (112, 47, 1), 1.898 * 10**27, -13070),
	"Saturn":  Planet((9.576 * Planet.AU, 0), 144, (217, 175, 117), 5.6834 * 10**26, -9680),
	"Uranus":  Planet((19.1913 * Planet.AU, 0), 64, (163, 243, 242), 8.681 * 10**25, -6800),
	"Neptune": Planet((30.07 * Planet.AU, 0), 64, (93, 112, 156), 1.02413 * 10**26, -5430),
}

TIMESTEP = 14400
DEFSCALE = SCALE = 250 / Planet.AU

posShiftX = 0
posShiftY = 0
currentlyPressedR = False
currentlyPressedL = False
currentOffset = (0, 0)
clickPos = (0, 0)
mouseOffset = (0, 0)

userPlanets = 0
currentGameTime = 0

while running:
	clock.tick()
	screen.fill((0,0,0))

	keys = pygame.key.get_pressed()

	highlightable = [None, ] + list(planets.keys())


	for event in pygame.event.get():
		if event.type == pygame.QUIT: running = 0
		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_LEFT:  currentlyHighlighted -= 1
			if event.key == pygame.K_RIGHT: currentlyHighlighted += 1

			if event.key == pygame.K_c: [planets[planet].orbitPath.clear() for planet in planets]

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				try:

					clickPos = event.pos
					currentlyPressedL = True

				except AttributeError: pass

			if event.button == 4: SCALE += 1.67112299465241e-11
			if event.button == 5:
				SCALE -= 1.67112299465241e-11
				if SCALE < 0: SCALE += 1.67112299465241e-11

			if event.button == 3:
				pygame.mouse.get_rel()
				mousePos = pygame.mouse.get_pos()
				currentlyPressedR = True

		if event.type == pygame.MOUSEBUTTONUP:
			currentlyPressedL = False

			currentOffset = (currentOffset[0] + mouseOffset[0], currentOffset[1] + mouseOffset[1])
			mouseOffset = (0, 0)

			if event.button == 3:
				velocityChange = pygame.mouse.get_rel()

				positionX = mousePos[0] / SCALE - screenRes[0]/(2*SCALE) - posShiftX/SCALE
				positionY = mousePos[1] / SCALE - screenRes[1]/(2*SCALE) - posShiftY/SCALE

				color = tuple(random.randint(0, 255) for _ in range(3))
				planets[f"Planeta {userPlanets + 1}"] = Planet((positionX, positionY), 10, color, 5.9742 * 10**24, velocityChange[1] * 100, velX = velocityChange[0] * 100)
				userPlanets += 1

				currentlyPressedR = False

	if currentlyPressedL:
		try:
			temp = pygame.mouse.get_pos()

			mouseOffset = (temp[0] - clickPos[0], temp[1] - clickPos[1])

			posShiftX = currentOffset[0] + mouseOffset[0]
			posShiftY = currentOffset[1] + mouseOffset[1]

		except AttributeError: pass

	if currentlyPressedR:
		try: pygame.draw.line(screen, (255, 0, 0), mousePos, pygame.mouse.get_pos())
		except AttributeError: pass

	if keys[pygame.K_UP]: TIMESTEP += 7200
	if keys[pygame.K_DOWN]:
		TIMESTEP -= 7200
		if TIMESTEP < 0: TIMESTEP = 0

	currentGameTime += TIMESTEP

	for planet in planets:
		planets[planet].draw(planets.values())
		planets[planet].focused = False

	currentlyHighlighted = currentlyHighlighted % len(highlightable)

	try:             highlightedPlanet = planets[highlightable[currentlyHighlighted]]
	except KeyError: highlightedPlanet = None

	if type(highlightedPlanet) == Planet:
		highlightedPlanet.focused = True

		text = font.render(f"{highlightable[currentlyHighlighted]}", True, (255,255,255))
		screen.blit(text, ((screenRes[0] - text.get_width())/2, 20))

		text = font.render(f"Distance to sun: {round(highlightedPlanet.toSun / 1000000)}mln km", True, (255,255,255))
		screen.blit(text, ((screenRes[0] - text.get_width())/2, 50))

		text = font.render(f"Velocity: {round(math.sqrt(highlightedPlanet.velX**2+highlightedPlanet.velY**2)/1000, 3)}km/s", True, (255,255,255))
		screen.blit(text, ((screenRes[0] - text.get_width())/2, 70))


	text = font.render(f"Current time: {round(currentGameTime / 31000000, 2)} earth years", True, (255,255,255))
	screen.blit(text, ((screenRes[0] - text.get_width())/2, 0))

	text = fpsFont.render(str(round(clock.get_fps())), True, (0,255,0))
	screen.blit(text, (0, 0))

	pygame.draw.line(screen, (255, 255, 255), (300, 18.5), (500, 18.5))

	clock.tick()

	pygame.display.update()