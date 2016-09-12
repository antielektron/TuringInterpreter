#!/usr/bin/env python3
from Turingmachine import *
import sys

def getLinesFromFile(filename):
    content = []
    with open(filename, "r") as f:
        content = f.read().splitlines()

    return content

def createTuringmachineFromLines(lineArray, userInput):
    k = None
    F = None
    S = None
    I = None

    inputStr = userInput

    d = []

    lineCounter = 0

    for line in lineArray:
        lineCounter += 1

        line = line.replace(" ","")

        if len(line) > 0:
            if line[0] == 'k' and line[-1] == ';':
                #hole k:
                l = line[1:-1]      #entferne k und ;
                kStr = l.replace("=","")  #entferne whitespaces und =
                k = int(kStr)

            elif line[0] == 'F' and line[-1] == ';':
                #hole Endzustände:
                l = line[1:-1]      #entferne F und ;
                FStr = l.replace("=","")  #entferne whitespaces und =
                F = FStr.split(",")

            elif line[0] == 'S' and line[-1] == ';':
                #hole Startzustand:
                l = line[1:-1]      #entferne S und ;
                S = l.replace("=","")  #entferne whitespaces und =
            elif line[0] == 'I' and line[-1] == ';':
                #hole Input:
                l = line[1:-1]      #entferne S und ;
                I = l.replace("=","")  #entferne whitespaces und =
            elif line[0] == '$' and line[-1] == ';':
                #hole Zustandsübergang:
                l = line[1:-1]      #entferne $ und ;
                tmp = l.replace("=","")  #entferne whitespaces und =
                splittedLine = tmp.split(",")

                #parse orientations:
                orientations = []
                for i in range(len(splittedLine[4])):
                    if splittedLine[4][i] == 'l':
                        orientations.append (-1)
                    elif splittedLine[4][i] == 'r':
                        orientations.append (1)
                    elif splittedLine[4][i] == 'n':
                        orientations.append (0)
                    else:
                        print("ERROR in line " + str(lineCounter) + ": " + line)
                        return None
                d.append((splittedLine[0],splittedLine[1],splittedLine[2],splittedLine[3],orientations))

            elif line[0] == '#':
                #bei Kommentaren tu nix
                None
            else: 
                print("ERROR in line " + str(lineCounter) + ": " + line)
                return None

    if k is None:
        print("ERROR: no k defined in Turing Program!")
        return None
    if F is None:
        print("ERROR: no F defined in Turing Program!")
        return None
    if S is None:
        print("ERROR: no S defined in Turing Program!")
        return None

    if inputStr is None:
        if I is None:
            print("WARNING: there is no input string defined. Machine will use an empty input string")
            inputStr = ""
        else:
            inputStr = I



    return Turingmachine(d, S, F, k, inputStr)

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except:
        print("ERROR: no input file. \n"
            + "usage: python TuringInterpreter.py [TuringProgramFile] [InputString] [SleepTimePerStep] \n"
            + "(Default value for SleepTimePerStep is 0.3)")
        sys.exit(0)

    try:
        inputStr = sys.argv[2]
    except:
        inputStr = None

    try:
        sleepTime = float(sys.argv[3])
    except:
        sleepTime = 0.3

    tm = createTuringmachineFromLines(getLinesFromFile(filename), inputStr)

    if tm is None:
        print("ERROR: Bad Program!")
        sys.exit(0)

    tm.run(sleepTime)


