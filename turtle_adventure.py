"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
from math import floor
import math
import random



class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x-10, self.y-10, self.x+10, self.y+10)
            self.canvas.coords(self.__id2, self.x-10, self.y+10, self.x+10, self.y-10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int], size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y
        self.__counter = 0

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown", width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size/2,
                           self.y - self.size/2,
                           self.x + self.size/2,
                           self.y + self.size/2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x-self.size/2, self.x+self.size/2
        y1, y2 = self.y-self.size/2, self.y+self.size/2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False) # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float):
        super().__init__(game)
        self.__size = size
        self.__color = color
        self.__speed = speed

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color
    
    @property
    def speed(self) -> float:
        """Return the speed of the enemy

        Returns:
            float: speed of the enemy
        """
        return self.__speed
    
    @speed.setter
    def speed(self, new_speed: float):
        self.__speed = new_speed
        
    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
            (self.x - self.size/2 < self.game.player.x < self.x + self.size/2)
            and
            (self.y - self.size/2 < self.game.player.y < self.y + self.size/2)
        )
        
    def generate_spawn_loca(self):
        x = random.choice((0,self.game.canvas.winfo_width()))
        y = random.choice((0,self.game.canvas.winfo_height()))
        range_x = [(x,x+1), (0, self.game.canvas.winfo_width())]
        range_y = [(y,y+1), (0, self.game.canvas.winfo_height())]
        choose_index = random.randint(0,1)
        return random.randrange(*range_x[choose_index]), random.randrange(*range_y[1-choose_index])


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str = "green", 
                 speed: float = 1):
        super().__init__(game, size, color, speed)
        self.__to_x = random.randrange(0, self.game.canvas.winfo_width())
        self.__to_y = random.randrange(0, self.game.canvas.winfo_height())

    def create(self) -> None:
        pos = self.generate_spawn_loca()
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    def update(self) -> None:
        distance = math.sqrt((self.__to_x-self.x)**2 + (self.__to_y-self.y)**2)
        self.x += self.speed * (self.__to_x-self.x) / distance
        self.y += self.speed * (self.__to_y-self.y) / distance
        if floor(self.x/self.speed/5) == floor(self.__to_x/self.speed/5) and floor(self.y/self.speed/5) == floor(self.__to_y/self.speed/5):
            self.__to_x = random.randrange(0, self.game.canvas.winfo_width())
            self.__to_y = random.randrange(0, self.game.canvas.winfo_height())
        if self.hits_player():
            self.game.game_over_lose()
            

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
        
class ChasingEnemy(Enemy):
    """
    Chasing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str, 
                 speed: float = 1):
        super().__init__(game, size, color, speed)

    def create(self) -> None:
        pos = self.generate_spawn_loca()
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    def update(self) -> None:
        distance = math.sqrt((self.game.player.x-self.x)**2 + (self.game.player.y-self.y)**2)
        self.x += self.speed * (self.game.player.x-self.x) / distance
        self.y += self.speed * (self.game.player.y-self.y) / distance
        if self.hits_player():
            self.game.game_over_lose()
            

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

class FencingEnemy(Enemy):
    """
    Chasing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str, 
                 speed: float = 1,
                 side: float = 300,
                 reverse: bool = False):
        super().__init__(game, size, color, speed)
        self.__index = 0
        self.__to = []
        s = side/2
        h_x = self.game.home.x
        h_y = self.game.home.y
        self.__sides = [[h_x+s, h_y+s],[h_x+s, h_y-s],[h_x-s, h_y-s],[h_x-s, h_y+s]]
        self.__reverse = reverse

    def create(self) -> None:
        pos = self.generate_spawn_loca()
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    def update(self) -> None:
        x = self.__sides[self.__index][0]
        y = self.__sides[self.__index][1]
        distance = math.sqrt((x-self.x)**2 + (y-self.y)**2)
        self.x += self.speed * (x-self.x) / distance
        self.y += self.speed * (y-self.y) / distance
        if floor(self.x/self.speed/5) == floor(x/self.speed/5) and floor(self.y/self.speed/5) == floor(y/self.speed/5):
            self.switch_place()
        if self.hits_player():
            self.game.game_over_lose()
        

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
        
    def switch_place(self):
        if self.__reverse:
            self.__index -= 1
            if self.__index < 0:
                self.__index = 3
        else:
            self.__index += 1
            if self.__index > 3:
                self.__index = 0
        
