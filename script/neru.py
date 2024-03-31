from .entity import *
import random


from script.spark import Spark

# 285, 300, 315, 330, 30, 45, 60, 75
ANGLES = [19*math.pi/12, 5*math.pi/3, 7*math.pi/4, 11*math.pi/6, math.pi/6, math.pi/4, math.pi/3, 5*math.pi/12]

class Neru(PhysicsEntity):
    def __init__(self, gameManager, pos, size, scene):
        super().__init__(gameManager, scene, "neru", pos, size)

        self.name = "Mikamo Neru"
        self.max_hp = 150
        self.hp = 150
        self.active_radius = 10*32

        self.topleft = 0
        self.topright = 0
        self.botleft = 0
        self.botright = 0
        self.room_w = 0
        self.room_h = 0

        self.active = False
        self.invincible = False
        self.teleport = False
        self.volley = False
        self.inAction = False
        self.enrage = False
        self.enrage_attack = False

        self.waitTimer = 35
        self.volley_wait = 0
        self.choice = ""
        self.previous_choice = ""
        self.count = 0
        self.warning_wait = 60

    def update(self, tilemap):
        if self.scene.player.rect().colliderect(self.pos[0] - self.active_radius, self.pos[1] - self.active_radius,
                                                self.active_radius*2, self.active_radius*2) and not self.active:
            self.scene.boss_encounter = True
            self.activate()

        if self.scene.player.rect().colliderect(self.rect()) and not self.scene.player.dashing:
            dis = (self.scene.player.pos[0] - self.pos[0], self.scene.player.pos[1] - self.pos[1])
            if not self.scene.player.invincible_frame:
                self.scene.player.hurting = True
                self.scene.player.hp = max(0, self.scene.player.hp - 2)
                self.scene.player.red_hp = 0
                self.scene.player.invincible_frame = 30
            if dis[0] < 0:
                self.scene.player.velocity[0] = -7
            else:
                self.scene.player.velocity[0] = 7

        if self.collisions['down'] and (self.previous_choice == "volley_right" or self.previous_choice == "volley_left"):
            self.dx = 0

        self.set_action("idle")

        #print("ACTION TIME: ", self.actionTimer)
        #print("WAIT TIME: ", self.waitTimer)
        if self.enrage_attack:
            self.teleport = False
            if self.volley_wait:
                self.volley_wait = max(0, self.volley_wait - 1)
            elif self.warning_wait:
                self.warning_wait = max(0, self.warning_wait - 1)
            else:
                self.raging()

        if self.hp <= self.max_hp / 2 and not self.enrage:
            self.enrage = True
            self.enrage_attack = True
            self.teleport = True
            self.invincible = True
            self.inAction = False
            self.volley = True
            self.count = 0
            self.dx = 0
            self.velocity[1] = 0
            self.waitTimer = 35
            self.pos = [self.topleft[0] + self.room_w / 2, self.topleft[1]]

        if self.active and not self.inAction and not self.enrage_attack:
            self.waitTimer = max(0, self.waitTimer - 1)
            if self.waitTimer == 0:
                #print("PICKING MOVES")
                self.check_position()
                self.inAction = True
                if self.choice == "punch_right":
                    self.punch_right()
                elif self.choice == "volley_left":
                    self.volley_left()
                elif self.choice == "punch_left":
                    self.punch_left()
                elif self.choice == "volley_right":
                    self.volley_right()

                self.waitTimer = 35
        elif self.inAction and not self.enrage_attack:
            if self.choice == "punch_right":
                self.punch_right()
            elif self.choice == "volley_left":
                if self.volley_wait:
                    self.volley_wait = max(0, self.volley_wait - 1)
                else:
                    self.volley_left()
            elif self.choice == "punch_left":
                self.punch_left()
            elif self.choice == "volley_right":
                if self.volley_wait:
                    self.volley_wait = max(0, self.volley_wait - 1)
                else:
                    self.volley_right()

        super().update(tilemap)

    def death(self):
        if self.hp <= 0:
            self.scene.boss_encounter = False
            self.scene.bosses.remove(self)
            self.scene.screenshake = max(16, self.scene.screenshake)
            for i in range(30):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.scene.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                self.scene.particles.append(Particle(self.gameManager, "particle", self.rect().center,
                                                     velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                               math.sin(angle + math.pi) * speed * 0.5],
                                                     frame=random.randint(0, 7)))
            self.scene.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
            self.scene.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))

    def activate(self):
        self.topleft = (self.pos[0] - 10*32, self.pos[1] - (64 - self.size[1]) - 3*32)
        self.topright = (self.pos[0] + 2*32, self.pos[1] - (64 - self.size[1]) - 3*32)
        self.botleft = (self.pos[0] - 10*32, self.pos[1] + self.size[1])
        self.botright = (self.pos[0] + 2*32, self.pos[1] + self.size[1])
        self.room_w = 12*32
        self.room_h = 5*32
        self.active = True

    def EuclideanDistance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def check_position(self):
        if self.EuclideanDistance(self.botleft, self.pos) <= self.EuclideanDistance(self.botright, self.pos):
            if self.previous_choice == "volley_left":
                weight = [0.8, 0.2]
            else:
                weight = [0.4, 0.6]
            self.choice = random.choices(["punch_right", "volley_left"], weight, k=1)[0]
        else:
            if self.previous_choice == "volley_right":
                weight = [0.8, 0.2]
            else:
                weight = [0.4, 0.6]
            self.choice = random.choices(["punch_left", "volley_right"], weight, k=1)[0]
        self.previous_choice = self.choice

    def punch_right(self):
        #print("PUNCH RIGHT")
        if self.EuclideanDistance(self.botright, self.pos) < 3*32:
            self.dx = 0
            self.inAction = False
        else:
            if self.enrage:
                self.dx = 7
            else:
                self.dx = 4

    def punch_left(self):
        #print("PUNCH LEFT")
        if self.EuclideanDistance(self.botleft, self.pos) < 1.5*32:
            self.dx = 0
            self.inAction = False
        else:
            if self.enrage:
                self.dx = -7
            else:
                self.dx = -4

    def volley_left(self):
        #print("VOLLEY LEFT")
        if not self.volley:
            if self.collisions['left']:
                self.dx = 0
                self.velocity[1] = 0
                self.volley = True
                self.count = 0
            else:
                self.dx = -5
                self.velocity[1] = -7
        else:
            dis_x = self.scene.player.pos[0] - self.pos[0]
            dis_y = self.scene.player.pos[1] - self.pos[1]
            dis = math.sqrt(dis_x**2 + dis_y**2)
            nor_dis_x = dis_x / dis * 5
            nor_dis_y = dis_y / dis * 5

            self.scene.projectiles.append(
                [[self.rect().centerx - 4,
                  self.rect().centery - self.gameManager.assets['enemy_bullet'].get_height() / 2 + 12],
                 [nor_dis_x, nor_dis_y], 0, self.gameManager.assets['enemy_bullet'], 2])
            for i in range(4):
                self.scene.sparks.append(Spark(self.scene.projectiles[-1][0],
                                               random.random() - 0.5 + math.pi, 2 + random.random()))
            if self.enrage:
                self.volley_wait = 10
            else:
                self.volley_wait = 20

            self.count += 1
            if self.enrage:
                if self.count == 7:
                    self.inAction = False
                    self.dx = 2
                    self.volley = False
                    self.count = 0
            else:
                if self.count == 5:
                    self.inAction = False
                    self.dx = 2
                    self.volley = False
                    self.count = 0

    def volley_right(self):
        #print("VOLLEY RIGHT")
        if not self.volley:
            if self.collisions['right']:
                self.dx = 0
                self.velocity[1] = 0
                self.volley = True
                self.count = 0
            else:
                self.dx = 5
                self.velocity[1] = -8
        else:
            dis_x = self.scene.player.pos[0] - self.pos[0]
            dis_y = self.scene.player.pos[1] - self.pos[1]
            dis = math.sqrt(dis_x**2 + dis_y**2)
            nor_dis_x = dis_x / dis * 5
            nor_dis_y = dis_y / dis * 5

            self.scene.projectiles.append(
                [[self.rect().centerx - 4,
                  self.rect().centery - self.gameManager.assets['enemy_bullet'].get_height() / 2 + 12],
                 [nor_dis_x, nor_dis_y], 0, self.gameManager.assets['enemy_bullet'], 2])
            for i in range(4):
                self.scene.sparks.append(Spark(self.scene.projectiles[-1][0],
                                               random.random() - 0.5 + math.pi, 2 + random.random()))

            if self.enrage:
                self.volley_wait = 10
            else:
                self.volley_wait = 20

            self.count += 1
            if self.enrage:
                if self.count == 7:
                    self.inAction = False
                    self.dx = -2
                    self.volley = False
                    self.count = 0
            else:
                if self.count == 5:
                    self.inAction = False
                    self.dx = -2
                    self.volley = False
                    self.count = 0

    def raging(self):
        for angle in ANGLES:
            angle_x = math.sin(angle)*5
            angle_y = math.cos(angle)*5
            self.scene.projectiles.append(
                [[self.rect().centerx - 4,
                  self.rect().centery - self.gameManager.assets['enemy_bullet'].get_height() / 2 + 12],
                 [angle_x, angle_y], 0, self.gameManager.assets['enemy_bullet'], 1])

        self.volley_wait = 10

        self.count += 1
        if self.count == 15:
            self.inAction = False
            self.volley = False
            self.count = 0
            self.invincible = False
            self.enrage_attack = False

    def render(self, surf, offset=(0, 0)):
        if not self.teleport:
            super().render(surf, offset)

    def gravity(self):
        if not self.volley:
            super().gravity()