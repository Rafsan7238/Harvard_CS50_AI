"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    if terminal(board):
        return "Game is already over!!"

    else:
        xCount = 0
        oCount = 0

        for i in range(0, 3):
            for j in range(0, 3):

                if board[i][j] == X:
                    xCount += 1
            
                elif board[i][j] == O:
                    oCount += 1
    
        if xCount > oCount:
            return O

        else:
            return X    


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    if terminal(board):
        return None

    else:
        actionSet = set()

        for i in range(0,3):
            for j in range(0,3):

                if board[i][j] == EMPTY:
                    actionSet.add((i,j))

        return actionSet


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY:
        raise ValueError

    else:
        resultBoard = copy.deepcopy(board)
        resultBoard[action[0]][action[1]] = player(board)

        return resultBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #checking rows

    if board[0][0] == board[0][1] and board[0][1] == board[0][2]:
        return board[0][0]

    elif board[1][0] == board[1][1] and board[1][1] == board[1][2]:
        return board[1][0]

    elif board[2][0] == board[2][1] and board[2][1] == board[2][2]:
        return board[2][0]

    #checking columns

    elif board[0][0] == board[1][0] and board[1][0] == board[2][0]:
        return board[0][0]

    elif board[0][1] == board[1][1] and board[1][1] == board[2][1]:
        return board[0][1]

    elif board[0][2] == board[1][2] and board[1][2] == board[2][2]:
        return board[0][2]

    #checking diagonals

    elif board[0][0] == board[1][1] and board[1][1] == board[2][2]:
        return board[0][0]

    elif board[0][2] == board[1][1] and board[1][1] == board[2][0]:
        return board[0][2]

    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    else:
        emptyCount = 0

        for i in range(0, 3):
            for j in range(0, 3):

                if board[i][j] == EMPTY:
                    emptyCount +=1
                    break
        
        if emptyCount == 0:
            return True

        else:
            return False



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        if winner(board) == X:
            return 1
    
        elif winner(board) == O:
            return -1

        else:
            return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    
    if terminal(board):
        return None

    else:
        if player(board) == X:
            utilValue, move = max_value(board)
            return move

        else:
            utilValue, move = min_value(board)
            return move

def max_value(board):
    if terminal(board):
        return utility(board), None

    val = float('-inf')
    move = None

    for action in actions(board):

        tempVal, tempAct = min_value(result(board,action))
        if tempVal > val:
            val = tempVal
            move = action

            if val == 1: 
                return val, move

    return val, move

def min_value(board):
    if terminal(board):
        return utility(board), None

    val = float('inf')
    move = None

    for action in actions(board):

        tempVal, tempAct = max_value(result(board,action))
        if tempVal < val:
            val = tempVal
            move = action

            if val == -1: 
                return val, move

    return val, move