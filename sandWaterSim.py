import pygame
import numpy as np
import numba as nb
from math import ceil,floor
from random import randint
pygame.init()
# ss = sw,sh = 1024,512
ss = sw,sh = 1524,1012
screen = pygame.display.set_mode(ss)
fps = pygame.time.Clock()

pwidth = 180
pheight = 140

class Tick():
    @staticmethod 
    @nb.jit
    def checkTick(ticks,n):
        if ticks % n == 0:
            return True
        return False
gToSHratio = sh/1024
class BLOCK:

    _blocks = []
    sframe = np.full((pwidth,pheight,3),30.0)
    frame =sframe
    bframe =  np.full((pwidth,pheight),30).tolist()
    def __init__(self,color,props,pos) -> None:

        self.color = color
        
        self.properties = props["modifiers"]
        self.data = props["data"]
        self.pos = [int(pos[0]),int(pos[1])]
        self.updated = False
        self.deleted = False
        
        if "GRAVITY" in self.properties:
            self.fallingTime= 0
        if "SPREAD" in self.properties:
            self.maxSpread= 0
        if not "NONE" in self.properties:
            BLOCK.bframe[int(self.pos[0])][int(self.pos[1])] = self
            
            BLOCK._blocks.append(self)
        else:
            BLOCK.bframe[int(self.pos[0])][int(self.pos[1])] = 30
            BLOCK._blocks.append(self)
            
    @property
    def x(self):
        return self.pos[0]
    @property
    def y(self):
        return self.pos[1]
    # @nb.jit
    def Update(self,px,py):
            
            BLOCK.bframe[px][py] = 30
            BLOCK.frame[px][py]= [30,30,30]
            BLOCK.bframe[self.x][self.y] = self
    def Delete(self):
        
        BLOCK.bframe[self.y][self.x] = 30
    def Loop(self):
        self.updated = False
        prevX = self.x
        prevY = self.y
        blockUnder =BLOCK.bframe[self.x][self.y+1 if self.y < pheight-1 else pheight-1]

        grounded= isinstance(blockUnder, BLOCK)

        if grounded and not "LIQUID" in self.properties :
            grounded = False if "LIQUID" in blockUnder.properties else True
            if not grounded:
                if not "LIQUID" in self.properties:
                    BLOCK.bframe[self.x][self.y+1].pos[1] = self.y - 1
                    BLOCK.bframe[self.x][self.y+1].Update(self.x,self.y+1)


        if "GRAVITY" in self.properties:

            gravupdated=False
            #ADD ADDING GRAVITy
            
            if self.y+3 < pheight:
                if not grounded:
                    self.fallingTime+= 1
                    gravupdated = True
                    
                    gSpeed =floor((self.data["Mass"]/self.fallingTime)+1) if self.fallingTime > 10 else 4

                    if Tick.checkTick(ctick, gSpeed ):
                        

                        # self.pos[1]+=ceil((self.fallingTime/9.8)*gToSHratio)
                        self.pos[1]+=1


                        # print(self)
                        
                        
                        self.updated=True
        

            if not gravupdated:
                self.fallingTime=0
                # print(groundedthisTick)

        if "SPREAD" in self.properties and self.maxSpread<=self.data["MAXSPREAD"] and (True if not "SMOOTHING" in self.data else Tick.checkTick(ctick,self.data["SMOOTHING"])): #tick for more thicker stuff like mud
            supdated = False
            if self.y+4 < pheight and  grounded and self.x-1 > 0 and self.x+1 < pwidth:
                spreadrandom=randint(0,1)

                if spreadrandom:
                    if not isinstance(BLOCK.bframe[self.x+1][self.y+1], BLOCK):

                        self.pos[0]+=1
                        self.updated=True
                        supdated=True
                    elif not isinstance(BLOCK.bframe[self.x-1][self.y+1], BLOCK):

                        self.pos[0]-=1
                        self.updated=True
                        supdated=True
                else:
                    if not isinstance(BLOCK.bframe[self.x-1][self.y+1], BLOCK):

                        self.pos[0]-=1
                        self.updated=True
                        supdated=True
                    elif not isinstance(BLOCK.bframe[self.x+1][self.y+1], BLOCK):

                        self.pos[0]+=1
                        self.updated=True
                        supdated=True
            if supdated:
                self.maxSpread+=1
                # little variation
                if not randint(0,3):
                    self.maxSpread=0


        
        if "LIQUID" in self.properties:

            lupdated = False
            if self.y+3 < pheight and grounded and self.x-1 > 0 and self.x+2 < pwidth:
                spreadrandom=randint(0,1)

                if spreadrandom and not lupdated:
                    if not isinstance(BLOCK.bframe[self.x+1][self.y], BLOCK):

                        self.pos[0]+=1
                        self.updated=True
                        lupdated = True

                    elif not isinstance(BLOCK.bframe[self.x-1][self.y], BLOCK):

                        self.pos[0]-=1
                        self.updated=True
                        lupdated = True

                elif not lupdated:
                    if not isinstance(BLOCK.bframe[self.x-1][self.y], BLOCK):

                        self.pos[0]-=1
                        self.updated=True
                        lupdated = True
                    elif not isinstance(BLOCK.bframe[self.x+1][self.y], BLOCK):

                        self.pos[0]+=1
                        self.updated=True
                        lupdated = True
            if lupdated:
                # little variation
                if not randint(0,3):
                    self.maxSpread=0
                    

        if "EXPLOSION" in self.properties:
            canExplode = False
            for t in self.data["TRIGGER"]:
                if t == "COLLISION":
                    if isinstance(BLOCK.bframe[self.x][self.y+1 if self.y < pheight-1 else pheight-1],BLOCK):
                        canExplode=True
            
            if canExplode:

                if isinstance(BLOCK.bframe[self.x][self.y+1 if self.y < pheight-1 else pheight-1],BLOCK):
                    NUKEDBLOCK(self.x,self.y)
                    offsetx = self.x-self.data["EXPLOSIONSIZE"]//2
                    offsety = self.y-self.data["EXPLOSIONSIZE"]//2
                    for y in range(self.data["EXPLOSIONSIZE"]):
                        for x in range(self.data["EXPLOSIONSIZE"]):
                            cx = offsetx+x
                            cy=offsety+y
                            if cx<pwidth and cy < pheight:
                                if BLOCK.bframe[cx][cy] != 30:
                                    NUKEDBLOCK(cx,cy)
                                    if "EXPLOSION" in  self.properties:
                                        self.properties.remove("EXPLOSION")
        if "TIMED" in self.properties:
            if Tick.checkTick(ctick,self.data["TIME"]):
                self.deleted = True
                EMPTY(*self.pos)
                BLOCK.bframe[self.x][self.y] = 30
                BLOCK.frame[self.x][self.y] = (30,30,30)

        if self.updated:
            self.Update(prevX,prevY)
    @nb.jit
    def returnFrame():

        BLOCK.frame = BLOCK.sframe
        
        for y in range(len(BLOCK.bframe)):
            for x in range(len(BLOCK.bframe[0])):
                # print(y,x)
                if isinstance(BLOCK.bframe[y][x],BLOCK):
                    BLOCK.frame[y][x] = BLOCK.bframe[y][x].color
                else:
                    BLOCK.frame[y][x] = (30,30,30)
        return BLOCK.frame
