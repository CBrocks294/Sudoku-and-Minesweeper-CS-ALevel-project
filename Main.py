# Following code adapted from GitHub user Lazerwolfegod with Permission
import pygame, math, random, sys, os
from GameClass import GameClass
from UIpygame import PyUI as pyui

pygame.init()
screenw = 1200
screenh = 900
screen = pygame.display.set_mode((screenw, screenh), pygame.RESIZABLE)
pygame.scrap.init()
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
#ui.styleload_soundium()
#ui.styleset(textsize=50)
# End of code adapted from GitHub user Lazerwolfegod with Permission

# Creates the class responsible for all the menus, friends lists and starting up the games
game = GameClass(ui)

# Following Code adapted from GitHub user Lazerwolfegod with Permission

while not done:
    pygameeventget = ui.loadtickdata()
    for event in pygameeventget:
        if event.type == pygame.QUIT:
            done = True
    screen.fill(pyui.Style.wallpapercol)
    game.gameLoop()
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
# End of code adapted from GitHub user Lazerwolfegod with Permission
