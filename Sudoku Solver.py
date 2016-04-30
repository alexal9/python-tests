# Sudoku Solver

from collections import namedtuple, defaultdict
import time
import copy

Cell = namedtuple('Cell', 'box row col val poss')
BOXES = 9
BOXSIZE = 3

def blank():
    '''
    Sets up an initially empty (all values are 0) Sudoku grid where each
    cell is a namedtuple with fields box (each smaller grid), row, col
    (column), corresponding value, and if the Cell doesn't have a value, it
    contains poss, a set of possible values. 
    '''
    result = []
    for i in range(BOXES):
        temp = []
        for j in range(BOXES):
           temp.append( Cell(i//BOXSIZE*BOXSIZE+j//BOXSIZE,
                             i, j, '-', set(range(1,BOXES+1)) ) )
        result.append(temp)
    return result

def inputvals():
    '''
    Asks the user to input valid 3-tuples specifiying row,col,val.
    '''
    result = []
    while True:
        try:
            a = input('Enter 3-tuple row,col,val or quit to stop input: ')
            a = a[:-1] if a[-1] == '\r' else a
            if a.upper() == 'QUIT':
                break
            a = tuple(int(i) for i in a.split(','))
            assert len(a) == 3
            assert all(type(i) == int for i in a)
            result.append(a)
        except:
            print('Not a valid tuple, please re-enter')
    return result

def initval(board: list, values: list):
    '''
    List of values to be added, calls addval
    '''
    for item in values:
        addval(board, item)

def addval(board: list, values: tuple):
    '''
    Given a Sudoku board, and a 3-tuples of (row, col, value),
    assign that cell corresponding to that particular row and column with
    that associated value.
    '''
    row,col,value = values
    if board[row][col].val != '-':
        return
    try:
        assertchecks(board, row, col, value)
        board[row][col] = board[row][col]._replace(val=value, poss = set())
    except:
        print('Cannot add entry', str(values), '; invalid')

def assertchecks(board: list, r: int, c: int, value: int):
    '''
    Asserts that the value to be added in the specified r,c (row, column)
    and consequently corresponding box, does not already contain that value.
    '''
    b = board[r][c].box
    assert value not in getvaluesbox(board, b)
    assert value not in getvaluesrow(board, r)
    assert value not in getvaluescol(board, c)

def getlocations(board: list, value: int):
    '''
    Given a Sudoku 9x9 board, get a locations of all the instances of the
    values in the board into a set of 3-tuples (box, row, col).
    '''
    result = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j].val == value:
                result.add((board[i][j].box, i, j))
    return result

