import chess.engine
import chess.pgn
import os
import time
import asyncio
import pyautogui
import random
import pyscreenshot
from PIL import ImageGrab
from chesstenso import tensorflow_chessbot
from chesstenso import chessboard_finder
from pyclick import HumanClicker
import pytweening
from pyclick.humancurve import HumanCurve


import time

nums = {1:"a", 2:"b", 3:"c", 4:"d", 5:"e", 6:"f", 7:"g", 8:"h"}

def checkColor(x, y):
    bbox = (x, y, x + 1, y + 1)
    im = ImageGrab.grab(bbox=bbox)
    rgbim = im.convert('RGB')
    r, g, b = rgbim.getpixel((0, 0))
    return r, g, b

def GameOver():
    if checkColor(1171, 665) == (127, 166, 80): # One side won
        return True
    if checkColor(693, 519) == (102, 100, 99): # Abort
        return True
    return False

def get_uci(board1, board2, who_moved):
    str_board = str(board1).split("\n")
    str_board2 = str(board2).split("\n")
    move = ""
    moved_piece = ""
    flip = False
    leave = False
    if who_moved == "w":
        for i in range(8)[::-1]:
            for x in range(15)[::-1]:
                if str_board[i][x] != str_board2[i][x]:
                    if moved_piece != "" and (str_board[i][x] != moved_piece and str_board2[i][x] != moved_piece):
                        continue
                    if str_board[i][x] == "." and move == "":
                        flip = True
                    moved_piece = str_board2[i][x]if str_board[i][x] == "."else str_board[i][x]
                    move+=str(nums.get(round(x/2)+1))+str(9-(i+1))
                    if len(move) == 4:
                        leave = True
                        break
            if leave:
                break
    else:
        for i in range(8):
            for x in range(15):
                if str_board[i][x] != str_board2[i][x]:
                    if moved_piece != "" and (str_board[i][x] != moved_piece and str_board2[i][x] != moved_piece):
                        continue
                    if str_board[i][x] == "." and move == "":
                        flip = True
                    moved_piece = str_board2[i][x] if str_board[i][x] == "." else str_board[i][x]
                    move += str(nums.get(round(x / 2) + 1)) + str(9 - (i + 1))
                    if len(move) == 4:
                        leave = True
                        break
            if leave:
                break
    if flip:
        move = move[2]+move[3]+move[0]+move[1]
    return move


