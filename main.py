import threading
import time
import cv2 as cv
import pygame as py
import random
import pygame.freetype
from hand_sign import HandSign
import os
import platform

py.init()
py.font.init()
py.mixer.init()
py.mixer.set_num_channels(8)

detector = HandSign()
current_sign = None
mouse_pointer = None

control_mode = "keyboard"

def toggle_control():
    global control_mode, current_sign
    control_mode = "hand" if control_mode == "keyboard" else "keyboard"
    current_sign = None 

running = True
cam_lock = threading.Lock()
cap = None
CAM_BACKEND = cv.CAP_DSHOW if platform.system() == "Windows" else cv.CAP_ANY

def find_cameras(max_tested=6):
    """Probe camera indexes and return the ones that deliver frames."""
    found = []
    for i in range(max_tested):
        c = cv.VideoCapture(i, CAM_BACKEND)
        if c.isOpened():
            ok, _ = c.read()
            if ok:
                found.append(i)
        c.release()
    return found

def open_camera(index):
    """Switch to a camera. The old one is only released if the new one opens."""
    global cap
    new_cap = cv.VideoCapture(index, CAM_BACKEND)
    if not new_cap.isOpened():
        new_cap.release()
        return False
    with cam_lock:
        if cap is not None:
            cap.release()
        cap = new_cap
    return True

available_cameras = find_cameras()
camera_pos = 0

def next_camera():
    global camera_pos, current_sign
    if len(available_cameras) < 2:
        return
    camera_pos = (camera_pos + 1) % len(available_cameras)
    open_camera(available_cameras[camera_pos])
    current_sign = None

if available_cameras:
    open_camera(available_cameras[0])

def detect_hand_sign():
    global current_sign, mouse_pointer
    while running:
        if control_mode != "hand":
            current_sign = None
            time.sleep(0.1)
            continue
        with cam_lock:
            ret, frame = cap.read() if cap is not None else (False, None)
        if not ret:
            current_sign = None
            time.sleep(0.05)
            continue
        try:
            frame = cv.flip(cv.resize(frame, (640, 480)), 1)
            result = detector.recognition(frame)
            current_sign = detector.play_sign(result)
            mouse_pointer = detector.mouse_pointer(result)
        except Exception as e:
            print("hand thread error:", e)
        time.sleep(0.05)

thread = threading.Thread(target=detect_hand_sign, daemon=True)
thread.start()

cam_font = py.font.SysFont(None, 32)
 
#Assign channels
bg_channel = py.mixer.Channel(0)
sfx_channel = py.mixer.Channel(1)
collision_channel = py.mixer.Channel(2)
user_channel = py.mixer.Channel(3)

bg_channel.set_volume(0.5)



os.environ["SDL_VIDEO_CENTERED"] = "1"
os.environ["SDL_RENDER_SCALE_QUALITY"] = "nearest"
screen_width = 1280
screen_height = 720
screen = py.display.set_mode((screen_width,screen_height),py.SCALED | py.RESIZABLE)

py.display.set_caption("Dutugamunu")
py.display.set_icon(py.image.load("assets/Images/game/game logo.png"))

#create a timer
timer = py.time.Clock()

FONT = pygame.freetype.Font("assets/fonts/iskoola-pota.ttf", 40)  # once, near the top

#load backgrounds
bg_1 = py.transform.scale(py.image.load("assets/Images/background/bg 1.png"), (screen_width, screen_height))
bg_2 = py.transform.scale(py.image.load("assets/Images/background/bg 2.png"), (screen_width, screen_height))

#load screen Images
start_screen = py.transform.scale(py.image.load("assets/Images/screens/start_screen.png"), (screen_width, screen_height))
game_over_screen = py.transform.scale(py.image.load("assets/Images/screens/game_over.png"), (screen_width, screen_height))
level_pass_screen = py.transform.scale(py.image.load("assets/Images/screens/level_passed.png"), (screen_width, screen_height))
victory_screen = py.transform.scale(py.image.load("assets/Images/screens/victory_screen.png"), (screen_width, screen_height))

