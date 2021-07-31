from itertools import cycle
import random
import sys
import math

import pygame
from pygame.locals import *

# Default settings
nFPS = 30
oFont = ''
nVolume = .2
nScrWidth  = 320
nScrHeight = 640
# Amount by which base can maximum shift to left
nPipeGapSize  = 108 # gap between upper and lower part of pipe
nBaseY        = nScrHeight * 0.80
# image, sound and hitmask dicts
fImages = {}
fSounds = {} 
fHitMask = {}
# True if the user plays the fury mode
bFuryMode = True
# In fury mode, the pipe sapwn system is different than in
# normal mode, we add pipes with a "timer" (a frame counter)
nFURYMODE_FRAMES_TO_SPAWN_PIPES = 35
# pipes particles amount (for each pipe)
nFURYMODE_PARTICLES = 8
# max particles for each pipe hit
nFURYMODE_PARTICLES_MAX = 48

# list of all possible players (tuple of 3 positions of flap)
fPLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
fBACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
fPIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)

try:
    xrange
except NameError:
    xrange = range


def main():
    global oScreen, oFPSClock, oFont, nScrWidth

    #pygame
    pygame.init()
    oFPSClock = pygame.time.Clock()
    infoObject = pygame.display.Info()
    nScrWidth = infoObject.current_w // 2
    oScreen = pygame.display.set_mode((nScrWidth, nScrHeight))
    #Default Font to show Text
    #oFont = pygame.font.Font(pygame.font.get_default_font(), 18)
    #Window Title
    pygame.display.set_caption('Flappy Bird: Arcade Mode [by Rafa10]')

    # numbers sprites for score display
    fImages['numbers'] = []
    for i in range(10):
        img = pygame.image.load('assets/sprites/' + str(i) + '.png').convert_alpha()
        fImages['numbers'].append(img)
    # game over sprite
    fImages['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
    # message sprite for welcome screen
    fImages['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
    # base (ground) sprite
    fImages['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()
    fImages['base'] = pygame.transform.scale(fImages['base'], (nScrWidth-1,int(nScrHeight*.22)) )
    # the "fury mode" button for welcome screen (with the key)
    fImages['furymode'] = pygame.image.load('assets/sprites/furymode.png').convert_alpha()

    # sound ext type
    if 'win' in sys.platform:
        soundExt = '.wav'
    else:
        soundExt = '.ogg'

    # sound files and volume
    fSounds['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
    fSounds['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
    fSounds['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
    fSounds['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
    fSounds['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)
    for key in fSounds:
        fSounds[key].set_volume( nVolume ) 

    while True:
        # select random background sprites
        randBg = random.randint(0, len(fBACKGROUNDS_LIST) - 1)
        fImages['background'] = pygame.image.load(fBACKGROUNDS_LIST[randBg]).convert()
        fImages['background'] = pygame.transform.scale(fImages['background'], (nScrWidth,nScrHeight) )

        # select random player sprites
        randPlayer = random.randint(0, len(fPLAYERS_LIST) - 1)
        fImages['player'] = (
            pygame.image.load(fPLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(fPLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(fPLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # select random pipe sprites
        pipeindex = random.randint(0, len(fPIPES_LIST) - 1)
        fImages['pipe'] = (
            pygame.transform.rotate(
                pygame.image.load(fPIPES_LIST[pipeindex]).convert_alpha(), 180),
            pygame.image.load(fPIPES_LIST[pipeindex]).convert_alpha(),
        )

        # pipes' particles for fury mode
        if pipeindex == 0:
            fImages['pipe-particle'] = []
            for i in range(8):
                img = pygame.image.load('assets/sprites/particles-green-' + str(i) + '.png').convert_alpha()
                fImages['pipe-particle'].append(img)

        else:
            fImages['pipe-particle'] = []
            for i in range(8):
                img = pygame.image.load('assets/sprites/particles-red-' + str(i) + '.png').convert_alpha()
                fImages['pipe-particle'].append(img)

        # hismask for pipes
        fHitMask['pipe'] = (
            getHitmask(fImages['pipe'][0]),
            getHitmask(fImages['pipe'][1]),
        )

        # hitmask for player
        fHitMask['player'] = (
            getHitmask(fImages['player'][0]),
            getHitmask(fImages['player'][1]),
            getHitmask(fImages['player'][2]),
        )

        movementInfo = showWelcomeAnimation()
        crashInfo = mainGame(movementInfo)
        showGameOverScreen(crashInfo)


def showWelcomeAnimation():
    """Shows welcome screen animation of flappy bird"""

    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    if nScrWidth > 440:
        playerx = int(nScrWidth // 3)
    else:
        playerx = int(nScrWidth // 2)
    playery = int((nScrHeight - fImages['player'][0].get_height()) / 2)

    messagex = int((nScrWidth - fImages['message'].get_width()) / 2)
    messagey = int(nScrHeight * 0.12)

    furymodex = int((nScrWidth - fImages['furymode'].get_width()) / 2)
    furymodey = int(nScrHeight * 0.90)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = fImages['base'].get_width() - fImages['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                fSounds['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }

        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        oScreen.blit(fImages['background'], (0,0))
        oScreen.blit(fImages['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        oScreen.blit(fImages['message'], (messagex, messagey))
        oScreen.blit(fImages['base'], (basex, nBaseY))
        oScreen.blit(fImages['furymode'], (furymodex, furymodey))

        pygame.display.update()
        oFPSClock.tick(nFPS)


def mainGame(movementInfo):
    global nFURYMODE_FRAMES_TO_SPAWN_PIPES

    nScore = 0
    nLives = 10
    playerIndex = 0
    loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']

    if nScrWidth > 440:
        playerx, playery = int(nScrWidth // 3), movementInfo['playery']
    else:
        playerx, playery = int(nScrWidth // 5), movementInfo['playery']

    basex = movementInfo['basex']
    baseShift = fImages['base'].get_width() - fImages['background'].get_width()

    # no need to spawn pipes at start
    if bFuryMode:
        # list of upper pipes
        upperPipes = []

        # list of lowerpipe
        lowerPipes = []

        # list of particles
        # a particle is an object with attributes:
        # {'x': position-x, 'y': position-y,
        # 'vx': velocity-x, 'vy': velocity-y,
        # 'i': index in textures list} 
        particles = []

    else:
        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        nPos = 200
        # list of upper pipes
        upperPipes = [
            {'x': nScrWidth + nPos, 'y': newPipe1[0]['y']},
            {'x': nScrWidth + nPos + (nScrWidth / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        lowerPipes = [
            {'x': nScrWidth + nPos, 'y': newPipe1[1]['y']},
            {'x': nScrWidth + nPos + (nScrWidth / 2), 'y': newPipe2[1]['y']},
        ]

    pipeVelX = -4

    # player velocity, max velocity, downward acceleration, acceleration on flap
    playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
    playerMaxVelY =  10   # max vel along Y, max descend speed
    playerMinVelY =  -8   # min vel along Y, max ascend speed
    playerAccY    =   1   # players downward acceleration
    playerRot     =  45   # player's rotation
    playerVelRot  =   3   # angular speed
    playerRotThr  =  20   # rotation threshold
    playerFlapAcc =  -9   # players speed on flapping
    playerFlapped = False # True when player flaps

    # The counter to spawn new pipes 
    furymodePipeFrameCounter = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > -2 * fImages['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    fSounds['wing'].play()

        # check for crash here
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                               upperPipes, lowerPipes)

        if crashTest[0]:
            # the player hits a pipe in fury mode
            if bFuryMode and nLives > 0 and not crashTest[1]:
                spawnParticles(particles, crashTest[3])
                # remove the pipe
                # it's an upper pipe
                if crashTest[2]:
                    upperPipes.remove(crashTest[3])
                # it's a lower pipe
                else:
                    lowerPipes.remove(crashTest[3])
                nLives -= 1
            else:
                return {
                    'y': playery,
                    'groundCrash': crashTest[1],
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'nScore': nScore,
                    'nCrash': nLives,
                    'playerVelY': playerVelY,
                    'playerRot': playerRot
                }

        # check for score
        playerMidPos = playerx + fImages['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + fImages['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                nScore += 1
                if (nScore % 25) == 0:
                    nLives += 1
                fSounds['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)

        # rotate the player
        if playerRot > -90:
            playerRot -= playerVelRot

        # player's movement
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            playerRot = 45

        playerHeight = fImages['player'][playerIndex].get_height()
        playery += min(playerVelY, nBaseY - playery - playerHeight)

        # move pipes to left
        for uPipe in upperPipes:
            uPipe['x'] += pipeVelX

        for lPipe in lowerPipes:
            lPipe['x'] += pipeVelX

        # update (add / remove) pipes and particles
        if bFuryMode:
            furymodePipeFrameCounter += 1
            # the counter has the max value, we must spawn new pipes
            if furymodePipeFrameCounter == nFURYMODE_FRAMES_TO_SPAWN_PIPES:
                # counter reset
                furymodePipeFrameCounter = 0
                
                # pipe spawn
                pipes = getRandomPipe()
                upperPipes.append(pipes[0])
                lowerPipes.append(pipes[1])

            # check if a pipe must be removed from the list
            for uPipe in upperPipes:
                if uPipe['x'] < -fImages['pipe'][0].get_width():
                    upperPipes.remove(uPipe)
            for lPipe in lowerPipes:
                if lPipe['x'] < -fImages['pipe'][0].get_width():
                    lowerPipes.remove(lPipe)

            # particles
            for particle in particles:
                # speed
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']

                # gravity
                particle['vy'] += playerAccY

                # remove if the particle is under the ground
                if particle['y'] >= nBaseY:
                    particles.remove(particle)

        else:
            # add new pipes when first pipe is about to touch left of screen
            if 0 < upperPipes[0]['x'] < 5:
                newPipe = getRandomPipe()
                upperPipes.append(newPipe[0])
                lowerPipes.append(newPipe[1])

            # remove first pipe if its out of the screen
            if upperPipes[0]['x'] < -fImages['pipe'][0].get_width():
                lowerPipes.pop(0)
                upperPipes.pop(0)

        # draw sprites
        oScreen.blit(fImages['background'], (0,0))

        for uPipe in upperPipes:
            oScreen.blit(fImages['pipe'][0], (uPipe['x'], uPipe['y']))

        for lPipe in lowerPipes:
            oScreen.blit(fImages['pipe'][1], (lPipe['x'], lPipe['y']))

        # pipes' particles
        if bFuryMode:
            for particle in particles:
                oScreen.blit(fImages['pipe-particle'][particle['i']], (particle['x'], particle['y']))

        oScreen.blit(fImages['base'], (basex, nBaseY))

        # print score so player overlaps the score
        showScore(nScore,nLives)

        # Player rotation has a threshold
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        
        playerSurface = pygame.transform.rotate(fImages['player'][playerIndex], visibleRot)
        oScreen.blit(playerSurface, (playerx, playery))

        pygame.display.update()
        oFPSClock.tick(nFPS)

def showGameOverScreen(crashInfo):
    """crashes the player down ans shows gameover image"""

    nScore  = crashInfo['nScore']
    nCrash  = crashInfo['nCrash']
    playerx = nScrWidth * 0.2
    playery = crashInfo['y']
    playerHeight = fImages['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7

    basex = crashInfo['basex']

    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # play hit and die sounds
    fSounds['hit'].play()
    if not crashInfo['groundCrash']:
        fSounds['die'].play()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery + playerHeight >= nBaseY - 1:
                    return

        # player y shift
        if playery + playerHeight < nBaseY - 1:
            playery += min(playerVelY, nBaseY - playery - playerHeight)

        # player velocity change
        if playerVelY < 15:
            playerVelY += playerAccY

        # rotate only when it's a pipe crash
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        # draw sprites
        oScreen.blit(fImages['background'], (0,0))

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            oScreen.blit(fImages['pipe'][0], (uPipe['x'], uPipe['y']))
            oScreen.blit(fImages['pipe'][1], (lPipe['x'], lPipe['y']))

        oScreen.blit(fImages['base'], (basex, nBaseY))
        showScore(nScore,nCrash)

        playerSurface = pygame.transform.rotate(fImages['player'][1], playerRot)
        gameoverx = int((nScrWidth - fImages['gameover'].get_width()) / 2)
        gameovery = int(nScrHeight * 0.44)
        oScreen.blit(playerSurface, (playerx,playery))
        oScreen.blit(fImages['gameover'], (gameoverx, gameovery))

        oFPSClock.tick(nFPS)
        pygame.display.update()

def playerShm(playerShm):
    """oscillates the value of playerShm['val'] between 8 and -8"""
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1

    if playerShm['dir'] == 1:
         playerShm['val'] += 1
    else:
        playerShm['val'] -= 1

def getRandomPipe():
    """ returns a randomly generated pipe """
    # y of gap between upper and lower pipe
    gapY = random.randrange(0, int(nBaseY * 0.6 - nPipeGapSize))
    gapY += int(nBaseY * 0.2)
    pipeHeight = fImages['pipe'][0].get_height()
    pipeX = nScrWidth + 10

    return [
        {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
        {'x': pipeX, 'y': gapY + nPipeGapSize}, # lower pipe
    ]

def showScore(nScore,nCrash):
    """displays score in center of screen"""
    scoreDigits = [int(x) for x in list(str(nScore))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += fImages['numbers'][digit].get_width()

    Xoffset = ( nScrWidth / 3 ) - totalWidth

    for digit in scoreDigits:
        oScreen.blit(fImages['numbers'][digit], (Xoffset, nScrHeight * 0.92))
        Xoffset += fImages['numbers'][digit].get_width()

    scoreDigits = [int(x) for x in list(str(nCrash))]
    totalWidth = 0 # total width of all numbers to be printed

    for digit in scoreDigits:
        totalWidth += fImages['numbers'][digit].get_width()

    Xoffset = Xoffset * 2

    for digit in scoreDigits:
        img = fImages['numbers'][digit].copy()
        drop(img)
        oScreen.blit(img, (Xoffset, nScrHeight * 0.92))
        Xoffset += img.get_width()

def spawnParticles(particles, pipe):
    """
        Add paticles to the particle list randomly
    generated with pipe's rectangle (hitbox)
    """
    global nFURYMODE_PARTICLES, nFURYMODE_PARTICLES_MAX, fSounds

    pipeW = fImages['pipe'][0].get_width()
    pipeH = fImages['pipe'][0].get_height()

    for i in range(nFURYMODE_PARTICLES_MAX):
        particle = {}
        particle['x'] = random.randint(pipe['x'], pipe['x'] + pipeW)
        particle['y'] = random.randint(pipe['y'], pipe['y'] + pipeH)
        particle['i'] = random.randint(1, nFURYMODE_PARTICLES) - 1

        # random angle for a minimum velocity
        vel = random.random() * 10 + 5
        aMin = -math.pi * .35
        aMax = math.pi * .25
        angle = random.random() * (aMax - aMin) + aMin
        particle['vx'] = math.cos(angle) * vel
        particle['vy'] = math.sin(angle) * vel

        particles.append(particle)

    # sound effect
    fSounds['hit'].play()

def checkCrash(player, upperPipes, lowerPipes):
    """returns True if player collides with base or pipes."""

    pi = player['index']
    player['w'] = fImages['player'][0].get_width()
    player['h'] = fImages['player'][0].get_height()

    # if player crashes into ground
    if player['y'] + player['h'] >= nBaseY - 1:
        return [True, True]

    else:
        playerRect = pygame.Rect(player['x'], player['y'],
                      player['w'], player['h'])
        pipeW = fImages['pipe'][0].get_width()
        pipeH = fImages['pipe'][0].get_height()

        for uPipe in upperPipes:
            # pipe rect
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)

            # player and pipe hitmasks
            pHitMask = fHitMask['player'][pi]
            uHitmask = fHitMask['pipe'][0]

            # if bird collided with pipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)

            if uCollide:
                # for fury mode we want to break the pipe so we
                # must return which pipe is colliding (lower or upper)
                if bFuryMode:
                    return [True, False, True, uPipe]
                # normal mode
                return [True, False]

        for lPipe in lowerPipes:
            # pipe rect
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and pipe hitmasks
            pHitMask = fHitMask['player'][pi]
            lHitmask = fHitMask['pipe'][0]

            # if bird collided with pipe
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if lCollide:
                # for fury mode we want to break the pipe so we
                # must return which pipe is colliding (lower or upper)
                if bFuryMode:
                    return [True, False, False, lPipe]
                # normal mode
                return [True, False]

    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    """Checks if two objects collide and not just their rects"""
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False

def getHitmask(image):
    """returns a hitmask using an image's alpha."""
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x,y))[3]))
    return mask

def drop(surface):
    w, h = surface.get_size()
    for x in range(w):
        for y in range(h):
            r = surface.get_at((x, y))[0]
            if r>150:
               r-=50
            g = surface.get_at((x, y))[1]
            if g>150:
               g-=50
            b = surface.get_at((x, y))[2]
            if b>150:
               b-=50
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a)) 

if __name__ == '__main__':
    main()
