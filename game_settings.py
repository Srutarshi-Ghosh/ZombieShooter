import pygame
vec = pygame.math.Vector2

TITLE = "ZOMBIE SHOOTER"
WIDTH = 1024
HEIGHT = 704
FPS = 60
FONT_NAME = 'arial'


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BROWN = (106, 53, 5)
CYAN = (0, 160, 105)

BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEM_LAYER = 1
SPAWNER_LAYER = 2

MAP = 'level1.tmx'

MOB_IMG = "zombie1_hold.png"
MOB_SPEEDS = [180, 160, 150, 160, 140, 180, 180]
MOB_HIT_RECT = pygame.Rect(0, 0, 32, 32)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 14
AVOID_RADIUS = 50
DETECT_RADIUS = 450
TOTAL_MOBS = 35


SPAWNER_IMG = "tent-tan.png"
SPAWN_FREQUENCY = 6000
SPAWN_RADIUS = 100
SPAWNER_HEALTH = 500
SPAWNER_KNOCKBACK = 40


WEAPONS = {
           'pistol': {'player_image': 'manBlue_gun.png',
                      'bullet_speed': 700,
                      'bullet_lifetime': 900,
                      'rate': 250,
                      'kickback': 200,
                      'spread': 4,
                      'damage': 20,
                      'bullet_size': 'lg',
                      'bullet_count': 1,
                      'barrel_offset': vec(30, 10),
                      'hands': 1
                      },

           'double gun': {'player_image': 'manBlue_Doublegun.png',
                          'bullet_speed': 700,
                          'bullet_lifetime': 900,
                          'rate': 250,
                          'kickback': 200,
                          'spread': 4,
                          'damage': 20,
                          'bullet_size': 'lg',
                          'bullet_count': 1,
                          'barrel_offset_right': vec(30, 10),
                          'barrel_offset_left': vec(30, -10),
                          'hands': 2
                          },

           'shotgun': {'player_image': 'manBlue_machine.png',
                       'bullet_speed': 500,
                       'bullet_lifetime': 500,
                       'rate': 900,
                       'kickback': 300,
                       'spread': 12,
                       'damage': 10,
                       'bullet_size': 'sm',
                       'bullet_count': 6,
                       'barrel_offset': vec(30, 10),
                       'hands': 1
                       },

           'mines': {'player_image': 'ManBlue_mine.png',
                     'damage': 100,
                     'radius': 150,
                     'rate': 1000,
                     'detonation_time': 2000
                     }
           }

PLAYER_IMAGES = [WEAPONS[i]['player_image'] for i in WEAPONS]
PLAYER_SPEED = 250
PLAYER_ROT_SPEED = 250
PLAYER_HEALTH = 100
PLAYER_HIT_RECT = pygame.Rect(0, 0, 36, 36)
BARREL_OFFSET_RIGHT = vec(30, 10)
BARREL_OFFSET_LEFT = vec(30, -10)

BULLET_IMG = "Bullet.png"
MINE_IMG = "mine-1.png"
MINE_EXPL_IMG = "mine-2.png"
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NUZZLE_FLASHES = ['whitePuff{}.png'.format(i) for i in range(15, 19)]
FLASH_DURATION = 80

ITEM_IMAGES = {'Health': 'health_pack.png', 'Shotgun': 'obj_shotgun.png', 'Mine': 'mine.png'}
HEALTH_AMOUNT = 50
BOB_RANGE = 15
BOB_SPEED = 0.5

BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['gun.wav'],
                 'shotgun': ['shotgun.wav'],
                 'double gun': ['gun.wav']}

EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav',
                  'mine_pickup': 'mine_pickup.wav',
                  'mine_place': 'mine_place.wav'}

SPLAT_IMG = 'splat green.png'
NIGHT_COLOR = (10, 10, 10)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = 'light_350_soft.png'

EXPLOSION_ANIMATION = {'mine': {'explosion_image': ['mine-1.png', 'mine-2.png']+['expl_01_00{:02d}.png'.format(i) for i in range(1, 16)],
                                'explosion_range': 200},
                       'spawner': {'explosion_image': ['expl_03_00{:02d}.png'.format(i) for i in range(2, 24)],
                                   'explosion_range': 160}}

EXPLOSION_SOUNDS = {'mine': ['Explosion11.wav'],
                    'spawner': ['Spawner_expl.wav']}

