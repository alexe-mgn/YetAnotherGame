import sys
from math import sqrt

# Vec2D comes from here: http://pygame.org/wiki/2DVectorClass
from vec2d import Vec2d
import pygame
from pygame.locals import *

pygame.init()

# --------------
# Constants
TITLE = "verletCloth01"
WIDTH = 600
HEIGHT = 600
FRAMERATE = 60
# How many iterations to run on our constraints per frame?
# This will 'tighten' the cloth, but slow the sim.
ITERATE = 5
GRAVITY = Vec2d(0.0, 0.05)
TSTEP = 2.8

# How many pixels to position between each particle?
PSTEP = int(WIDTH * .03)
# Offset in pixels from the top left of screen to position grid:
OFFSET = int(.25 * WIDTH)


# -------------
# Define helper functions, classes

class Particle(object):
    """
    Stores position, previous position, and where it is in the grid.
    """

    def __init__(self, screen, currentPos, gridIndex):
        # Current Position : m_x
        self.currentPos = Vec2d(currentPos)
        # Index [x][y] of Where it lives in the grid
        self.gridIndex = gridIndex
        # Previous Position : m_oldx
        self.oldPos = Vec2d(currentPos)
        # Force accumulators : m_a
        self.forces = GRAVITY
        # Should the particle be locked at its current position?
        self.locked = False
        self.followMouse = False

        self.colorUnlocked = Color('white')
        self.colorLocked = Color('green')
        self.screen = screen

    def __str__(self):
        return "Particle <%s, %s>" % (self.gridIndex[0], self.gridIndex[1])

    def draw(self):
        # Draw a circle at the given Particle.
        screenPos = (self.currentPos[0], self.currentPos[1])
        if self.locked:
            pygame.draw.circle(self.screen, self.colorLocked, (int(screenPos[0]),
                                                               int(screenPos[1])), 4, 0)
        else:
            pygame.draw.circle(self.screen, self.colorUnlocked, (int(screenPos[0]),
                                                                 int(screenPos[1])), 1, 0)


class Constraint(object):
    """
    Stores 'constraint' data between two Particle objects.  Stores this data
    before the sim runs, to speed sim and draw operations.
    """

    def __init__(self, screen, particles):
        self.particles = particles
        # Calculate restlength as the initial distance between the two particles:
        self.restLength = sqrt(abs(pow(self.particles[1].currentPos.x -
                                       self.particles[0].currentPos.x, 2) +
                                   pow(self.particles[1].currentPos.y -
                                       self.particles[0].currentPos.y, 2)))
        self.screen = screen
        self.color = Color('red')

    def __str__(self):
        return "Constraint <%s, %s>" % (self.particles[0], self.particles[1])

    def draw(self):
        # Draw line between the two particles.
        p1 = self.particles[0]
        p2 = self.particles[1]
        p1pos = (p1.currentPos[0],
                 p1.currentPos[1])
        p2pos = (p2.currentPos[0],
                 p2.currentPos[1])
        pygame.draw.aaline(self.screen, self.color,
                           (p1pos[0], p1pos[1]), (p2pos[0], p2pos[1]), 1)


class Grid(object):
    """
    Stores a grid of Particle objects.  Emulates a 2d container object.  Particle
    objects can be indexed by position:
        grid = Grid()
        particle = g[2][4]
    """

    def __init__(self, screen, rows, columns, step, offset):

        self.screen = screen
        self.rows = rows
        self.columns = columns
        self.step = step
        self.offset = offset

        # Make our internal grid:
        # _grid is a list of sublists.
        #    Each sublist is a 'column'.
        #        Each column holds a particle object per row:
        # _grid =
        # [[p00, [p10, [etc,
        #   p01,  p11,
        #   etc], etc],     ]]
        self._grid = []
        for x in range(columns):
            self._grid.append([])
            for y in range(rows):
                currentPos = (x * self.step + self.offset, y * self.step + self.offset)
                self._grid[x].append(Particle(self.screen, currentPos, (x, y)))

    def getNeighbors(self, gridIndex):
        """
        return a list of all neighbor particles to the particle at the given gridIndex:

        gridIndex = [x,x] : The particle index we're polling
        """
        possNeighbors = []
        possNeighbors.append([gridIndex[0] - 1, gridIndex[1]])
        possNeighbors.append([gridIndex[0], gridIndex[1] - 1])
        possNeighbors.append([gridIndex[0] + 1, gridIndex[1]])
        possNeighbors.append([gridIndex[0], gridIndex[1] + 1])

        neigh = []
        for coord in possNeighbors:
            if (coord[0] < 0) | (coord[0] > self.rows - 1):
                pass
            elif (coord[1] < 0) | (coord[1] > self.columns - 1):
                pass
            else:
                neigh.append(coord)

        finalNeighbors = []
        for point in neigh:
            finalNeighbors.append((point[0], point[1]))

        return finalNeighbors

    # --------------------------
    # Implement Container Type:

    def __len__(self):
        return len(self.rows * self.columns)

    def __getitem__(self, key):
        return self._grid[key]

    def __setitem__(self, key, value):
        self._grid[key] = value

    # def __delitem__(self, key):
    # del(self._grid[key])

    def __iter__(self):
        for x in self._grid:
            for y in x:
                yield y

    def __contains__(self, item):
        for x in self._grid:
            for y in x:
                if y is item:
                    return True
        return False


