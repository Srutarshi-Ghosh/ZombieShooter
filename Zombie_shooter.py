from Tile_settings import *
from Tile_sprites import *
import sys
import os
import pygame


class Game:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(500, 100)
        self.running = True
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pygame.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def explosion_size_adjust(self, sprite, size, frame=0):
        for i in range(frame, len(self.explosion_images[sprite])):
            self.explosion_images[sprite][i] = pygame.transform.scale(self.explosion_images[sprite][i], (size, size))

    def render_fog(self):
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pygame.BLEND_MULT)


    def load_data(self):

        if getattr(sys, 'frozen', False):
            game_folder = sys._MEIPASS
        else:
            game_folder = os.path.dirname(__file__)

        img_folder = os.path.join(game_folder, 'Tile_img')
        snd_folder = os.path.join(os.path.join(game_folder, 'Tile_Sounds'), 'snd')
        music_folder = os.path.join(os.path.join(game_folder, 'Tile_Sounds'), 'music')

        self.img_folder = img_folder

        self.title_font = os.path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = os.path.join(img_folder, 'Impacted2.0.ttf')

        self.dim_screen = pygame.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        self.player_images = {i: pygame.image.load(os.path.join(img_folder, WEAPONS[i]['player_image'])).convert_alpha() for i in WEAPONS}
        self.mob_img = pygame.image.load(os.path.join(img_folder, MOB_IMG)).convert_alpha()
        self.spawner_img = pygame.transform.scale(pygame.image.load(os.path.join(img_folder, SPAWNER_IMG)).convert_alpha(), (90, 90))
        self.splat_img = pygame.image.load(os.path.join(img_folder, SPLAT_IMG)).convert_alpha()
        self.splat_img = pygame.transform.scale(self.splat_img, (TILESIZE, TILESIZE))

        self.bullet_images = {'lg': pygame.transform.scale(pygame.image.load(os.path.join(img_folder, BULLET_IMG)).convert_alpha(), (15, 15)),
                              'sm': pygame.transform.scale(pygame.image.load(os.path.join(img_folder, BULLET_IMG)).convert_alpha(), (10, 10))}
        self.mine_img = pygame.image.load(os.path.join(img_folder, MINE_IMG)).convert_alpha()


        self.gun_flashes = [pygame.image.load(os.path.join(img_folder, img)).convert_alpha() for img in NUZZLE_FLASHES]

        self.item_images = {item: pygame.image.load(os.path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
                            for item in ITEM_IMAGES}

        self.explosion_images = {sprite: [pygame.image.load(os.path.join(img_folder, img)).convert_alpha()
                                          for img in EXPLOSION_ANIMATION[sprite]['explosion_image']]
                                 for sprite in EXPLOSION_ANIMATION}

        self.explosion_size_adjust('mine', EXPLOSION_ANIMATION['mine']['explosion_range'], frame=2)
        self.explosion_size_adjust('spawner', EXPLOSION_ANIMATION['spawner']['explosion_range'])


        self.fog = pygame.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pygame.image.load(os.path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pygame.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        pygame.mixer.music.load(os.path.join(music_folder, BG_MUSIC))

        self.effects_sounds = {type: pygame.mixer.Sound(os.path.join(snd_folder, EFFECTS_SOUNDS[type]))
                               for type in EFFECTS_SOUNDS}

        self.explosion_sounds = {type: [pygame.mixer.Sound(os.path.join(snd_folder, snd)) for snd in EXPLOSION_SOUNDS[type]]
                                 for type in EXPLOSION_SOUNDS}

        self.weapon_sounds = {weapon: [pygame.mixer.Sound(os.path.join(snd_folder, snd))for snd in WEAPON_SOUNDS[weapon]]
                              for weapon in WEAPON_SOUNDS}

        self.zombie_sounds = {}
        self.zombie_sounds['zombie_moan_sounds'] = [pygame.mixer.Sound(os.path.join(snd_folder, snd))
                                                    for snd in ZOMBIE_MOAN_SOUNDS]
        self.zombie_sounds['zombie_hit_sounds'] = [pygame.mixer.Sound(os.path.join(snd_folder, snd))
                                                    for snd in ZOMBIE_HIT_SOUNDS]

        self.player_hit_sounds = [pygame.mixer.Sound(os.path.join(snd_folder, snd)) for snd in PLAYER_HIT_SOUNDS]

    def new(self):

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.walls = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.mines = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        self.map = Tiledmap(os.path.join(self.img_folder, 'Test_level.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        self.set_time = PLAY_TIME
        self.timer = pygame.time.get_ticks()

        self.score = 0

        for tile_object in self.map.tmxdata.objects:
            object_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'Player':
                self.player = Player(self, object_center.x, object_center.y)
                self.all_sprites.add(self.player)

            if tile_object.name == 'Wall':
                Wall(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)

            if tile_object.name == 'Zombie':
                Mob(self, object_center.x, object_center.y)

            if tile_object.name == 'Spawner':
                Spawner(self, object_center.x, object_center.y)

            if tile_object.name in self.item_images.keys():
                Item(self, object_center, tile_object.name)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
        self.paused = False
        self.night = False
        self.run()

    def run(self):

        self.playing = True
        pygame.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.clock.tick(FPS)
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw(self):
        #pygame.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                draw_health(sprite, MOB_HEALTH)

            if isinstance(sprite, Spawner):
                sprite.image = self.spawner_img
                draw_health(sprite, SPAWNER_HEALTH)

            self.screen.blit(sprite.image, self.camera.apply(sprite))


        if self.night:
            self.render_fog()

        self.player.draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)

        if self.set_time <= 30 and self.set_time > 20:
            self.draw_text("NIGHT MODE IN {}".format(self.set_time - 20), self.hud_font, 20, GREEN, WIDTH // 2, 46, align="center")

        self.draw_text("ENEMIES KILLED: {}".format(self.score), self.hud_font, 30, WHITE, WIDTH - 10, 10, align="ne")
        self.draw_text("TIME: {}".format(self.set_time), self.hud_font, 20, GREEN, WIDTH // 2, 26, align="center")
        self.draw_text("Weapon:  {}".format(self.player.weapon), self.hud_font, 10, WHITE, 120, 10, align="nw")

        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("PAUSED", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")
        pygame.display.flip()

    def events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()

                if event.key == pygame.K_p:
                    self.paused = not self.paused

                # if event.key == pygame.K_n:
                #     self.night = not self.night

                if event.key == pygame.K_g:
                    self.player.change_weapon()


    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

        if len(self.mobs) == 0 or not self.set_time:
            self.playing = False

        now = pygame.time.get_ticks()
        if now  - self.timer > 1000:
            self.set_time -= 1
            self.timer = now
            if self.set_time == 20:
                self.night = True

        hits = pygame.sprite.spritecollide(self.player, self.items, False, collide_hit_rect)
        for hit in hits:
            if hit.type == 'Health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.player.add_health(HEALTH_AMOUNT)
                self.effects_sounds['health_up'].play()

            if hit.type == 'Shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon_list.append('shotgun')
                self.weapon = 'shotgun'

            if hit.type == 'Mine':
                hit.kill()
                self.effects_sounds['mine_pickup'].play()
                if 'mines' not in self.player.weapon_list:
                    self.player.weapon_list.append('mines')
                self.player.mines += 1

        hits = pygame.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            random.choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False

        if hits and isinstance(hits[0], Mob):
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        elif hits and isinstance(hits[0], Spawner):
            self.player.hit()
            self.player.pos -= vec(SPAWNER_KNOCKBACK, 0).rotate(-self.player.rot)

        hits = pygame.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            for bullet in hits[hit]:
                hit.health -= bullet.damage
            hit.vel = vec(0, 0)

        hits = pygame.sprite.groupcollide(self.mines, self.mobs, False, False)
        for hit in hits:
            if not hit.detonating:
                hit.mine_detonate()

        hits = pygame.sprite.groupcollide(self.mobs, self.explosions, False, False)
        for expl in self.explosions:
            if expl.lethal:
                for hit in hits:
                    hit.kill()
                    self.score += 1

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (x, 0), (x, HEIGHT))

        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, LIGHTBLUE, (0, y), (WIDTH, y))

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("ZOMBIE SHOOTER", self.title_font, 60, RED, WIDTH / 2, 120, align="center")

        self.draw_text("Arrow keys - Move", self.title_font, 40, CYAN, WIDTH / 2, HEIGHT / 2 - 60, align="center")
        self.draw_text("Space - Shoot", self.title_font, 40, CYAN, WIDTH / 2, HEIGHT / 2 - 15, align="center")
        self.draw_text("G - Change Weapon", self.title_font, 40, CYAN, WIDTH / 2, HEIGHT / 2 + 30, align="center")
        self.draw_text("P - Pause", self.title_font, 40, CYAN, WIDTH / 2, HEIGHT / 2 + 75, align="center")
        self.draw_text("Press any key to Start", self.title_font, 75, RED, WIDTH / 2, HEIGHT * 3 / 4, align="center")

        pygame.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("Enemies Killed {}".format(self.score), self.title_font, 60, RED, WIDTH / 2, 100, align="center")
        self.draw_text("Time Left {} secs".format(self.set_time), self.title_font, 45, RED, WIDTH / 2, 180, align="center")
        self.draw_text("GAME OVER", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Press Enter to Play Again", self.title_font, 70, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")

        pygame.display.flip()
        self.wait_for_key(key=1)

    def wait_for_key(self, key=None):
        pygame.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.quit()

                if event.type == pygame.KEYUP:
                    if key == None:
                        waiting = False
                    else:
                        if event.key == pygame.K_RETURN:
                            waiting = False


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()