#load buttons
start_btn = py.image.load("assets/Images/Buttons/start.png")
start_rect = start_btn.get_rect(topleft=((screen_width//2-start_btn.get_width()//2),425))
retry_btn = py.image.load("assets/Images/Buttons/retry.png")
retry_rect = retry_btn.get_rect(topleft=((screen_width//2-(retry_btn.get_width()+25)),590))
next_btn = py.image.load("assets/Images/Buttons/next.png")
next_rect = next_btn.get_rect(topleft=((screen_width//2-next_btn.get_width()//2),590))
exit_btn = py.image.load("assets/Images/Buttons/exit.png")
exit_rect = exit_btn.get_rect(topleft=((screen_width//2-exit_btn.get_width()//2),550))
retry_exit_rect = exit_btn.get_rect(topleft=((screen_width//2)+25,590))
victory_exit_rect = exit_btn.get_rect(topleft=((screen_width//2-exit_btn.get_width()//2),590))

#load castles
castle_1 = py.transform.scale(py.image.load("assets/Images/obstac_items/castle_1.png"), (600, 450))
castle_2 = py.transform.scale(py.image.load("assets/Images/obstac_items/castle_2.png"), (600, 450))

#load flags
sri_lanka_flag = py.transform.scale(py.image.load("assets/Images/obstac_items/sri_lanka.png"), (250, 350))
enemy_flag = py.transform.rotate(py.transform.scale(py.image.load("assets/Images/obstac_items/enemy.png"), (150, 350)), -12)

#load character's frames
    #load gamunu
gamunu = py.image.load("assets/Images/characters/gamunu/g2.png")
g_walk = [py.image.load("assets/Images/characters/gamunu/g1.png"), py.image.load(
    "assets/Images/characters/gamunu/g2.png"),
          py.image.load("assets/Images/characters/gamunu/g3.png")]
g_fight = [py.image.load("assets/Images/characters/gamunu/g2.png"), py.image.load(
    "assets/Images/characters/gamunu/g4.png"),
           py.image.load("assets/Images/characters/gamunu/g5.png")]

    #load soldier
soldier = py.image.load("assets/Images/characters/soilder/s1.png")
s_fight = [py.image.load("assets/Images/characters/soilder/s1.png"), py.image.load(
    "assets/Images/characters/soilder/s2.png"),
           py.image.load("assets/Images/characters/soilder/s3.png")]

    #load elara
elara = py.transform.flip(py.image.load("assets/Images/characters/elara/e1.png"), True, False)
e_fight = [py.transform.flip(py.image.load("assets/Images/characters/elara/e1.png"), True, False),
           py.transform.flip(py.image.load("assets/Images/characters/elara/e2.png"), True, False),
           py.transform.flip(py.image.load("assets/Images/characters/elara/e3.png"), True, False)]

#load obstacles
stone = py.image.load("assets/Images/obstac_items/stone.png")
fire = py.image.load("assets/Images/obstac_items/fire.png")
rice_pot = py.image.load("assets/Images/obstac_items/rice_pot.png")
thunder = py.image.load("assets/Images/obstac_items/thunder.png")

heart = py.transform.scale(py.image.load("assets/Images/game/health.png"), (50, 50))
arrow = py.transform.flip(py.transform.rotate(py.transform.scale(py.image.load("assets/Images/game/arrow.png"), (160, 80)), 150), 0, 1)
speed = py.transform.scale(thunder,(30,50))

pointer = py.image.load("assets/Images/game/cursor.png")
pointer_rect = pointer.get_rect()

#load audio
bg = py.mixer.Sound("assets/audio/background.wav")
click = py.mixer.Sound("assets/audio/click.mp3")
fight = py.mixer.Sound("assets/audio/fight.wav")
walk = py.mixer.Sound("assets/audio/walk.wav")
jump = py.mixer.Sound("assets/audio/jump.wav")
stone_collision = py.mixer.Sound("assets/audio/stone.wav")
improve_speed = py.mixer.Sound("assets/audio/speed.wav")
game_over = py.mixer.Sound("assets/audio/game_over.wav")
level_pass = py.mixer.Sound("assets/audio/level_complete.wav")
victory = py.mixer.Sound("assets/audio/victory.wav")
improve_health = py.mixer.Sound("assets/audio/health.wav")
fire_collision = py.mixer.Sound("assets/audio/fire.mp3")
burn = py.mixer.Sound("assets/audio/burning.wav")


#load colors
red = (255,0,0)
orange = (255,165,0)
yellow = (255,255,0)
light_yellow = (255,222,52)
green = (0,255,0)
grey = (128,128,128)

#play background music
bg_channel.play(bg,-1,fade_ms=2000)


#Main Class
class Game:
    def __init__(self):
        self.screen = True
        self.in_game = False
        self.on_game = True
        self.g_over = False
        self.lev_pass = False
        self.victory = False
        self.last_sign = None
        self.ctrl_rect = py.Rect(0, 0, 0, 0)
        self.cam_rect = py.Rect(0, 0, 0, 0)
        self.sign_count = 0
        self.scroll = 0
        self.scr_increment = 3
        self.current_time = py.time.get_ticks() // 1000
        self.collision_time = 0
        self.time_quantum = 5
        self.castles = [{"name":"මාගම බලෙකාටුව","type":castle_2,"rect":castle_2.get_rect(topleft=(0,260)),"flag":sri_lanka_flag},
                        {"name":"මහියංගණය බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(10000,285)),"flag":enemy_flag},
                        {"name":"දීඝවාපිය බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(20000,285)),"flag":enemy_flag},
                        {"name":"මලය බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(30000,285)),"flag":enemy_flag},
                        {"name":"ෙකාටෙවෙහර බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(40000,285)),"flag":enemy_flag},
                        {"name":"ෙකාස්ගම බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(50000,285)),"flag":enemy_flag},
                        {"name":"විජිතපුර බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(60000,285)),"flag":enemy_flag},
                        {"name":"ගිරිකන්දක බලෙකාටුව","type":castle_1,"rect":castle_1.get_rect(topleft=(70000,285)),"flag":enemy_flag},
                        {"name":"අනුරාධපුර බලෙකාටුව","type":castle_2,"rect":castle_2.get_rect(topleft=(80000,260)),"flag":enemy_flag}]
        self.close_castle = 10000
        self.last_castle = 0
        self.direction = True
        #self.flag = enemy_flag
        self.last_distance = []
        self.close_distance = []
        self.player = Player(self.scr_increment)
        self.obstacle = Obstacle(self.scr_increment)

    def draw_control_button(self):
        if control_mode == "hand":
            label = "Control: HAND  [H]"
            bg_color, hover_color = (40, 140, 70), (60, 180, 95)      # green
        else:
            label = "Control: KEYBOARD  [H]"
            bg_color, hover_color = (225, 155, 44), (255, 160, 60)     # orange

        text = cam_font.render(label, True, (0, 0, 0))
        self.ctrl_rect = text.get_rect(topleft=(30, 85)).inflate(24, 16)

        hovering = self.ctrl_rect.collidepoint(py.mouse.get_pos())
        py.draw.rect(screen, hover_color if hovering else bg_color, self.ctrl_rect, border_radius=8)
        py.draw.rect(screen, (0, 0, 0), self.ctrl_rect, 2, border_radius=8)
        screen.blit(text, text.get_rect(center=self.ctrl_rect.center))

    def draw_control_hud(self):
        """Small indicator during gameplay."""
        if control_mode == "hand":
            label = "HAND"
            bg_color = (40, 140, 70)
        else:
            label = "KEYBOARD"
            bg_color = (225, 155, 44)
        label = "HAND" if control_mode == "hand" else "KEYBOARD"
        text = cam_font.render(f"{label}  ( 'h' to switch )", True, (0, 0, 0))
        box = text.get_rect(topright=(screen_width - 50, 45)).inflate(25, 16)
        py.draw.rect(screen, bg_color, box, border_radius=8)
        screen.blit(text, text.get_rect(center=box.center))
    
    def draw_camera_button(self):
        if available_cameras:
            label = f"Camera {available_cameras[camera_pos]}  ({camera_pos+1}/{len(available_cameras)})  [C]"
        else:
            label = "No camera found"
        text = cam_font.render(label, True, (0, 0, 0))
        self.cam_rect = text.get_rect(topleft=(30, 30)).inflate(24, 16)
        py.draw.rect(screen, (225, 155, 44), self.cam_rect, border_radius=8)
        py.draw.rect(screen, (0, 0, 0), self.cam_rect, 2, border_radius=8)
        screen.blit(text, text.get_rect(center=self.cam_rect.center))

    def mouse(self):
        py.mouse.set_visible(False)
        pointer_rect.center = py.mouse.get_pos()
        screen.blit(pointer, pointer_rect)

    def held_sign(self, frames=15):
        """Returns a sign only after it has been held for `frames` loop iterations."""
        if current_sign is not None and current_sign == self.last_sign:
            self.sign_count += 1
        else:
            self.sign_count = 0
        self.last_sign = current_sign
        return current_sign if self.sign_count >= frames else None

    def start_screen(self):
        while self.on_game:
            screen.blit(start_screen, (0,0))
            screen.blit(start_btn, start_rect)
            screen.blit(exit_btn, exit_rect)
            self.draw_camera_button()
            self.draw_control_button()
            self.mouse()

            for event in py.event.get():
                if event.type == py.QUIT:
                    self.on_game = False
                    self.screen = False
                if event.type == py.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if start_rect.collidepoint(pos):
                        sfx_channel.play(click)
                        self.on_game = False
                        self.in_game = True
                    if exit_rect.collidepoint(pos):
                        self.on_game = False
                        self.screen = False
                if event.type == py.KEYDOWN and event.key == py.K_c:
                    next_camera()
                if event.type == py.MOUSEBUTTONDOWN and self.cam_rect.collidepoint(event.pos):
                    sfx_channel.play(click)
                    next_camera()
                if event.type == py.KEYDOWN and event.key == py.K_h:
                    toggle_control()
                if event.type == py.MOUSEBUTTONDOWN and self.ctrl_rect.collidepoint(event.pos):
                    sfx_channel.play(click)
                    toggle_control()
            sign = self.held_sign()
            if sign == 'start':
                sfx_channel.play(click)
                self.on_game = False
                self.in_game = True
            elif sign == 'exit':
                self.on_game = False
                self.screen = False
            py.display.flip()
    
    def game_screen(self):
        while self.in_game:
            self.obstacle.spawn(random.choice([rice_pot, thunder, stone, fire, soldier]))
            self.current_time = py.time.get_ticks() // 1000
            if self.scroll <= -screen_width:
                self.scroll = 0
            for event in py.event.get():
                if event.type == py.QUIT:
                    self.in_game = False
                    self.screen = False
                if event.type == py.KEYDOWN and event.key == py.K_h:
                    toggle_control()
                if event.type == py.KEYDOWN and event.key == py.K_c:
                    next_camera()
                if event.type == py.MOUSEBUTTONDOWN and self.cam_rect.collidepoint(event.pos):
                    sfx_channel.play(click)
                    next_camera()
            sign = self.held_sign()
            if sign == 'exit':
                self.in_game = False
                self.screen = False
            screen.blit(bg_1,(0+self.scroll,0))
            screen.blit(bg_1,(screen_width+self.scroll,0))
            self.build_castle()
            self.obstacle.draw()
            self.player.draw()
            self.collision_detection()
            self.display_health()
            self.display_direction()
            self.draw_control_hud()
            self.frame_rate()
            screen.blit(bg_2,(0+self.scroll,0))
            screen.blit(bg_2,(screen_width+self.scroll,0))
            if self.player.walk and self.player.player_rect.x >= screen_width//3:
                self.scroll -= self.scr_increment #scrolling background

            if self.player.health <= 0:
                sfx_channel.play(game_over)
                self.in_game = False
                self.g_over = True

            py.display.flip()

    def game_over_screen(self):
        while self.g_over:
            screen.blit(game_over_screen,(0,0))
            screen.blit(retry_btn,retry_rect)
            screen.blit(exit_btn,retry_exit_rect)

            self.mouse()

            for event in py.event.get():
                if event.type == py.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if retry_rect.collidepoint(pos):
                        self.game_restart()
                    if retry_exit_rect.collidepoint(pos):
                        self.g_over = False
                        self.screen = False
                if event.type == py.QUIT:
                    self.g_over = False
                    self.screen = False
            sign = self.held_sign()
            if sign == 'start':
                self.game_restart()
            if sign == 'exit':
                self.g_over = False
                self.screen = False
            py.display.flip()

    def game_restart(self):
        sfx_channel.play(click)
        for castle in self.castles:
            castle["rect"].x -= self.last_castle
        self.obstacle.e_rect.x -= self.last_castle
        for obs in self.obstacle.obstacles:
            if self.player.player_rect.colliderect(obs["rect"]):
                self.obstacle.remove_obstacle(obs["rect"])
        self.player.health = 100
        self.player.eh_count = 100
        self.player.speed = False
        self.scr_increment = 3
        self.obstacle.scr_increment = 3
        self.player.gravity = 0.08
        self.player.player_rect.y = 460
        self.player.fight = False
        self.obstacle.fight = False
        self.player.bounce = False
        self.obstacle.e_live = True
        self.in_game = True
        self.g_over = False

    def level_pass_screen(self):
        while self.lev_pass:
            screen.blit(level_pass_screen,(0,0))
            screen.blit(next_btn,next_rect)

            self.mouse()

            for event in py.event.get():
                if event.type == py.QUIT:
                    self.lev_pass = False
                    self.screen = False
                if event.type == py.MOUSEBUTTONDOWN:
                    if next_rect.collidepoint(event.pos):
                        self.next_level()
            sign = self.held_sign()
            if sign == 'start':
                self.next_level()
            py.display.flip()

    def next_level(self):
        sfx_channel.play(click)
        if self.player.health < 100:
            self.player.health = 100
        self.player.speed = False
        self.scr_increment = 3
        self.obstacle.scr_increment = 3
        self.player.gravity = 0.08
        self.player.player_rect.y = 460
        self.player.fight = False
        self.player.bounce = False
        self.lev_pass = False
        self.in_game = True

    def victory_screen(self):
        while self.victory:
            screen.blit(victory_screen,(0,0))
            screen.blit(exit_btn,victory_exit_rect)

            self.mouse()

            for event in py.event.get():
                if event.type == py.MOUSEBUTTONDOWN:
                    sfx_channel.play(click)
                    if victory_exit_rect.collidepoint(event.pos):
                        self.victory = False
                        self.screen = False
                if event.type == py.QUIT:
                    self.victory = False
                    self.screen = False
            sign = self.held_sign()
            if sign == 'exit':
                self.victory = False
                self.screen = False
            py.display.flip()

    def build_castle(self):
        castle_distance = []
        for castle in self.castles:
            if self.player.walk and self.player.player_rect.x >= screen_width//3:
                castle["rect"].x -= self.scr_increment
            screen.blit(castle["type"], castle["rect"])
            castle["f_rect"] = castle["flag"].get_rect(
            topleft=(castle["rect"].centerx - castle["flag"].get_width() // 2,
                    castle["rect"].bottom - castle["flag"].get_height()))
            screen.blit(castle["flag"],castle["f_rect"])
            self.display_text("castle",castle["name"],(255,255,255),(castle["rect"]))
            castle_distance.append(castle["rect"].centerx - self.player.player_rect.x)
        self.last_distance = [x for x in castle_distance if x <= 0]
        self.close_distance = [x for x in castle_distance if x >= 0]
        if len(self.last_distance) == 1:
            self.last_castle = self.last_distance[0]
        else:
            self.last_castle = max(self.last_distance)
        self.close_castle = min(self.close_distance)

    def collision_detection(self):
        for obs in self.obstacle.obstacles:
            offset_x = self.player.player_rect.x - obs["rect"].x
            offset_y = self.player.player_rect.y - obs["rect"].y
            if obs["mask"].overlap(self.player.player_mask,(offset_x,offset_y)):
                if obs["type"] == stone:
                    collision_channel.play(stone_collision)
                    self.player.health_update(stone)
                    self.player.player_rect.x -= 50
                    self.player.walk = False
                if obs["type"] == fire:
                    if not sfx_channel.get_busy() and not collision_channel.get_busy():
                        sfx_channel.play(fire_collision)
                        collision_channel.play(burn)
                    self.player.health_update(fire)
                if obs["type"] == soldier:
                    if not collision_channel.get_busy():
                        collision_channel.play(fight)
                    self.player.y_pos = 460
                    self.player.fight = True
                    self.obstacle.fight = True

                    self.player.health_update(soldier)
                    if self.player.sh_count == 0:
                        self.player.fight = False
                        self.obstacle.fight = False
                        self.obstacle.remove_obstacle(obs["rect"])
                        self.player.sh_count = 10
                else:
                    self.player.fight = False
                    self.obstacle.fight = False

                if obs["type"] == rice_pot:
                    sfx_channel.play(improve_health)
                    self.player.health_update(rice_pot)
                    self.obstacle.remove_obstacle(obs["rect"])
                if obs["type"] == thunder:
                    sfx_channel.play(improve_speed)
                    self.player.speed = True
                    self.collision_time = self.current_time
                    self.obstacle.remove_obstacle(obs["rect"])



        if self.obstacle.e_live:
            off_x = self.player.player_rect.x - self.obstacle.e_rect.x
            off_y = self.player.player_rect.y - self.obstacle.e_rect.y
            if py.mask.from_surface(elara).overlap(self.player.player_mask,(off_x,off_y)):
                if not collision_channel.get_busy():
                    collision_channel.play(fight)
                self.player.fight = True
                self.obstacle.fight = True
                self.player.health_update(elara)
                if self.player.eh_count == 0:
                    self.player.fight = False
                    self.obstacle.fight = False
                    self.obstacle.e_live = False
                    self.player.eh_count = 100


        for castle in self.castles:
            if castle["flag"] == enemy_flag:
                if self.player.player_rect.colliderect(castle["f_rect"]):
                    if not castle["name"] == "අනුරාධපුර බලෙකාටුව":
                        sfx_channel.play(level_pass)
                        self.in_game = False
                        self.lev_pass = True
                        castle["flag"] = sri_lanka_flag
                        castle["rect"].x -= sri_lanka_flag.get_width()
                    else:
                        sfx_channel.play(victory)
                        self.in_game = False
                        self.victory = True
            for obs in self.obstacle.obstacles:
                if obs["rect"].colliderect(castle["rect"]):
                    self.obstacle.remove_obstacle(obs["rect"])


        for castle in self.castles:
            if castle["rect"].colliderect(self.player.player_rect):
                self.direction = False
                break
            else:
                self.direction = True

    def display_health(self):
        if self.player.health >= 85:
            color = red
        elif self.player.health >= 60:
            color = orange
        elif self.player.health >= 35:
            color = yellow
        else:
            color = grey

        screen.blit(self.color_change(heart,color),(50,36))
        self.display_text("health",str(self.player.health),color,heart.get_rect())

    def display_direction(self):
        if self.close_castle >= 7000:
            color = red
        elif self.close_castle >= 4000:
            color = light_yellow
        else:
            color = green
        if self.direction:
            screen.blit(self.color_change(arrow,color),(self.player.player_rect.x-20,self.player.player_rect.y-100))

    def display_text(self,choice,text,color,rect):
        font = py.freetype.Font("assets/fonts/iskoola-pota.ttf", 40)
        text_surface,text_rect = font.render(text,color)
        if choice == "castle":
            screen.blit(text_surface,(rect.centerx-text_rect.centerx,rect.y-text_rect.height-10))
        if choice == "health":
            screen.blit(text_surface,(60+rect.width,50))
        if choice == "speed":
            screen.blit(text_surface,(250,50))

    def color_change(self,image,color):
        tint_img = image.copy()
        tint_img.fill(color,special_flags=py.BLEND_RGBA_MULT)
        return tint_img

    def frame_rate(self):
        if self.player.speed:
            self.scr_increment = 6
            self.obstacle.scr_increment = 6
            self.player.gravity = 0.04
            final_time = self.collision_time + self.time_quantum
            display_time = final_time - self.current_time
            if final_time == self.current_time:
                self.player.speed = False
                self.scr_increment = 3
                self.obstacle.scr_increment = 3
                self.player.gravity = 0.08
            screen.blit(speed,(210,36))
            self.display_text("speed",str(display_time),(255,255,0),speed.get_rect())



#Player Class
class Player:
    def __init__(self,increment):
        self.scr_increment = increment
        self.x_pos = castle_2.get_width()//2
        self.y_pos = 460
        self.frames = g_walk
        self.walk = False
        self.bounce = False
        self.fight = False
        self.velocity = 5
        self.gravity = 0.08
        self.health = 100
        self.sh_count = 10
        self.eh_count = 100
        self.speed = False
        self.player_rect = gamunu.get_rect(topleft=(self.x_pos,self.y_pos))
        self.player_mask = py.mask.from_surface(self.frame_update())

    def draw(self):
        screen.blit(self.frame_update(), self.player_rect)

    def frame_update(self):
        self.pos_update()
        frame = gamunu
        if self.walk or self.fight:
            if self.walk and not self.fight:
                if not user_channel.get_busy():
                    user_channel.play(walk)
                self.frames = g_walk
            elif self.fight and not self.walk:
                self.frames = g_fight
            elif self.fight and self.walk:
                self.walk = False
                self.frames = g_fight
            if not self.bounce:
                frame = self.frames.pop(0)
                self.frames.append(frame)
            else:
                frame = self.frames[1]
        timer.tick(50)
        return frame

    def pos_update(self):
        key = py.key.get_pressed()

        if control_mode == "keyboard":
            want_walk = key[py.K_RIGHT]
            want_jump = key[py.K_SPACE]
        else:
            want_walk = current_sign in ('walk', 'walk_jump')
            want_jump = current_sign in ('jump', 'walk_jump')

        if want_walk:
            self.walk = True
            if self.player_rect.x < screen_width//3:
                self.player_rect.x += self.scr_increment
        else:
            self.walk = False
            user_channel.stop()

        if want_jump:
            self.bounce = True
        self.jump()

    def jump(self):
        if not self.bounce:
            return
        if self.velocity == 5:
            sfx_channel.play(jump)
        user_channel.pause()
        
        self.y_pos -= self.velocity
        self.velocity -= self.gravity
        if self.y_pos >= 460:
            self.y_pos = 460
            self.bounce = False
            user_channel.play(walk)
            self.velocity = 5
        self.player_rect.y = round(self.y_pos)

    def health_update(self,obs):
        if obs == stone:
            self.health -= 5
        if obs == fire:
            self.health -= 1
        if obs == soldier:
            self.health -= 1
            self.sh_count -= 1
        if obs == rice_pot:
            self.health += 20
        if obs == elara:
            self.health -= 1
            self.eh_count -= 1



#Obstacle Class
class Obstacle:
    def __init__(self,increment):
        self.scr_increment = increment
        self.obstacles = []
        self.gap = 600
        self.fight = False
        self.e_live = True
        self.e_rect = elara.get_rect(topleft=(79500,460))
        self.frames = s_fight

        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1500  # in milliseconds

    def spawn(self, choice):
        if len(self.obstacles) >= 3:
            return

        # Prevent same type as previous
        attempts = 0
        while self.obstacles and self.obstacles[-1]["type"] == choice and attempts < 5:
            choice = random.choice([rice_pot, thunder, stone, fire, soldier])
            attempts += 1

        # Determine spawn x position
        if not self.obstacles:
            x_pos = screen_width + 100
        else:
            last_obs = self.obstacles[-1]
            x_pos = last_obs["rect"].right + self.gap

            # Extra check to avoid overlap
            if x_pos - last_obs["rect"].right < self.gap:
                return

        # Set y position based on obstacle type
        if choice == stone:
            y_pos = 595
        elif choice == fire:
            y_pos = 560
        elif choice == rice_pot:
            y_pos = 580
        elif choice == castle_1:
            y_pos = 25
        elif choice == soldier:
            y_pos = 460
        else:
            y_pos = 550

        # Add obstacle
        self.obstacles.append({
                "type": choice,
                "rect": choice.get_rect(topleft=(x_pos, y_pos)),
                "mask": py.mask.from_surface(choice)
            })

    def draw(self):
        current_time = pygame.time.get_ticks()

        for obs in self.obstacles:
            frame = obs["type"]

            # Scroll obstacle if player moves
            if game.player.walk and game.player.player_rect.x >= screen_width // 3:
                obs["rect"].x -= self.scr_increment

            # Animate soldier
            if frame == soldier:
                self.frames = s_fight
                if self.fight:
                    frame = self.frames.pop(0)
                    self.frames.append(frame)
                    timer.tick(50)

            screen.blit(frame, obs["rect"])

        if self.e_live:
            frame = elara
            if self.fight:
                timer.tick(50)
                self.frames = e_fight
                frame = self.frames.pop(0)
                self.frames.append(frame)

            if game.player.walk:
                self.e_rect.x -= game.scr_increment
            screen.blit(frame, self.e_rect)

        # Remove off-screen obstacles or ones too far behind
        self.obstacles = [
            obs for obs in self.obstacles
            if obs["rect"].right > 0
            ]

        # Spawn new obstacle only after delay
        if len(self.obstacles) < 3 and current_time - self.last_spawn_time > self.spawn_delay:
            self.spawn(random.choice([rice_pot, thunder, stone, fire, soldier]))
            self.last_spawn_time = current_time

    def remove_obstacle(self,obs_rect):
        self.obstacles = [obs for obs in self.obstacles if obs["rect"] != obs_rect]


#Game Loop
game = Game()
run = game.screen
while run:
    game.start_screen()
    game.game_screen()
    game.game_over_screen()
    game.level_pass_screen()
    game.victory_screen()
    run = game.screen

running = False
thread.join(timeout=1)
cap.release()
detector.close()
py.quit()
