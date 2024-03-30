import pygame
import json
from buttonRect import Button

class MainMenu:
    def __init__(self, gameManager):
        self.gameManager = gameManager
        self.screen = self.gameManager.screen
        self.clock = self.gameManager.clock
        self.playButton = Button("NEW GAME", (self.gameManager.SCREENWIDTH / 2 - 103, 460), (206, 40), 0, 0,
                                 [255, 210, 159], [100, 0, 35],
                                 self.gameManager.fonts['title'], [229,64,64], [184, 0, 64], [229,148,57])
        self.continueButton = Button("CONTINUE", (self.gameManager.SCREENWIDTH / 2 - 105, 520), (210, 40), 0, 0,
                                     [255, 210, 159], [100, 0, 35],
                                     self.gameManager.fonts['title'], [229,64,64], [184, 0, 64], [229,148,57])
        self.greyContinueButton = Button("CONTINUE", (self.gameManager.SCREENWIDTH / 2 - 105, 520), (210, 40), 0, 0,
                                         [200, 200, 200], [0,0,0],
                                         self.gameManager.fonts['title'], border=[0, 0, 0])

        try:
            with open('save/data.json', "r") as file:
                self.gameManager.data = json.load(file)
            self.saveFound = True
        except FileNotFoundError:
            self.saveFound = False

    def run(self):
        self.screen.blit(self.gameManager.menuAssets["menu_bg"], (0, 0))

        self.playButton.render(self.screen)
        if self.saveFound:
            self.continueButton.render(self.screen)
        else:
            self.greyContinueButton.render(self.screen)

        if self.playButton.update():
            self.gameManager.data = {
                "level": 0,
                "id": 0,
            }
            self.gameManager.changeState("main_game")

        if self.saveFound and self.continueButton.update():
            self.gameManager.changeState("main_game")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameManager.isRunning = False