from random import randint
import time

class Pos:
    """
    Класс используется для создания точки
    Атрибуты
    ----------
    x и y - координаты точки
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f'Pos{self.x, self.y}'

class Ship:
    """
    Класс используется для создания корабля (списка точек из которого состоит корабль)
    Атрибуты
    ----------
    head - начало корабля - объект класса Pos
    size - длина корабля от 1 до 4
    rotate - поворот в пространстве, True - вдоль оси x, False - вдоль оси y
    Методы
    ----------
    position - возвращает список точек
    """

    def __init__(self, head, size, rotate):
        self.head = head
        self.size = size
        self.rotate = rotate
        self.health = size

    @property
    def position(self):
        ship_pos = []
        local_x, local_y = None, None
        for i in range(self.size):
            local_x = self.head.x
            local_y = self.head.y
            if self.rotate:
                local_x += i
            else:
                local_y += i
            ship_pos.append(Pos(local_x, local_y))
        return ship_pos # Возвращает список точек - наш корабль

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Стрелять за пределы игрового поля запрещено!!!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли по этим координатам!!!"

class BoardWrongShipException(BoardException):
    pass

class Board:
    """
    Класс хранит информацию о состоянии игрового поля
    Выводит игровое поле в консоль
    Атрибуты
    ----------
    visibility - видимость доски, тип bool, True - для PC и False для игрока
    field - двумерный список состояния игрового поля
    ship_list - список кораблей
    busy - список недоступных координат (сначала для установки, в дальнейшем - для выстрела)
    count - счётчик подбытых кораблей

    Методы
    ----------
    out - метод проверяет нахождение точки в границах игрового поля, False если выходит за границу
    contur - метод создает контур вокруг корабля, недоступный для установки
    add_ship - метод добавляет корабль на поле
    shot - метод обрабатывает координаты выстрела,
            -1 к health корабля с каждым попаданием,
            +1 к count после уничтожения корабля
    start - обнуляем список недоступных координат
    """

    def __init__(self, visibility = False):
        self.visibility = visibility  # видимость доски

        self.field = [['0'] * 6 for _ in range(6)]  #двумерный список состояния игрового поля
        self.ship_list = [] #список кораблей

        self.busy = [] #список занятых полей
        self.count = 0

    def __str__(self): # метод выводит поле
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for row, i in enumerate(self.field):
            res += f'\n{row+1} | {" | ".join(i)} |'
        if self.visibility:
            res = res.replace('■', '0')
        return res

    def out(self, dot): # метод проверяет нахождение точки в границах игрового поля, False если выходит за границу
        return (0 <= dot.x < 6) and (0 <= dot.y < 6)

    def contur(self, ship, visibility = False): # метод создает контур вокруг корабля, недоступный для установки
        near = [
            (-1, 1), (0, 1), (1, 1),
            (-1, 0), (0, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1),
        ]
        for i in ship.position:
            for dx, dy in near:
                res = Pos(i.x + dx, i.y + dy)
                if self.out(res) and res not in self.busy:
                    if visibility:
                        self.field[res.x][res.y] = '.'
                    self.busy.append(res)

    def add_ship(self, ship): # метод добавляет корабль на поле
        for p in ship.position:
            if not (self.out(p) and p not in self.busy):
                raise BoardWrongShipException()
            if p not in self.busy:
                self.field[p.x][p.y] = "■"
                self.busy.append(p)
        self.ship_list.append(ship)
        self.contur(ship)

    def shot(self, p): # делаем выстрел
        if not self.out(p):
            raise BoardOutException()
        if p in self.busy:
            raise BoardUsedException()
        self.busy.append(p)
        for ship in self.ship_list:
            if p in ship.position:
                ship.health -= 1
                self.field[p.x][p.y] = 'X'
                if ship.health == 0:
                    self.count += 1
                    self.contur(ship, visibility = True)
                    print('Корабль уничтожен!!!')
                    return True
                else:
                    print('Корабль поврежден!!!')
                    return True
        self.field[p.x][p.y] = 'T'
        print('Вы промахнулись')
        return False

    def start(self): # обнуляем список занятых полей
        self.busy = []

    def winner(self):
        return self.count == len(self.ship_list)

class Player: # Родительский класс игроков
    """
    Родительский класс игроков

    Атрибуты
    ----------
    board и enemy - игровые поля игроков
    Методы
    ----------
    ask - переопределить в наследываемых классах
    move - передает координаты выстрела на поле соперника
    """

    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    """
    Наследованный класс игрока - человека
    Методы
    ----------
    ask - принимает координаты хода от игрока из консоли и передает в класс Pos
    """

    def ask(self):

        while True:
            step = input('Ваш ход:   ').split()
            if len(step) != 2:
                print('Введите две координаты!')
                continue
            x, y = step
            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа!')
                continue
            x, y = int(x), int(y)

            return Pos(x - 1, y - 1)


class AI(Player):
    """
       Наследованный класс игрока - AI
       Методы
       ----------
       ask - принимает координаты случайного хода и передает в класс Pos

    """

    def ask(self):
        d = Pos(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера {d.x + 1} {d.y + 1}')
        return d

class Game:
    """
    класс игры
    Атрибуты
    ----------
    navy - корабли флотилии (количество и размер)
    player_board - генерируем игровое поле игрока - человека
    AI_board - генерируем игровое поле игрока - AI, переключаем visibilitu, чтобы скрыть корабли соперника
    pl и ai - создаем игроков, передав им игровые поля

    Методы
    ----------
    rules - выводим правила игры
    screen - выводим приветственную заставку
    bay - прощальная заставка
    board_maker - расставляем случайным образом корабли на игровом поле
    board_maker_secure - гарантированно расставляет корабли на игровом поле
    join_board - выводит игровые поля рядом
    game_cycle - цикл, управляющий игрой
    play_game - запускает или прекращает игру
    """

    def __init__(self):
        self.navy = [3, 2, 2, 1, 1, 1, 1]
        player_board = self.board_maker_secure()
        ai_board = self.board_maker_secure()
        ai_board.visibility = True

        self.pl = User(player_board, ai_board)
        self.ai = AI(ai_board, player_board)

    def rules(self):
        print("************************************")
        print("    Правила игры - просты!")
        print("     стреляй метко: x y")
        print("      x - номер строки")
        print("      y - номер столбца")
        print("  Не стреляй за пределы поля!")
        print("Будь хитрее, не стреляй два раза\n     в одно и тоже место!")
        print("       Попутного ветра!")
        print("************************************")

    def screen(self):
        print(".. ^ v ^ _____$$")
        print("_____________$_$$")
        print("_____________$$$ ….       ^ v ^")
        print("____________$$_§§§.")
        print("___________$$$_§§§§§")
        print("___________$_$_§§§§§§       ^ v ^")
        print("__________$$_$__§§§§§§")
        print("_________$$$_$__§§§§§§§")
        print("________$$$$_$__§§§§§§§§")
        print("_______$$$$$_$__§§§§§§§§")
        print("_____$$$$$$$_$__§§§§§§§§§")
        print("____$$$$$$$$_$_§§§§§§§§§§§")
        print("_$_$$$$$$$$$_$_§§§§§§§§§§§")
        print("_$$_$________$$$_____$$$$$___$$")
        print("__$$$$$$$$$$$$$$$$$$$$$$$_$$$$.")
        print("___$$$$$$$$$$$$$$$$$$$$$$$$$$")
        print('\nДОБРО ПОЖАЛОВАТЬ В ИГРУ "МОРСКОЙ БОЙ"')

    def bay(self):
        print('░░░░░░░░░░░░░░░░▄▄░░░░░░░░░░░░░░░░')
        print('░░░░░░░░░░▄█████▀▀▀░░░░░░░░░░░░░░░')
        print('░░░░░░░░░░██▀▀░░▄▄▄░░░░░░░░░░░░░░░')
        print('░░░░░░░░░▄▄▄████████░░█▄▄░░░░░░░░░')
        print('░░░░░░░▀█████████████░▀███▄░░░░░░░')
        print('░░░░░░░░▀████████████░░█████▄░░░░░')
        print('░░░░░░░░░█████████████░▀█████▄░░░░')
        print('░░░░░░░░░░████████████░░██████▄░░░')
        print('░░░░░░░░░░████████████░░███████▄░░')
        print('░░░░░░░░░░████████████░░░░░░░░░░░░')
        print('█████████▄▀▀▀░░░░░░░░░░██████████░')
        print('██████████▄▄▄▄▄▄▄▄▄▄▄▄██████████▀░')
        print('░▀▀▀███████████████████████████▀░░')
        print('░░░░░█████████████████████████▀░░░')
        print('░░░░░░▀▀░▀▀███▀▀░░▀▀███▀▀░▀▀▀░░░░░')
        print('█▄▄▄▄▄▄▄██▄▄▄▄▄▄██▄▄▄▄▄▄██▄▄▄▄▄▄▄█')
        print('▀███████▀███████▀▀███████▀███████▀')
        print('░░░▀▀▀░░░░░▀▀▀░░░░░░▀▀▀░░░░░▀▀▀░░░')

    def board_maker(self):

        board = Board()
        attempts = 0
        for i in self.navy:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Pos(randint(0,5),randint(0,5)), i, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start()
        return board

    def board_maker_secure(self):
        board = None
        while board is None:
            board = self.board_maker()
        return board

    def join_board(first, second):
        first_lines = first.split("\n")
        second_lines = second.split("\n")
        res = ''
        for i in range(len(first_lines)):
            result_line = f'{first_lines[i]}    ||   {second_lines[i]}\n'
            res += result_line
        return res

    def game_cycle(self):
        step = 0
        while True:
            user_board = "Игровое поле пользователя  \n" + str(self.pl.board)
            ai_board = "  Игровое поле компьютера\n" + str(self.ai.board)
            print(Game.join_board(user_board, ai_board))
            if step % 2 == 0:
                print('Ходит пользователь: ')
                repeat = self.pl.move()
            else:
                print('Ходит компьютер: ')
                time.sleep(randint(1, 4))
                repeat = self.ai.move()
            if repeat:
                step -= 1
            if self.ai.board.winner():
                print(Game.join_board(user_board, ai_board))
                print("Пользователь выиграл!")
                break
            if self.pl.board.winner():
                print(Game.join_board(user_board, ai_board))
                print("Компьютер выиграл!")
                break
            step += 1

    def play_game(self):
        self.screen()
        time.sleep(3)
        self.rules()
        time.sleep(3)
        self.game_cycle()
        self.bay()
        print()
        print('\tПопутного ветра !!!')

game = Game()
game.play_game()