class BossEnemy(Enemy):
    """
    Boss enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str, 
                 speed: float = 1):
        super().__init__(game, size, color, speed)

    def create(self) -> None:
        pos = self.generate_spawn_loca()
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    @property
    def id(self):
        return self.__id

    def update(self) -> None:
        distance = math.sqrt((self.game.player.x-self.x)**2 + (self.game.player.y-self.y)**2)
        self.x += self.speed * (self.game.player.x-self.x) / distance
        self.y += self.speed * (self.game.player.y-self.y) / distance
        if random.randint(0,1) == 1:
            new_enemy = Bullet(self.game, 10, 'black', self.x, self.y, 2)
            self.game.add_enemy(new_enemy)
            
        if self.hits_player():
            self.game.game_over_lose()
            

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
        
class Bullet(Enemy):
    """
    Chasing enemy
    """
    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str, 
                 x:int,
                 y:int,
                 speed: float = 1,):
        super().__init__(game, size, color, speed)
        self.__speedx = 0
        self.__speedy = 0
        self.__acceleration = speed * 0.1
        self.__x = x
        self.__y = y
    
    @property
    def id(self):
        return self.__id
    
    def create(self) -> None:
        pos = [self.__x, self.__y]
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    def update(self) -> None:
        distance = math.sqrt((self.game.player.x-self.x)**2 + (self.game.player.y-self.y)**2)
        self.__speedx += self.__acceleration * (self.game.player.x-self.x) / distance
        self.__speedy += self.__acceleration * (self.game.player.y-self.y) / distance
        # if abs(self.__speedx) > self.speed:
        #     self.__speedx = self.__speedx / abs(self.__speedx) * 2
        # if abs(self.__speedy) > self.speed:
        #     self.__speedy = self.__speedy / abs(self.__speedy) * 2
        self.x += self.__speedx
        self.y += self.__speedy
        if self.hits_player():
            self.game.game_over_lose()
        if self.x < 0 or self.x > self.game.winfo_width():
            self.game.bullets.pop(0)
            self.game.delete_element(self)
            return 
        if self.y < 0 or self.y > self.game.winfo_height():
            self.game.bullets.pop(0)
            self.game.delete_element(self)
            return

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
        
class OhioLastBossEnemy(Enemy):
    """
    Chasing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str, 
                 speed: float = 1):
        super().__init__(game, size, color, speed)

    def create(self) -> None:
        pos = self.generate_spawn_loca()
        self.__id = self.canvas.create_oval(0,0,0,0,fill=self.color)
        self.x = pos[0]
        self.y = pos[1]
        self.render()

    def update(self) -> None:
        distance = math.sqrt((self.game.player.x-self.x)**2 + (self.game.player.y-self.y)**2)
        self.x += self.speed * (self.game.player.x-self.x) / distance
        self.y += self.speed * (self.game.player.y-self.y) / distance
        if self.hits_player():
            self.game.game_over_lose()
            

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x-self.size/2, self.y -
                            self.size/2, self.x+self.size/2, self.y+self.size/2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)
            

# TODO
# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        num = self.game.enemy_formula(self.__level)
        dtime = 2000 / num

        # example
        deltatime = round((80/99)**self.__level*100)
        self.__game.after(math.floor(dtime)+1, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        if not self.game.is_started:
            return
        if len(self.game.enemies) <= self.game.enemy_formula(self.__level):  
            choose = random.randint(0,1)
            if choose == 1:
                new_enemy = DemoEnemy(self.__game, 20, "red", 3)
            else:
                new_enemy = ChasingEnemy(self.__game, 20, "green", 3)
            # new_enemy.x = 100
            # new_enemy.y = 100
            self.game.add_enemy(new_enemy)
        if len(self.game.fencing_enemies) <= self.game.fencing_formula(self.__level):
            new_enemy = FencingEnemy(self.__game, 20, "blue", 2, random.randint(100,200))
            self.game.add_enemy(new_enemy)
        if self.game.boss_formula(self.__level):
            if len(self.game.boss_enemies) <= self.game.get_boss_amount(self.__level):
                new_enemy = BossEnemy(self.__game, 20, "black", 2)
                self.game.add_enemy(new_enemy)
        self.__game.after(self.game.delta_time_formula(self.__level), self.create_enemy)


class TurtleAdventureGame(Game): # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int, level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.fencing_enemies: list[Enemy] = []
        self.boss_enemies: list[BossEnemy] = []
        self.bullets: list[Bullet] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent, 20)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height-1, self.screen_width-1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self, (self.screen_width-100, self.screen_height//2), 20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>", lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height//2
        

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        if isinstance(enemy, FencingEnemy):
            self.fencing_enemies.append(enemy)
            self.add_element(enemy)
        elif isinstance(enemy, BossEnemy):
            self.boss_enemies.append(enemy)
            self.add_element(enemy)
        elif isinstance(enemy, Bullet):
            self.bullets.append(enemy)
            self.add_element(enemy)
        else:
            self.enemies.append(enemy)
            self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width/2,
                                self.screen_height/2,
                                text="Skill Issue",
                                font=font,
                                fill="red")
                
    @classmethod
    def enemy_formula(cls, level:int):
        return 20 * math.log10(level + 1)
    
    @classmethod
    def fencing_formula(cls, level:int):
        return math.log10(level + 1)*2.3 + 1
    
    @classmethod
    def boss_formula(cls, level:int) -> bool:
        return round(math.sin(level*math.pi/2*(math.log10(level + 1)/5))*10) == 10
    
    @classmethod
    def delta_time_formula(cls, level:int) -> float:
        a = cls.enemy_formula(level) + cls.fencing_formula(level)
        return round(5000 / a)
    
    @classmethod
    def get_boss_amount(cls, level:int) -> int:
        return int(round(-((1/1.02)**(level-35)) + 3)) - 1
    
    @classmethod
    def get_speed(cls, level):
        return (1.07)**(-level + 9) + 1.2
    