def getvaluesbox(board: list, b: int):
    '''
    Gets all of the values in a given box.
    '''
    result = set()
    for i in range(b//BOXSIZE*BOXSIZE,(b//BOXSIZE+1)*BOXSIZE):
        for j in range(b%BOXSIZE*BOXSIZE,(b%BOXSIZE+1)*BOXSIZE):
            if board[i][j].val != '-':
                result.add(board[i][j].val)
    return result

def getvaluesrow(board: list, r: int):
    '''
    Gets all of the values in a given row.
    '''
    result = set()
    for i in range(BOXES):
        if board[r][i].val != '-':
            result.add(board[r][i].val)
    return result

def getvaluescol(board: list, c: int):
    '''
    Gets all of the values in a given column.
    '''
    result = set()
    for i in range(BOXES):
        if board[i][c].val != '-':
            result.add(board[i][c].val)
    return result

def getpossbox(board: list, r: int, c: int):
    '''
    Gets all of the possible values of all the cells in a given box,
    excluding the current cell in row r and column c.
    '''
    result = set()
    b = board[r][c].box
    for i in range(b//BOXSIZE*BOXSIZE,(b//BOXSIZE+1)*BOXSIZE):
        for j in range(b%BOXSIZE*BOXSIZE,(b%BOXSIZE+1)*BOXSIZE):
            if board[i][j].val == '-' and (i,j) != (r,c):
                result.update(board[i][j].poss)
    return result

def getpossrow(board: list, r: int):
    '''
    Gets all of the possible values of all the cells in a given row,
    excluding the current cell in row r.
    '''
    result = set()
    for i in range(BOXES):
        if board[r][i].val == '-' and i != r:
            result.update(board[r][i].poss)
    return result

def getposscol(board: list, c: int):
    '''
    Gets all of the possible values of all the cells in a given column,
    excluding the current cell in column c.
    '''
    result = set()
    for i in range(BOXES):
        if board[i][c].val == '-' and i != c:
            result.update(board[i][c].poss)
    return result

##################

def pseudoval(board: list, b: int):
    '''
    When a value cannot be explicitly determined (belonging to one particular cell),
    but its value is along either a row or a column, its corresponding row's empty
    cells have that number removed from their set of possibilities.
    '''
    result = {}
    for i in set(range(1,BOXES+1)) - getvaluesbox(board, b):
        temp = []
        breakcount = 0
        for j in range(b//BOXSIZE*BOXSIZE,(b//BOXSIZE+1)*BOXSIZE):
            for k in range(b%BOXSIZE*BOXSIZE,(b%BOXSIZE+1)*BOXSIZE):
                if board[j][k].val == '-' and i in board[j][k].poss:
                    if len(temp) == 3:
                        breakcount += 1
                        temp = []
                        break
                    temp.append( (j,k) )
            if breakcount != 0:
                break
        if temp != [] and any( len(set(i)) == 1 for i in zip(*temp) ):
            result[i] = temp
    return result

def cellwithposs(board: list, values: set):
    '''
    Given a set of possible values, return the first location in which that
    cell also has those same possible values.
    '''
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j].val == '-' and board[i][j].poss == values:
                return (i,j)

def findmostcommonposs(board: list, size: int):
    '''
    Find the possbilities that occur the most often with in the Sudoku board,
    and return a list of lists of length 'size' containing the most common
    possibilities.
    '''
    result = defaultdict(int)
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j].val == '-' and len(board[i][j].poss) == size:
                result[ str(sorted(board[i][j].poss)) ] += 1
    return [eval(key) for key in result if result[key] == max(result.values())]

def makeguess(boardcopy: list, r: int, c: int, value: int):
    '''
    Given a specific cell (specified by r,c for each row and column, respectively),
    and the value to be added, we make a guess and place that value into the cell
    (in a temporary board), and proceed to solve the modified board. Returns True
    if the guess solves the Sudoku, otherwise returns False if the guess fails.
    '''
    count = 0
    currentcount = updatecount = blankcellcount(boardcopy)
    boardcopy[r][c] = boardcopy[r][c]._replace(val = value, poss = set())
    while not any( (boardcopy[i][j].val == '-' and boardcopy[i][j].poss == set())
                   for i in range(len(boardcopy)) for j in range(len(boardcopy)) ):
        updatecount = blankcellcount(boardcopy)
        updateboard(boardcopy)
        if currentcount == 0:
            board = boardcopy
            return True
        if currentcount == updatecount:
            break
        currentcount = updatecount
    return False

###################

def updatecell(board: list, r: int, c: int):
    '''
    Based on which values are already in the row and column (specified by r
    and c), and consequently box, update the possibilities set by removing
    the values contained in that cell's box, row, and column. If no cell
    contains only a single possibility, we use the second method to find
    which cell can only contain one particular value and update that cell
    with that corresponding value.
    '''
    remove = set(getvaluesbox(board, board[r][c].box)) | \
             set(getvaluesrow(board, r)) | set(getvaluescol(board, c))
    board[r][c] = board[r][c]._replace(poss = board[r][c].poss - remove)
    # updates the possibilities set
    if len(board[r][c].poss) == 1:
        board[r][c] = board[r][c]._replace(val = board[r][c].poss.pop(),
                                           poss = set())
        #displayboard(board)
        return
        # if there is only one value in the possibilities set,
        # set the value of that cell to the value in the set
    remaining1 = board[r][c].poss - set(getpossbox(board, r, c))
    remaining2 = board[r][c].poss - set(getpossrow(board, r))
    remaining3 = board[r][c].poss - set(getposscol(board, c))
    for i in (remaining1, remaining2, remaining3):
        if len(i) == 1:
            board[r][c] = board[r][c]._replace(val = i.pop(), poss = set())
            #print('Second condition')
            #displayboard(board)
    # for each possible remaining set (either from box, row, or column),
    # if there is only one possible value in the remaining set,
    # set the value of that cell to that corresponding value

def updateposs(board: list):
    '''
    Updates the possibilites of either a row or column determined by the pseudoval
    method to reduce the number of possibilities based on implied number positioning.
    '''
    for i in range(len(board)):
        for num, poss in pseudoval(board, i).items():
            temp = list(zip(*poss))
            if len(set(temp[0])) == 1: # expand along row
                r = set(temp[0]).pop()
                for j in range(len(board)):
                    if board[r][j].val == '-' and board[r][j].box != i:
                        newposs = board[r][j].poss - {num}
                        board[r][j] = board[r][j]._replace(poss = newposs)
            elif len(set(temp[1])) == 1: # expand along column
                c = set(temp[1]).pop()
                for j in range(len(board)):
                    if board[j][c].val == '-' and board[j][c].box != i:
                        newposs = board[j][c].poss - {num}
                        board[j][c] = board[j][c]._replace(poss = newposs)

def updateboard(board: list):
    '''
    Updates every blank cell in the Sudoku board using the updatecell method
    to determine values for other cells. 
    '''
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j].val == '-':
                updatecell(board, i, j)    