Sand = lambda x,y:BLOCK((255,250,20),{"modifiers":["GRAVITY","SPREAD"],"data":{"Mass":8,"MAXSPREAD":4}},(x,y))
Water = lambda x,y:BLOCK((0,50,220),{"modifiers":["GRAVITY","LIQUID"],"data":{"Mass":8}},(x,y))    
SOLID = lambda x,y:BLOCK((255,255,255),{"modifiers":["SOLID"],"data":{}},(x,y))    
Mud = lambda x,y:BLOCK((165,50,42),{"modifiers":["GRAVITY","SPREAD"],"data":{"Mass":1, "MAXSPREAD":20,"SMOOTHING":20}},(x,y))    
NUKE = lambda x,y:BLOCK((20,255,42),{"modifiers":["SOLID","GRAVITY","EXPLOSION"],"data":{"Mass":20, "TRIGGER":["COLLISION","GROUND"], "EXPLOSIONSIZE": 20}},(x,y))    
NUKEDBLOCK = lambda x,y:BLOCK((255,30,30),{"modifiers":["TIMED"],"data":{"TIME":50}},(x,y))    
EMPTY = lambda x,y:BLOCK((30,30,30),{"modifiers":["NONE"],"data":{}},(x,y))    

BLOCKCOLS = (255,250,20),(0,50,220),(255,255,255),(165,50,42),(20,255,42)

blocks = [Sand,Water,SOLID,Mud,NUKE]  
currentBlock = 0

Sand(pwidth/2,pheight/2)
spacePressed = False
def ChooseBlock():
    global currentBlock,spacePressed
    
    k = pygame.key.get_pressed()
    if k[pygame.K_SPACE]:
        if not spacePressed:
            currentBlock = currentBlock+1 if len(blocks) > currentBlock+1 else 0
            spacePressed=True
    else:
        spacePressed=False

_brushSize =10
clicked= True
@nb.jit
def draw(brushSize,m,currentBlock):

    if currentBlock != 4:
        for x in range(brushSize):
            sq = ceil(m[0]/(sw/pwidth))+(randint(-x,x) if currentBlock != 2 else 0),ceil(m[1]/(sh/pheight)+(randint(-x*2,x*2) if currentBlock != 2 else 0))

            if sq[0] > 0 and sq[0]+x < pwidth and sq[1]-x*2 > 0 and sq[1]+x*10 < pheight:
                blocks[currentBlock](*sq)



while True:
    matching_blocks=[]
    ctick = pygame.time.get_ticks()
    # print(ctick)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()

    ChooseBlock()
    x=0
    for block in BLOCK._blocks:
        if not block.deleted:
            block.Loop()
        else:
            BLOCK._blocks.pop(x)
        x+=1


    if pygame.mouse.get_pressed()[0]:
        
        mpos = pygame.mouse.get_pos()
        draw(_brushSize,mpos,currentBlock)
        if currentBlock == 4 and not clicked:
             sq = [ceil(mpos[0]/(sw/pwidth)),ceil(mpos[1]/(sh/pheight))]

             if sq[0] > 0 and sq[0] < pwidth and sq[1]> 0 and sq[1] < pheight:
                blocks[currentBlock](*sq)
                clicked=True
    else:
        clicked=False

               

    currentFrame = BLOCK.returnFrame()
    currentFrame[0][0] = BLOCKCOLS[currentBlock]
    matching_blocks = []


    frameSurf = pygame.surfarray.make_surface(currentFrame)
    screen.blit(pygame.transform.scale(frameSurf,ss),[0,0])
    

    pygame.display.set_caption(f"FPS: {pygame.Clock.get_fps(fps)}")
    pygame.display.flip()
    fps.tick(160)