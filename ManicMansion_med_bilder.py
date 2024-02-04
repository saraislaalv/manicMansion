import pygame as pg
import sys
import random
import math

# Konstanter
WIDTH = 800
HEIGHT = 800
width=30
height=30
player_width=50
player_height=50
# Størrelsen til vinduet
SIZE = (WIDTH, HEIGHT)
# Frames per second (bilder per sekund)
FPS = 60
# Farger
GREEN = (19,109,21)
DARKGREEN = (19, 80, 21)
GRAY = (150,150,150)
carrying_sheep=False

# Henter bildene
player_img = pg.transform.scale(pg.image.load('player.png'), (player_width, player_height))
player2_img = pg.transform.scale(pg.image.load('player2.png'), (player_width, player_height))
ghost_img = pg.transform.scale(pg.image.load('ghost.png'), (width, height))
sheep_img = pg.transform.scale(pg.image.load('sheep.png'), (width, height))
block_img = pg.transform.scale(pg.image.load('stone.png'), (width, height))

# Initierer pygame
pg.init()
surface = pg.display.set_mode(SIZE)
clock = pg.time.Clock()
#Definerer fonten
font = pg.font.SysFont('Arial', 26)
run = True

# Klassen game object som alle objektene skal arve av.
# Jeg har ikke brukt alle metodene som de som stod i UML-diagrammet, fordi jeg ikke så det som nødvendig i min kode.
# Fbevegelsesobjektet har jeg allerede i spiller-klassen, og plasseringen er såppas forskjellig fra objekt til objekt at jeg syntes det var enklere uten.
class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Spillbrett-klassen som tegner spillbrettet og spillobjektene
# Jerg har ikke med metoden som fjerner objektene, fordi jeg ikke fant det hensiktsmessig i min kode. Jeg fjerner heller sauene fra listen i stedet for å ha en egen metode for det.
class GameBoard(GameObject):
    def __init__(self):
        super().__init__(0, 0)
        
    def draw_background(self, surface):
        surface.fill(GREEN)
        pg.draw.rect(surface, DARKGREEN, pg.Rect(0, 0, 100, 800))
        pg.draw.rect(surface, DARKGREEN, pg.Rect(700, 0, 100, 800))

    def draw_image(self, img, x, y, width, height):
        surface.blit(img, (x, y))

# Spilleren man kontrollerer med piltastene
class Player(GameObject):
    def __init__(self, width, height, speed, points):
        # Arver x og y-koorinater fra overklassen
        super().__init__(20, 300)
        self.points= 0
        self.speed= speed
        self.width= width
        self.height = height
    
    def movement(self, keys, blocks):
        # Metoden som gjør det mulig å flytte på spilleren. 
        new_x, new_y = self.x, self.y
        new_x -= self.speed if keys[pg.K_LEFT] else 0
        new_x += self.speed if keys[pg.K_RIGHT] else 0
        new_y -= self.speed if keys[pg.K_UP] else 0
        new_y += self.speed if keys[pg.K_DOWN] else 0
    
        # Legger begrensninger for spilleren til å holde seg innenfor spillbrettet pg frisonene
        new_x = max(0, min(WIDTH - self.width, new_x))
        new_y = max(0, min(HEIGHT - self.height, new_y))
    
        #Sørger for at det ikke er mulig for spilleren å gå gjennom blokkene
        for block in blocks:
            if (new_x < block.x + block.width
                    and new_x + self.width > block.x
                    and new_y < block.y + block.height
                    and new_y + self.height > block.y):
                return

        self.x, self.y = new_x, new_y

    def reduce_speed(self):
        # Metode som senker farten dersom en sau blir båret
        if carrying_sheep is True:
            self.speed = 2.5
        else:
            self.speed=4
    def increase_points(self):
        self.points += 1
    def check_collision(self, other):
        # Denne metoden brukes for å sbjekke kollisjon med både spøkelser og sauer
        return (
            self.x < other.x + other.width
            and self.x + self.width > other.x
            and self.y < other.y + other.height
            and self.y + self.height > other.y)