class ParticleSystem(Grid):
    """
    Implements the verlet particles physics on the encapsulated Grid object.
    """

    def __init__(self, screen, rows=10, columns=10, step=PSTEP, offset=OFFSET):
        super(ParticleSystem, self).__init__(screen, rows, columns, step, offset)

        # Generate our list of Constraint objects.  One is generated between
        # every particle connection.
        self.constraints = []
        for p in self:
            neighborIndices = self.getNeighbors(p.gridIndex)
            for ni in neighborIndices:
                # Get the neighbor Particle from the index:
                n = self[ni[0]][ni[1]]
                # Let's not add duplicate Constraints, which would be easy to do!
                new = True
                for con in self.constraints:
                    if n in con.particles and p in con.particles:
                        new = False
                if new:
                    self.constraints.append(Constraint(self.screen, (p, n)))

        # Lock our top left and right particles by default:
        self[0][0].locked = True
        self[1][0].locked = True
        self[-2][0].locked = True
        self[-1][0].locked = True

    def verlet(self):
        # Verlet integration step:
        for p in self:
            if not p.locked:
                # make a copy of our current position
                temp = Vec2d(p.currentPos)
                p.currentPos += p.currentPos - p.oldPos + p.forces * TSTEP ** 2
                p.oldPos = temp
            elif p.followMouse:
                temp = Vec2d(p.currentPos)
                p.currentPos = Vec2d(pygame.mouse.get_pos())
                p.oldPos = temp

    def satisfyConstraints(self):
        # Keep particles together:
        for c in self.constraints:
            delta = c.particles[0].currentPos - c.particles[1].currentPos
            deltaLength = sqrt(delta.dot(delta))
            try:
                # You can get a ZeroDivisionError here once, so let's catch it.
                # I think it's when particles sit on top of one another due to
                # being locked.
                diff = (deltaLength - c.restLength) / deltaLength
                if diff >= 0:
                    if not c.particles[0].locked:
                        c.particles[0].currentPos -= delta * 0.5 * diff
                    if not c.particles[1].locked:
                        c.particles[1].currentPos += delta * 0.5 * diff
            except ZeroDivisionError:
                pass

    def accumulateForces(self):
        # This doesn't do much right now, other than constantly reset the
        # particles 'forces' to be 'gravity'.  But this is where you'd implement
        # other things, like drag, wind, etc.
        for p in self:
            p.forces = GRAVITY

    def timeStep(self):
        # This executes the whole shebang:
        self.accumulateForces()
        self.verlet()
        for i in range(ITERATE):
            self.satisfyConstraints()

    def draw(self):
        """
        Draw constraint connections, and particle positions:
        """
        for c in self.constraints:
            c.draw()
        # for p in self:
        #    p.draw()

    def lockParticle(self):
        """
        If the mouse LMB is pressed for the first time on a particle, the particle
        will assume the mouse motion.  When it is pressed again, it will lock
        the particle in space.
        """
        mousePos = Vec2d(pygame.mouse.get_pos())
        for p in self:
            dist2mouse = sqrt(abs(pow(p.currentPos.x -
                                      mousePos.x, 2) +
                                  pow(p.currentPos.y -
                                      mousePos.y, 2)))
            if dist2mouse < 10:
                if not p.followMouse:
                    p.locked = True
                    p.followMouse = True
                    p.oldPos = Vec2d(p.currentPos)
                else:
                    p.followMouse = False

    def unlockParticle(self):
        """
        If the RMB is pressed on a particle, if the particle is currently
        locked or being moved by the mouse, it will be 'unlocked'/stop following
        the mouse.
        """
        mousePos = Vec2d(pygame.mouse.get_pos())
        for p in self:
            dist2mouse = sqrt(abs(pow(p.currentPos.x -
                                      mousePos.x, 2) +
                                  pow(p.currentPos.y -
                                      mousePos.y, 2)))
            if dist2mouse < 5:
                p.locked = False


# ------------
# Main Program
def main():
    # Screen Setup
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    # Create our grid of particles:
    particleSystem = ParticleSystem(screen, 12, 12)
    backgroundCol = Color('black')

    # main loop
    looping = True
    while looping:
        clock.tick(FRAMERATE)
        pygame.display.set_caption(
            "%s -- www.AKEric.com -- LMB: move\lock - RMB: unlock - fps: %.2f" % (TITLE, clock.get_fps()))
        screen.fill(backgroundCol)

        # Detect for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                looping = False
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    # See if we can make a particle follow the mouse and lock
                    # its position when done.
                    particleSystem.lockParticle()
                if event.button == 3:
                    # Try to unlock the current particles position:
                    particleSystem.unlockParticle()

        # Do stuff!
        particleSystem.timeStep()
        particleSystem.draw()

        # update our display:
        pygame.display.update()


# ------------
# Execution from shell\icon:
if __name__ == "__main__":
    print("Running Python version:", sys.version)
    print("Running PyGame version:", pygame.ver)
    print("Running %s.py" % TITLE)
    sys.exit(main())