def main(legit, who):
    twoply = 0
    wait_interval = 0.1  # The wait time between taking screenshots and retrying commands
    engine_path = r"C:\Users\lunat\Desktop\Engines\BadChess_1.4_MultiTNN\BadChess.exe"  # The absolute path to the engine executable
    engine_max_think_time = 7
    engine_min_think_time = 0.1


    #engine_think_time = 0.5  # <----- The higher this value is the better the engine plays, but also the slower it plays

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    nnue = False

    os.chdir(r"C:\Users\lunat\Downloads\Auto-Chess-main\Auto-Chess-main\chesstenso")

    if who == "w":
        other = "b"
        flip = False
        prev_fen = "IDEK"
    elif who == "b":
        other = "w"
        flip = True
        prev_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    invalid = 0
    board = chess.Board()
    first_move = True

    overhead = 20
    tenminutes = 10 * 60
    timeused = overhead
    while True:
        if GameOver():
            engine.quit()
            return
        image = pyscreenshot.grab()
        image.save("board.png")
        try:
            result = tensorflow_chessbot.main(img='board.png', active=who, unflip=flip)
            accuracy = result[1]
        except:
            time.sleep(wait_interval)
            continue
        if str(result[0]).split(" ")[0] == prev_fen:
            time.sleep(wait_interval)
            continue

        starttime = time.perf_counter() - 1.5

        board1 = chess.Board(result[0])
        if not board1.is_valid():
            if invalid >= 10:
                print(
                    f"Unable to detect a valid board position... Detected board position with {round(accuracy, 2)}% confidence was:")
                print(board1)
                break
            print("Invalid board position detected, retrying...")
            invalid += 1
            time.sleep(wait_interval)
            continue
        invalid = 0

        if not first_move:
            try:
                move_made = get_uci(board, board1, other)
                print("Detected move was: " + move_made, end=", ")
                board.push_uci(move_made)
                tempcastle = board.castling_rights
                board.castling_rights = 0
                if str(board) != str(chess.Board(result[0])):
                    board = chess.Board(result[0])
                else:
                    board.castling_rights = tempcastle
            except:
                board = chess.Board(result[0])
        else:
            first_move = False
            board.castling_rights = 0
            if str(board) != str(chess.Board(result[0])):
                board = chess.Board(result[0])
                board.castling_rights = chess.Board().castling_rights  #Attempting to add castling
                print("Game already started!, fen:", board.fen())
            else:
                print("New Game")
                board = chess.Board()
        print(f"Detected board position with {round(accuracy, 2)}% confidence:")

        if ((twoply/35) > random.random()):
            nnue = True
        else:
            nnue = False

        timeused += (time.perf_counter() - starttime)
        starttime = time.perf_counter()
        timeleft = round(tenminutes - timeused, 3)
        #white_clock
        while 1:
            try:
                if (timeleft <= 0):
                    legit = "n"
                    result = engine.play(board, chess.engine.Limit(time=engine_min_think_time), info=chess.engine.INFO_SCORE,
                                         options={"OwnBook": "true", "Nnue": "true"})
                    nnue = True
                    break
                elif (twoply < 10):
                    result = engine.play(board, chess.engine.Limit(depth=8), info=chess.engine.INFO_SCORE, options={"OwnBook": "true", "Nnue": "true"})
                    nnue = True
                else:
                    if (nnue):
                        result = engine.play(board, chess.engine.Limit(white_clock= timeleft, black_clock= timeleft, remaining_moves=40), info=chess.engine.INFO_SCORE, options={"OwnBook": "true", "Nnue": "true"})
                    else:
                        result = engine.play(board, chess.engine.Limit(white_clock=timeleft, black_clock= timeleft, remaining_moves=40), info=chess.engine.INFO_SCORE, options={"OwnBook": "true", "Nnue": "false"})
                twoply += 1
                break
            except asyncio.exceptions.TimeoutError:
                print("Engine Timeout Error")
                continue
            except chess.engine.EngineTerminatedError:
                print("Engine terminated")
                engine = chess.engine.SimpleEngine.popen_uci(engine_path)
                continue
        #print(board)
        print("Playing Move: " + str(result.move))
        result.info.values()
        print(result.info)
        print("NNUE: ", nnue)
        move = result.move


        try:
            board.push(result.move)
            prev_fen = str(board.fen().split(" ")[0])
        except:
            print("Looks like I got checkmated, how is that even possible?")
            engine.quit()
            return

        board_pos = chessboard_finder.main(url=os.path.abspath('board.png'))

        board_width = board_pos[2] - board_pos[0]
        board_height = board_pos[3] - board_pos[1]

        square_mar_wi = board_width / 8
        square_mar_he = board_height / 8

        if who == "b":
            x_square1 = 9 - (ord(str(move)[0]) - 96)
            y_square1 = int(str(move)[1])
            x_square2 = 9 - (ord(str(move)[2]) - 96)
            y_square2 = int(str(move)[3])
        else:
            x_square1 = ord(str(move)[0]) - 96
            y_square1 = 9 - int(str(move)[1])
            x_square2 = ord(str(move)[2]) - 96
            y_square2 = 9 - int(str(move)[3])

        if legit == "y":
            time.sleep(random.randint(1, 35) / 500)
            hc = HumanClicker()
            curve = HumanCurve(pyautogui.position(), (
            round(board_pos[0] + (square_mar_wi * x_square1) - square_mar_wi / 2) - random.randint(-13, 13),
            round(board_pos[1] + (square_mar_he * y_square1) - square_mar_he / 2) - random.randint(-13, 13)),
                               distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                               offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
            hc.move((round(board_pos[0] + (square_mar_wi * x_square1) - square_mar_wi / 2),
                     round(board_pos[1] + (square_mar_he * y_square1) - square_mar_he / 2)), duration=0.02,
                    humanCurve=curve)
            pyautogui.click()
            curve = HumanCurve(pyautogui.position(), (
            round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2) - random.randint(-5, 5),
            round(board_pos[1] + (square_mar_he * y_square2) - square_mar_he / 2) - random.randint(-10, 10)),
                               distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                               offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
            hc.move((round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                     round(board_pos[1] + (square_mar_he * y_square2) - square_mar_he / 2)), duration=0.005,
                    humanCurve=curve)
            pyautogui.click()
        else:
            pyautogui.click(round(board_pos[0] + (square_mar_wi * x_square1) - square_mar_wi / 2),
                            round(board_pos[1] + (square_mar_he * y_square1) - square_mar_he / 2))
            pyautogui.click(round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                            round(board_pos[1] + (square_mar_he * y_square2) - square_mar_he / 2))

        try:
            if str(move)[4] == "q":
                pyautogui.click()
            elif str(move)[4] == "n":
                if legit == "y":
                    curve = HumanCurve(pyautogui.position(),
                                       (round(board_pos[0] + (
                                                   square_mar_wi * x_square2) - square_mar_wi / 2) - random.randint(-7,
                                                                                                                    7),
                                        round(board_pos[1] + (square_mar_he * (
                                                    y_square2 + 1)) - square_mar_he / 2) - random.randint(-7, 7)),
                                       distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                                       offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
                    hc.move((round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                             round(board_pos[1] + (square_mar_he * (y_square2 + 1)) - square_mar_he / 2)),
                            duration=0.02,
                            humanCurve=curve)
                    pyautogui.click()
                else:
                    pyautogui.click(round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                                    round(board_pos[1] + (square_mar_he * (y_square2 + 1)) - square_mar_he / 2))
            elif str(move)[4] == "r":
                if legit == "y":
                    curve = HumanCurve(pyautogui.position(),
                                       (round(board_pos[0] + (
                                                   square_mar_wi * x_square2) - square_mar_wi / 2) - random.randint(-7,
                                                                                                                    7),
                                        round(board_pos[1] + (square_mar_he * (
                                                    y_square2 + 2)) - square_mar_he / 2) - random.randint(-7, 7)),
                                       distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                                       offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
                    hc.move((round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                             round(board_pos[1] + (square_mar_he * (y_square2 + 2)) - square_mar_he / 2)),
                            duration=0.04,
                            humanCurve=curve)
                    pyautogui.click()
                else:
                    pyautogui.click(round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                                    round(board_pos[1] + (square_mar_he * (y_square2 + 2)) - square_mar_he / 2))
            elif str(move)[4] == "b":
                if legit == "y":
                    curve = HumanCurve(pyautogui.position(),
                                       (round(board_pos[0] + (
                                                   square_mar_wi * x_square2) - square_mar_wi / 2) - random.randint(-7,
                                                                                                                    7),
                                        round(board_pos[1] + (square_mar_he * (
                                                    y_square2 + 3)) - square_mar_he / 2) - random.randint(-7, 7)),
                                       distortionFrequency=0, tweening=pytweening.easeInOutQuad,
                                       offsetBoundaryY=8, offsetBoundaryX=8, targetPoints=random.randint(30, 40))
                    hc.move((round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                             round(board_pos[1] + (square_mar_he * (y_square2 + 3)) - square_mar_he / 2)),
                            duration=0.05,
                            humanCurve=curve)
                    pyautogui.click()
                else:
                    pyautogui.click(round(board_pos[0] + (square_mar_wi * x_square2) - square_mar_wi / 2),
                                    round(board_pos[1] + (square_mar_he * (y_square2 + 3)) - square_mar_he / 2))
        except:
            pass
        timeused += (time.perf_counter() - starttime)
        timeleft = round(tenminutes - timeused,3)
        print("Time left: ", round(timeleft) // 60, " min, ", round(timeleft) % 60, " sec")
        print("\n\n")

        if board.is_game_over():
            print("Looks like I won again!")
            engine.quit()
            return

if __name__ == "__main__":
    while 1:
        legit = input("Do you want legit mode? (y/n): ")
        if legit != "y" and legit != "n":
            print("Please type y or n.")
            continue
        break
    while 1:
        who = input("Are you playing as white or black?: ")

        if who == "white" or who == "w":
            who = "w"
            other = "b"
            flip = False
            prev_fen = "IDEK"
            break
        elif who == "black" or who == "b":
            who = "b"
            other = "w"
            flip = True
            prev_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
            break

    main(legit, who)