# Klassen til blokkene som skal stå ute på spillbrettet
class Block(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width = width
        self.height = height

# Klassen til spøkelset som skal bevege seg rundt på spillebrettet
class Ghost(GameObject):
    def __init__(self, width, height, speed):
        super().__init__(random.randint(110, 660), random.randint(10, 760))
        self.width = width
        self.height = height
        self.speed = speed
        # 
        self.angle = random.uniform(0, 360)
    
    # Metoden som gjør at spøkelset spretter tilbake når det treffer veggen
    def change_direction(self):
        # Jeg har brukt vinkler for å ikke bare få spøkelset til å sprette i rette linjer. Jeg fikk hjelp fra denne nettsiden:
        # https://stackoverflow.com/questions/53426079/pygame-trigonometry-position-jittering-when-moving-target 
        angle_rad = math.radians(self.angle)
        delta_x, delta_y = self.speed * math.cos(angle_rad), self.speed * math.sin(angle_rad)
        self.x += delta_x
        self.y += delta_y

        if self.x + self.width >= 700 or self.x <= 100:
            self.angle = 180 - self.angle

        if self.y + self.height >= 800 or self.y <= 0:
            self.angle = 360 - self.angle

# Klassen til sauene som skal stå på frisonen
# Jeg har ingen metoder som tilsier om sauen blir løftet fordi jeg syntes det var enklere å ha inni while run løkken og bruke en boolean i stedet.
class Sheep(GameObject):
    def __init__(self, x, y, width, height):
        super().__init__(x, y)
        self.width, self.height = width, height

# Jeg har brukt en funskjon for å lage flere blokker og sauer på en gang ved å hente inn antallet og lage en liste.
def create_objects(num_objects, x_range, y_range, width, height, obj_class, min_distance=50):
    objects = []
    for i in range(num_objects):
        x = random.randint(*x_range)
        y = random.randint(*y_range)
        # Sjekk om det valgte stedet overlapper med eksisterende objekter
        while any(
            (obj.x - min_distance <= x <= obj.x + obj.width + min_distance and
             obj.y - min_distance <= y <= obj.y + obj.height + min_distance)
            for obj in objects
        ):
            x = random.randint(*x_range)
            y = random.randint(*y_range)

        obj = obj_class(x, y, width, height)
        objects.append(obj)

    return objects

# Starter spillet med å lage 3 blokker og 3 sauer
blocks=create_objects(3, (110, 660), (10, 760), width, height, Block)
sheep_list = create_objects( 3, (700, 770), (20, 750), width, height, Sheep)

# Skriver ut poengsummen til spillbrettet
def display_points(points):
    text_img = font.render(f"Score:{points}", True, GRAY)
    surface.blit(text_img, (10,20))

# Definerer spillbrettet
game_board = GameBoard()

# Definerer spilleren og spøkelset. num_ghosts bruker jeg for å senere kunne legge til fler spøkelser for å øke vanselighetsgraden
player = Player(width, height, 4, 0)
num_ghosts = player.points+1
ghosts = [Ghost(width, height, 4) for i in range(num_ghosts)]

while run:
    # Spillet avsluttes om man trykker på avsluttkanppen oppe i hjørnet
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
    
    # Tegner bakgrunnen
    game_board.draw_background(surface)
    # Går gjennom alle spøkelsene i listen og sjekker om den kolliderer med spilleren.
    # Da avsluttes spillet.
    for ghost in ghosts:
        if player.check_collision(ghost):
            run = False
        # Henter funskjonen som gjør at spøkelset spretter i veggene
        # Tegner alle spøkelsene
        ghost.change_direction()
        game_board.draw_image(ghost_img, ghost.x, ghost.y, ghost.width, ghost.height)
    
    #Tegner alle blokkene
    for block in blocks:
        game_board.draw_image(block_img, block.x, block.y, block.width, block.height)
    
    # Går gjennom alle sauene og sjekker om en av dem kolliderer med spilleren
    # Isåfall, fjernes sauen fra listen (dvs at den slutter å tegnes), og hastigheten til spilleren reduseres
    for sheep in sheep_list:
        game_board.draw_image(sheep_img, sheep.x, sheep.y, sheep.width, sheep.height)
        if player.check_collision(sheep):
            sheep_list.remove(sheep)
            carrying_sheep=True
            player.reduce_speed()
    
    # Tegner spøkelset
    #game_board.draw_objects(surface, ghost.x, ghost.y, ghost.width, ghost.height, BLUE)
    
    # Hvis spilleren ikke bærer sauen,. vil hastigheten økes igjen, og spilleren vil gå tilbake til rød
    if carrying_sheep is False:
        game_board.draw_image(player_img, player.x, player.y, player.width, player.height)
        player.reduce_speed()
    else:
        game_board.draw_image(player2_img, player.x, player.y, player.width, player.height)
        # Stopper spillet hvis du treffer en sau i mens du bærer en sau
        if len(sheep_list)==1 and player.check_collision(sheep):
            run = False
        # Når spilelren kommer til frisonen på den andre siden, får den et poeng og vanskelighetsgraden økes.
        if player.x < 70:
            carrying_sheep=False
            sheep_list = create_objects( 3, (700, 770), (20, 750), width, height, Sheep)
            player.increase_points()
            number=3+player.points
            blocks= create_objects(number, (110, 660), (10, 760), width, height, Block)
            num_ghosts = player.points+1
            ghosts = [Ghost(width, height, 4) for i in range(num_ghosts)]
        
    display_points(player.points)
    keys = pg.key.get_pressed()
    player.movement(keys, blocks)

    pg.display.flip()
    clock.tick(FPS)

pg.quit()
sys.exit()

