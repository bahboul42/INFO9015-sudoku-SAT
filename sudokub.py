#!/usr/bin/python3

import sys
import subprocess

# reads a sudoku from file
# columns are separated by |, lines by newlines
# Example of a 4x4 sudoku:
# |1| | | |
# | | | |3|
# | | |2| |
# | |2| | |
# spaces and empty lines are ignored
def sudoku_read(filename):
    myfile = open(filename, 'r')
    sudoku = []
    N = 0
    for line in myfile:
        line = line.replace(" ", "")
        if line == "":
            continue
        line = line.split("|")
        if line[0] != '':
            exit("illegal input: every line should start with |\n")
        line = line[1:]
        if line.pop() != '\n':
            exit("illegal input\n")
        if N == 0:
            N = len(line)
            if N != 4 and N != 9 and N != 16 and N != 25:
                exit("illegal input: only size 4, 9, 16 and 25 are supported\n")
        elif N != len(line):
            exit("illegal input: number of columns not invariant\n")
        line = [int(x) if x != '' and int(x) >= 0 and int(x) <= N else 0 for x in line]
        sudoku += [line]
    return sudoku

# print sudoku on stdout
def sudoku_print(myfile, sudoku):
    if sudoku == []:
        myfile.write("impossible sudoku\n")
    N = len(sudoku)
    for line in sudoku:
        myfile.write("|")
        for number in line:
            if N > 9 and number < 10:
                myfile.write(" ")
            myfile.write(" " if number == 0 else str(number))
            myfile.write("|")
        myfile.write("\n")

# get number of constraints for sudoku
def sudoku_constraints_number(sudoku):
    N = len(sudoku)

    count = 4 * (N ** 2) * ( 1 + N * (N - 1) / 2)

    pre_filled_count = sum(1 for line in sudoku for number in line if number > 0)  # Now this should work

    print(count + pre_filled_count)
    return count + pre_filled_count

