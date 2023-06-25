import random
import sqlite3 as lite
from datetime import date
from tabulate import tabulate


def bot(start, board, bot_num, enemy_num):
    if start == 1 and board["mid-M"] == 0:  # if the enemy started
        return 'mid-M'
    if start == 0:  # if bot started
        return random.choice(('top-L', 'top-R', 'bot-L', 'bot-R'))  # random for various games
    move = []  # list of all moves avilable if no move is winning or losing
    lose = ''
    for (name, num) in board.items():
        if num == 0:  # if the square isn't taken
            move.append(name)
            # check what happens if we play there
            board[name] = bot_num
            if is_win(board) == bot_num:
                return name
            # check what happens if the enemy plays there
            board[name] = enemy_num
            if is_win(board) == enemy_num:
                lose = name
            board[name] = 0  # reset the board after we changed things
    if lose != '':
        return lose
    # if no moves an instant win or a lose
    return random.choice(move)


def print_board(board):
    print('\n')
    print_sqr('top-L', board['top-L'], False)
    print_sqr('top-M', board['top-M'], False)
    print_sqr('top-R', board['top-R'], False)
    print_sqr('mid-L', board['mid-L'], True)
    print_sqr('mid-M', board['mid-M'], False)
    print_sqr('mid-R', board['mid-R'], False)
    print_sqr('bot-L', board['bot-L'], True)
    print_sqr('bot-M', board['bot-M'], False)
    print_sqr('bot-R', board['bot-R'], False)


def print_sqr(name, num, new_line):
    if new_line:
        print('\n=========================')
    if num == 0:
        print(" " + name + " ", end="|")
    elif num == 1:
        print('\033[92m   X   \033[0m', end="|")  # color of x is green
    else:
        print("\033[94m   O   \033[0m", end="|")  # color of x is blue


def is_win(board):
    board_nums = (
    board['top-L'], board['top-M'], board['top-R'], board['mid-L'], board['mid-M'], board['mid-R'], board['bot-L'],
    board['bot-M'], board['bot-R'])
    # check columns
    for i in range(3):
        if board_nums[i] == board_nums[i + 3] == board_nums[i + 6]: return board_nums[i]
    # check rows
    for i in range(0, 8, 3):
        if board_nums[i] == board_nums[i + 1] == board_nums[i + 2]: return board_nums[i]
    # check diagonals
    if board_nums[0] == board_nums[4] == board_nums[8]:
        return board_nums[0]
    if board_nums[2] == board_nums[4] == board_nums[6]:
        return board_nums[2]
    # no win
    return 0


def game(is_computer):
    board = {'top-L': 0, 'top-M': 0, 'top-R': 0, 'mid-L': 0, 'mid-M': 0, 'mid-R': 0, 'bot-L': 0, 'bot-M': 0, 'bot-R': 0}
    turn = int(1)  # to decide who's turn is it, x or 0
    computer_turn = random.choice([1, 2])  # decide whatever computer is x or o
    game_moves = ''
    # main game loop
    for i in range(9):
        turn = (i % 2) + 1  # this way x is always first and is represented by 1, O is represented by 2
        # printing
        print_board(board)
        print("\n================================\nits turn number: " + str(i + 1))  # separate the turns

        # main turn logic
        if is_computer and turn == computer_turn:
            print('Computer is playing')
            move = bot(i, board, turn, ((i + 1) % 2) + 1)  # the calculation is for the enemy num
        else:
            # check for valid input for the turn
            move = input("\nits player " + str(turn) + " turn, enter move: ")
            while True:
                if move in board.keys():
                    if board.get(move) == 0:
                        break
                    else:
                        move = input("square occupied, enter other square: ")
                else:
                    move = input("InValid input, pls enter again: ")
        board[move] = turn  # change the square of the move to whoever turn is playing
        game_moves = game_moves + str(turn) + ':' + move + ', '

        # check for winner
        win = is_win(board)
        if win != 0:
            print_board(board)
            print('\n\nTHE WINNER IS PLAYER NUMBER ' + str(win) + ' !!!!!!')
            break

        # incase we reached the end with no winner, print the board last time
        if i == 8:
            print("======================================\n")
            print_board(board)
            print("\nITS A DRAW!!!!!")
    input("\nto proceed to options, enter any button: ")
    return (game_moves, computer_turn, win)


def save_in_database(game, conn, player1, player2, win):
    curser = conn.cursor()
    # count how many rows to assign ID
    row = curser.execute("SELECT * FROM games")
    counter = 0
    for num in row:
        counter += 1
    insert = """INSERT INTO games (ID, Player1, Player2,Winner,Date,Game) VALUES (?,?,?,?,?,?)"""
    d = date.today().strftime("%d/%m/%Y")
    values = (counter, player1, player2, win, d, game)
    curser.execute(insert, values)
    conn.commit()


def open_database(path, conn=None):
    try:
        conn = lite.connect(path)
    except (lite.Error):
        print("Error %s:" % path)
    return conn


def create_table(cursor, conn):
    try:
        create_str = '''CREATE TABLE IF NOT EXISTS games (
        ID INT PRIMARY KEY NOT NULL,
        Player1 TEXT NOT NULL,
        Player2 TEXT NOT NULL,
        Winner INT NOT NULL,
        Date TEXT NOT NULL,
        Game TEXT NULL
        );'''

        cursor.execute(create_str)
        conn.commit()
    except lite.Error as e:
        print(e)


def fetch_data(name, cursor):
    data = (name, name)
    if name == 'ALL':
        cursor.execute("SELECT * FROM games")
    else:
        cursor.execute("SELECT * FROM games WHERE Player1 = ? OR Player2 = ?", data)
    headers = ['ID', 'Player1', 'Player2', 'Winner', 'Date', 'Game moves']
    print(tabulate(cursor, headers=headers, tablefmt='fancy_grid'))


def main():
    # open the database and create a table(if needed)
    conn = open_database('C:/SqlDatabases/tictactoe.sqlite2')  # enter your path here
    create_table(conn.cursor(), conn)
    # get initial input
    while True:  # As long as the user didn't quit, continue the cycle
        options = input('choose an option:\n1) 2 players\n2) vs computer\n3)get games data\n4)exit\nyour choise here: ')
        # check input
        while True:
            if options.isdigit():
                if 1 <= int(options) <= 4:
                    break
            options = input('Invalid Input. enter a number between 1-3: ')
        options = int(options)

        if options == 4:
            exit()
        elif options == 3:
            name = input("enter your name (type 'ALL' for all games): ")
            fetch_data(name, conn.cursor())
        else:
            name1 = input("enter first player name: ")
            if options != 2:
                name2 = input("enter second player name: ")
            else:
                name2 = 'computer'
            game_record = game(options == 2)  # if options is 2, is_computer is true, else its false
            if options == 1:
                save_in_database(game_record[0], conn, name1, name2, game_record[2])
            else:
                if game_record[1] == 1:
                    save_in_database(game_record[0], conn, name2, name1, game_record[2])
                else:
                    save_in_database(game_record[0], conn, name1, name2, game_record[2])
    conn.close()


if __name__ == '__main__':
    main()
