import pygame
from itertools import *
import pytmx
import random
from Tile_settings import *
import pytweening as tween
vec = pygame.math.Vector2


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if  hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x

    if dir == 'y':
        hits = pygame.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


def draw_health(sprite, total_health):
    if sprite.health > 60 * total_health / 100:
        col = GREEN
    elif sprite.health > 30 * total_health / 100:
        col = YELLOW
    else:
        col = RED
    width = int(sprite.rect.width * sprite.health / total_health)
    sprite.health_bar = pygame.Rect(0, 0, width, 7)
    if sprite.health < total_health:
        temp = sprite.image.copy()
        pygame.draw.rect(temp, col, sprite.health_bar)
        sprite.image = temp

class Player(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.image = game.player_images['pistol']
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon_list = ['double gun']
        self.weapon = 'double gun'
        self.index = 0
        self.damaged = False
        self.mines = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel =  vec(0, 0)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def change_weapon(self, key=1, direct=-1):
        if direct != -1 and direct <= len(self.weapon):
            self.index = direct - 1
        elif direct == -1:
            self.index = (self.index + key) % len(self.weapon_list)
        self.weapon = self.weapon_list[self.index]
        self.image = self.game.player_images[self.weapon]

    def shoot(self):
        if self.weapon == 'mines':
            now = pygame.time.get_ticks()
            if now - self.last_shot > WEAPONS[self.weapon]['rate']:
                self.last_shot = now
                Mine(self.game, self.pos.x, self.pos.y)
                self.game.effects_sounds['mine_place'].play()
                self.mines -= 1
                if self.mines == 0:
                    self.weapon_list.remove('mines')
                    self.change_weapon(direct=len(self.weapon_list) - 1)
        else:
            if WEAPONS[self.weapon]['hands'] == 1:
                now = pygame.time.get_ticks()
                if now - self.last_shot > WEAPONS[self.weapon]['rate']:
                    self.last_shot = now
                    dir = vec(1, 0).rotate(-self.rot)
                    pos = self.pos + WEAPONS[self.weapon]['barrel_offset'].rotate(-self.rot)
                    self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
                    for i in range(WEAPONS[self.weapon]['bullet_count']):
                        spread = random.uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                        Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                        snd = random.choice(self.game.weapon_sounds[self.weapon])
                        if snd.get_num_channels() > 2:
                            snd.stop()
                        snd.play()
                    NuzzleFlash(self.game, pos)
            else:
                now = pygame.time.get_ticks()
                if now - self.last_shot > WEAPONS[self.weapon]['rate']:
                    self.last_shot = now
                    dir = vec(1, 0).rotate(-self.rot)
                    pos_right = self.pos + WEAPONS[self.weapon]['barrel_offset_right'].rotate(-self.rot)
                    pos_left = self.pos + WEAPONS[self.weapon]['barrel_offset_left'].rotate(-self.rot)
                    self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
                    for i in range(WEAPONS[self.weapon]['bullet_count']):
                        spread = random.uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                        Bullet(self.game, pos_right, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                        Bullet(self.game, pos_left, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                        snd = random.choice(self.game.weapon_sounds[self.weapon])
                        if snd.get_num_channels() > 2:
                            snd.stop()
                        snd.play()
                    NuzzleFlash(self.game, pos_right)
                    NuzzleFlash(self.game, pos_left)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 3)

    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pygame.transform.rotate(self.game.player_images[self.weapon], self.rot)
        if self.damaged:
            try:
                self.image.fill((*WHITE, next(self.damage_alpha)), special_flags=pygame.BLEND_RGBA_MULT)
            except:
                self.damaged = False

        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def draw_player_health(self, surf, x, y, pct):
        if pct < 0:
            pct = 0
        BAR_LENGTH = 100
        BAR_HEIGHT = 20

        fill = pct * 100
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        if pct > 0.6:
            col = GREEN
        elif pct > 0.3:
            col = YELLOW
        else:
            col = RED

        pygame.draw.rect(surf, col, fill_rect)
        pygame.draw.rect(surf, WHITE, outline_rect, 2)

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Mob(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.mob_img.copy()
        self.game = game
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.pos = vec(x, y)
        self.speed = random.choice(MOB_SPEEDS)
        self.hit_rect.center = self.pos
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.target = game.player

    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS**2:
            if random.random() < 0.008:
                random.choice(self.game.zombie_sounds['zombie_moan_sounds']).play()
            self.rot = target_dist.angle_to(vec(1, 0))
            self.image = pygame.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

        if self.health <= 0:
            random.choice(self.game.zombie_sounds['zombie_hit_sounds']).play()
            self.kill()
            self.game.score += 1
            self.game.map_img.blit(self.game.splat_img, self.pos - vec(32, 32))


class Spawner(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self._layer = SPAWNER_LAYER
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.spawner_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.game = game
        self.spawn_time = pygame.time.get_ticks()
        self.spawn_count = 0
        self.pos = vec(x, y)
        self.health = SPAWNER_HEALTH

    def spawn_mob(self):
        now = pygame.time.get_ticks()
        if now - self.spawn_time > SPAWN_FREQUENCY and len(self.game.mobs) <= TOTAL_MOBS:
            Mob(self.game, self.pos.x + random.randrange(-SPAWN_RADIUS, SPAWN_RADIUS), self.pos.y + random.randrange(-SPAWN_RADIUS, SPAWN_RADIUS))
            self.spawn_time = now
            self.spawn_count += 1

    def update(self):
        self.spawn_mob()
        if self.health <= 0:
            self.kill()
            Explosion('spawner', self.game, self.rect.centerx, self.rect.centery, lethal=False)
            self.game.explosion_sounds['spawner'][0].play()


class Wall(pygame.sprite.Sprite):

    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Bullet(pygame.sprite.Sprite):

    def __init__(self, game, pos, dir, damage):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * random.uniform(0.9, 1.1)
        self.spawn_time = pygame.time.get_ticks()
        self.damage = damage
        self.life_time = WEAPONS[self.game.player.weapon]['bullet_lifetime']

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pygame.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pygame.time.get_ticks() - self.spawn_time > self.life_time:
            self.kill()


class Mine(pygame.sprite.Sprite):

    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mines
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mine_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.detonation_time = WEAPONS['mines']['detonation_time']
        self.detonating = False

    def mine_detonate(self):
        #self.explosion_alpha = chain(EXPLOSION_ALPHA * 3)
        self.detonating = True
        self.start = pygame.time.get_ticks()
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75
        self.frame = 0



    def update(self):
        if self.detonating:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_rate:
                self.last_update = now
                self.frame += 1
                if pygame.time.get_ticks() - self.start > self.detonation_time:
                    Explosion('mine', self.game, self.rect.centerx, self.rect.centery, frame=2)
                    self.kill()
                    self.game.explosion_sounds['mine'][0].play()

                if self.frame == 2:
                    self.frame = 0

                center = self.rect.center
                self.image = self.game.explosion_images['mine'][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Map:

    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class Tiledmap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:

    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + WIDTH // 2
        y = -target.rect.centery + HEIGHT // 2
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIDTH), x)
        y = max(-(self.height - HEIGHT), y)
        self.camera = pygame.Rect(x, y, self.width, self.height)

class NuzzleFlash(pygame.sprite.Sprite):

    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = random.randint(20, 50)
        self.image = pygame.transform.scale(random.choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Explosion(pygame.sprite.Sprite):

    def __init__(self, sprite, game, x, y, frame=0, frame_rate=75, lethal=True):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites, game.explosions
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.sprite = sprite
        self.image = game.explosion_images[sprite][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = frame_rate
        self.frame = frame
        self.lethal = lethal

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1

            if self.frame == len(EXPLOSION_ANIMATION[self.sprite]['explosion_image']):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_images[self.sprite][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Item(pygame.sprite.Sprite):

    def __init__(self, game, pos, type):
        self._layer = ITEM_LAYER
        self.groups = game.all_sprites, game.items
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self):
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