# prints the generic constraints for sudoku of size N
def sudoku_generic_constraints(myfile, N):

    def output(s):
        myfile.write(s)

    # Notice that the following function only works for N = 4 or N = 9
    def newlit(i,j,k, N=N):
        output(str(i * N + j)+str(k).zfill(2)+ " ")

    def newneglit(i,j,k, N=N):
        output("-"+ str(i * N + j)+str(k).zfill(2)+ " ")

    def newcl():
        output("0\n")

    def newcomment(s):
        output("")

    if N == 4:
        n = 2
    elif N == 9:
        n = 3
    elif N == 16:
        n = 4
    elif N == 25:
        n = 5
    else:
        exit("Only supports size 4, 9, 16 and 25")

    # First, let's ensure that the solver have to fill in every cell with at least a number, ad that it appears at least one 
    # time per column, row, and block

    # each cell contains a number
    for row in range(N):
        for col in range(N):
            for nb in range(1, N + 1):
                # Create the constraint that this number must be in this cell
                newlit(row, col, nb)
            newcl()

    # each column contains every number once
    for col in range(N):
        for nb in range(1, N + 1):
            for row in range(N):
                # Create the constraint that this number must be in this column
                newlit(row, col, nb)
            newcl()
                
    # each row contains every number once
    for row in range(N):
        for nb in range(1, N + 1):
            for col in range(N):
                # Create the constraint that this number must be in this row
                newlit(row, col, nb)
            newcl()

    # each block contains every number once
    for block in range(N):
        # Calculate the starting row and column for this block
        block_row = (block // n) * n
        block_col = (block % n) * n

        # Now iterate over each cell within the block
        for row in range(block_row, block_row + n):
            for col in range(block_col, block_col + n):
                for number in range(1, N + 1):
                    # Create the constraint that this number must be in this block
                    newlit(row, col, number)
                newcl()


    # Now, We need to ensure that every row, col, block has every number at most once
    # each cell contains at most one number
    for row in range(N):
        for col in range(N):
            for nb1 in range(1, N + 1):
                for nb2 in range(nb1 + 1, N + 1):
                    newneglit(row, col, nb1)
                    newneglit(row, col, nb2)
                    newcl()

    # for each line, each number appears at most once
    for row in range(N):
        for nb in range(1, N+1):
            for col1 in range(N):
                for col2 in range(col1 + 1, N):
                    newneglit(row, col1, nb)
                    newneglit(row, col2, nb)
                    newcl()

    # for each column, each number appears at most once
    for col in range(N):
        for nb in range(1, N + 1):
            for row1 in range(N):
                for row2 in range(row1 + 1, N):
                    newneglit(row1, col, nb)
                    newneglit(row2, col, nb)
                    newcl()

# for each block, each number appears at most once
    for block in range(N):
        # Calculate the starting row and column for this block
        block_row = (block // n) * n
        block_col = (block % n) * n

        # Now iterate over each number within the block
        for number in range(1, N + 1):
            # Iterate over each cell within the block
            for row1 in range(block_row, block_row + n):
                for col1 in range(block_col, block_col + n):
                    # Now iterate over each cell again within the block to create pairs
                    for row2 in range(block_row, block_row + n):
                        for col2 in range(block_col, block_col + n):
                            # Ensure we don't compare a cell with itself
                            if row1 == row2 and col1 == col2:
                                continue
                            # Create the constraint that this number cannot be in both cells
                            newneglit(row1, col1, number)
                            newneglit(row2, col2, number)
                            newcl()


def sudoku_specific_constraints(myfile, sudoku):

    N = len(sudoku)

    def output(s):
        myfile.write(s)

    # Fixed
    def newlit(i,j,k, N=N):
        output(str(i * N + j)+str(k).zfill(2)+ " ")

    def newcl():
        output("0\n")

    for i in range(N):
        for j in range(N):
            if sudoku[i][j] > 0:
                newlit(i, j, sudoku[i][j])
                newcl()

def sudoku_other_solution_constraint(myfile, sudoku):

    N = len(sudoku)

    def output(s):
        myfile.write(s)

    def newneglit(i,j,k, N=N):
        output("-" + str(i * N + j)+str(k).zfill(2)+ " ")

    def newcl():
        output("0\n")

    # Added a constraint that tells that at least one of the numbers in the first solution must be different in the other.
    for row in range(N):
        for col in range(N):
                nb = sudoku[row][col]
                newneglit(row, col, nb)
    newcl()
                
def sudoku_solve(filename):
    command = "java -jar org.sat4j.core.jar sudoku.cnf"
    process = subprocess.Popen(command, shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    for line in out.split(b'\n'):
        line = line.decode("utf-8")
        if line == "" or line[0] == 'c':
            continue
        if line[0] == 's':
            if line != 's SATISFIABLE':
                return []
            continue
        if line[0] == 'v':
            line = line[2:]
            units = line.split()
            if units.pop() != '0':
                exit("strange output from SAT solver:" + line + "\n")
            units = [int(x) for x in units if int(x) >= 0]
            N = len(units)
            if N == 16:
                N = 4
            elif N == 81:
                N = 9
            elif N == 256:
                N = 16
            elif N == 625:
                N = 25
            else:
                exit("strange output from SAT solver:" + line + "\n")
            sudoku = [ [0 for i in range(N)] for j in range(N)]
            # Notice that the following function works
            for number in units:
                last_two = number % 100
                first_digits = number // 100

                i = first_digits // N
                j = first_digits % N

                sudoku[i][j] = last_two
            
            return sudoku
        exit("strange output from SAT solver:" + line + "\n")
        return []
    
import random
def sudoku_generate(size):

    if size in [4, 9]:
        health = size*size
    elif size == 16:
        health = size * 4
    else :
        health = 5

    sudoku = [[ 0 for _ in range(size)] for _ in range(size)]

    # First, we need to generate a random solution

    sudoku[random.randint(0, size - 1)][random.randint(0, size - 1)] = random.randint(1, size)
    sudoku_print(sys.stdout, sudoku)

    with open("sudoku.cnf", 'w') as myfile:
        myfile.write("p cnf " + str(size**2) + str(size).zfill(2)  +" "+
                     str(sudoku_constraints_number(sudoku))+"\n")
        sudoku_generic_constraints(myfile, size)
        sudoku_specific_constraints(myfile, sudoku)
    
    sudoku = sudoku_solve("sudoku.cnf")

    sudoku_print(sys.stdout, sudoku)

    print("Solution found, starting to remove numbers...")
    # Now, we need to remove numbers from the solution until it is not unique anymore
    while True:
        # Pick a random number
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)

        nb = sudoku[row][col]


        # If it is already 0, then we can't remove it
        if nb == 0:
            continue

        # Remove the number
        sudoku[row][col] = 0

        with open("sudoku.cnf", 'w') as myfile:
            myfile.write("p cnf " + str(size**2) + str(size).zfill(2)  +" "+
                        str(sudoku_constraints_number(sudoku))+"\n")
            sudoku_generic_constraints(myfile, size)
            sudoku_specific_constraints(myfile, sudoku)

        temp = sudoku_solve("sudoku.cnf")

        with open("sudoku.cnf", 'a') as myfile:
            sudoku_other_solution_constraint(myfile, temp)

        solvable = sudoku_solve(sudoku)

        print("Health: " + str(health))
        if solvable == []:
            continue
        else:
            sudoku[row][col] = nb
            health -= 1

            if health == 0:
                break
        
    return sudoku 
    

def sudoku_generate_cm(size):

    if size in [4, 9]:
        health = size*size
    elif size == 16:
        health = size * 4
    else :
        health = 5

    sudoku = [[ 0 for _ in range(size)] for _ in range(size)]

    # First, we need to generate a random solution

    sudoku[random.randint(0, size - 1)][random.randint(0, size - 1)] = random.randint(1, size)
    sudoku_print(sys.stdout, sudoku)

    with open("sudoku.cnf", 'w') as myfile:
        myfile.write("p cnf " + str(size**2) + str(size).zfill(2)  +" "+
                     str(sudoku_constraints_number(sudoku))+"\n")
        sudoku_generic_constraints(myfile, size)
        sudoku_specific_constraints(myfile, sudoku)
    
    sudoku = sudoku_solve("sudoku.cnf")

    # Remove ever number == size
    for row in range(size):
        for col in range(size):
            if sudoku[row][col] == size:
                sudoku[row][col] = 0

    sudoku_print(sys.stdout, sudoku)

    print("Solution found, starting to remove numbers...")
    # Now, we need to remove numbers from the solution until it is not unique anymore
    while True:
        # Pick a random number
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)

        nb = sudoku[row][col]

        # If it is already 0, then we can't remove it
        if nb == 0:
            continue

        # Remove the number
        sudoku[row][col] = 0

        with open("sudoku.cnf", 'w') as myfile:
            myfile.write("p cnf " + str(size**2) + str(size).zfill(2)  +" "+
                        str(sudoku_constraints_number(sudoku))+"\n")
            sudoku_generic_constraints(myfile, size)
            sudoku_specific_constraints(myfile, sudoku)

        temp = sudoku_solve("sudoku.cnf")

        with open("sudoku.cnf", 'a') as myfile:
            sudoku_other_solution_constraint(myfile, temp)

        solvable = sudoku_solve(sudoku)
        print("Health: " + str(health))
        if solvable == []:
            continue
        else:
            sudoku[row][col] = nb
            health -= 1
            if health == 0:
                break
        
    return sudoku 

from enum import Enum
class Mode(Enum):
    SOLVE = 1
    UNIQUE = 2
    CREATE = 3
    CREATEMIN = 4

OPTIONS = {}
OPTIONS["-s"] = Mode.SOLVE
OPTIONS["-u"] = Mode.UNIQUE
OPTIONS["-c"] = Mode.CREATE
OPTIONS["-cm"] = Mode.CREATEMIN

if len(sys.argv) != 3 or not sys.argv[1] in OPTIONS :
    sys.stdout.write("./sudokub.py <operation> <argument>\n")
    sys.stdout.write("     where <operation> can be -s, -u, -c, -cm\n")
    sys.stdout.write("  ./sudokub.py -s <input>.txt: solves the Sudoku in input, whatever its size\n")
    sys.stdout.write("  ./sudokub.py -u <input>.txt: check the uniqueness of solution for Sudoku in input, whatever its size\n")
    sys.stdout.write("  ./sudokub.py -c <size>: creates a Sudoku of appropriate <size>\n")
    sys.stdout.write("  ./sudokub.py -cm <size>: creates a Sudoku of appropriate <size> using only <size>-1 numbers\n")
    sys.stdout.write("    <size> is either 4, 9, 16, or 25\n")
    exit("Bad arguments\n")

mode = OPTIONS[sys.argv[1]]
if mode == Mode.SOLVE or mode == Mode.UNIQUE:
    filename = str(sys.argv[2])
    sudoku = sudoku_read(filename)
    N = len(sudoku)
    myfile = open("sudoku.cnf", 'w')
    # Notice that this may not be correct for N > 9
    myfile.write("p cnf " + str(N*N) + str(N).zfill(2)  +" "+
                 str(sudoku_constraints_number(sudoku))+"\n")
    sudoku_generic_constraints(myfile, N)
    sudoku_specific_constraints(myfile, sudoku)
    myfile.close()
    sys.stdout.write("sudoku\n")
    sudoku_print(sys.stdout, sudoku)
    sudoku = sudoku_solve("sudoku.cnf")    
    sys.stdout.write("\nsolution\n")
    sudoku_print(sys.stdout, sudoku)
    if sudoku != [] and mode == Mode.UNIQUE:
        myfile = open("sudoku.cnf", 'a')
        sudoku_other_solution_constraint(myfile, sudoku)
        myfile.close()
        sudoku = sudoku_solve("sudoku.cnf")
        if sudoku == []:
            sys.stdout.write("\nsolution is unique\n")
        else:
            sys.stdout.write("\nother solution\n")
            sudoku_print(sys.stdout, sudoku)
elif mode == Mode.CREATE:
    print("Creation mode")
    size = int(sys.argv[2])
    sudoku = sudoku_generate(size)
    sys.stdout.write("\ngenerated sudoku\n")
    sudoku_print(sys.stdout, sudoku)
elif mode == Mode.CREATEMIN:
    size = int(sys.argv[2])
    sudoku = sudoku_generate_cm(size)
    sys.stdout.write("\ngenerated sudoku\n")
    sudoku_print(sys.stdout, sudoku)