def blankcellcount(board: list):
    '''
    Returns the number of blank cells (values that are '-')
    '''
    result = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j].val == '-':
                result += 1
    return result

def displayboard(board: list):
    '''
    Displays the Sudoku game board.
    '''
    print()
    print('-'*( (BOXES+BOXSIZE+1)*3-2) )
    for i in range(len(board)):
        print('| ', end=' ')
        for j in range(len(board[i])):
            print('{:<2}'.format(board[i][j].val), end=' ')
            if (j+1)%BOXSIZE == 0:
                print('| ', end=' ')
        print()
        if (i+1)%BOXSIZE == 0:
            print('-'*( (BOXES+BOXSIZE+1)*3-2) )
    print()

def game(board: list):
    '''
    Runs the game.
    '''
    currentcount = updatecount = blankcellcount(board)
    count = guesscount = 0
    size = 2
    while True:
        updateboard(board)
        updatecount = blankcellcount(board)
        if currentcount == 0:
            print('Sudoku solved!')
            break
        if currentcount == updatecount:
            if count > 1:
                ####
                common = findmostcommonposs(board, size)
                r, c = cellwithposs(board, set(common[0]))
                while common != []:
                    boardcopy = copy.deepcopy(board)
                    a = common[0]
                    value = a[0]
                    #print(common, a, r, c, value)
                    if not makeguess(boardcopy, r, c, value):
                        a.pop(0) # remove the first entry in the first nested list
                        if a == []:
                            common.pop(0) # remove the first element
                            if common == []:
                                size += 1
                                if size > 8:
                                    print('Guesses failed')
                                    return board
                                #print(size)
                                common = findmostcommonposs(board, size)
                                # increase the size and find the most common
                                # possibilities of that size
                            r, c = cellwithposs(board, set(common[0]))
                    else:
                        board = boardcopy
                        break
                ####
                # adding a size parameter makes the find most common restriction
                # seem pointless since you can just loop through everything of size
                # 2 and then continue on, however it appears that limiting the
                # results to those that occur the most often makes the code
                # more efficient, and the runtime faster. 
            updateposs(board)
            count += 1
        currentcount = updatecount
    return board

if __name__ == '__main__':
    board = blank()
    inputs = inputvals()
    initval(board, inputs)
    #initval9x9(board, [(0,0,3),(1,4,3),(0,5,2),(5,0,9),(0,1,4),(1,1,5),(2,5,8),(5,7,3)])
    displayboard(board)
    start = time.time()
    board = game(board)
    displayboard(board)
    end = time.time()
    print(end-start)
