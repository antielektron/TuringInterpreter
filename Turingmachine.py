#!/usr/bin/env python3
import numpy as np
import sys
import time

# Bezeichnungen:
# delta     = Zustandsübergangsfunktion: eine Liste von Tupeln im Format: 
#           (aktuellerZustand, aktuelleZeichen[Tupel], nächsterZustand, zuSchreibendeZeichen[Tupel], orientation[Tupel])
# q0        = Startzustand
# F         = Menge der Endzustände

#ein paar konstanten:
GO_LEFT                 = -1
GO_NOWHERE              = 0
GO_RIGHT                = 1

#zur vereinfachung: konstanten für indices in delta:
DELTA_CURRENT_STATE     = 0
DELTA_CURRENT_CHARS     = 1
DELTA_NEXT_STATE        = 2
DELTA_NEXT_CHARS        = 3
DELTA_ORIENTATIONS      = 4

#Konstanten für die Ausgabe:
CURSOR_UP_ONE           = '\x1b[1A'
ERASE_LINE              = '\x1b[2K'

#hilfsfunktionen für die ausgabe:
def eraseLines(n):
    for i in range(n):
        print(CURSOR_UP_ONE + ERASE_LINE, end = "")

#und die eigentliche Turingmaschine:
class Turingmachine(object):
    def __init__(self,delta, q0, F, n, inputStr):
        self.delta = delta
        self.q0 = q0
        self.F = F

        self.n = n

        #zur internen Verwaltung der Turinmaschine brauchen wir folgendes:
        self.stripes = []
        self.positions = []
        
        self.steps = 0 #counting the steps

        for i in range(n):
            self.stripes.append(['$'])
            self.positions.append(0)

        #schreibe unsere Eingabe auf das erste Band:
        for c in inputStr:
            self.stripes[0].append(c)

        self.currentQ = q0
        self.error = False
        self.isInFinalState = False

        self.firstPrint = True

    # Lese char unter dem i-ten Lesekopf:
    def readChar(self,i):

        #erweitere Band, falls notwendig:
        if len(self.stripes[i]) <= self.positions[i]:
            self.stripes[i].append('_')

        #und Zeichen zurückgeben:
        return self.stripes[i][self.positions[i]]

    # Schreibe char unter dem i-ten Lesekopf:
    def writeChar(self,i, char):

        #erweitere Band, falls notwendig:
        if len(self.stripes[i]) <= self.positions[i]:
            self.stripes[i].append('_')

        #und setze Zeichen:
        self.stripes[i][self.positions[i]] = char

    #bewege den Lese-/Schreibkopf
    def move(self, i, orientation):
        self.positions[i] += orientation

    #führe einen Zustandsübergang aus: (gibt true bei erfolg zurück, sonst false)
    def runDelta(self):

        #durchlaufe alle Übergänge in Delta
        for d in self.delta:

            #suche nach Übergängen für unseren Zustand:
            if d[DELTA_CURRENT_STATE] == self.currentQ:

                #prüfe Einganszeichen:
                qInputChars = d[DELTA_CURRENT_CHARS]
                isInputOK = True
                for i in range(self.n):
                    if not ((qInputChars[i] == self.readChar(i)) or (qInputChars[i] == '*')):
                        #eingangszeichen stimmen nicht überein!
                        isInputOK = False

                if isInputOK:
                    #jetzt haben wir den richtigen zustandsübergang gefunden!
                    qNextChars = d[DELTA_NEXT_CHARS]
                    qOrientations = d[DELTA_ORIENTATIONS]
                    for i in range(self.n):
                        #schreibe Zeichen:
                        if qNextChars[i] != '*':
                            self.writeChar(i, qNextChars[i])
                        #Bewege Lese-/Schreibkopf
                        self.move(i, qOrientations[i])

                        #prüfe auf underflows:
                        for j in range(self.n):
                            if self.positions[j] < 0:
                                return False

                    #setze nächsten Zustand:
                    self.currentQ = d[DELTA_NEXT_STATE]
                    self.steps+=1

                    #fertig!
                    return True

        #wenn wir bis hierhin kommen, haben wir keinen Übergang gefunden!
        return False

    # mache einen einzelnen Schritt mit der Turing Maschine (gibt true bei erfolg zurück, sonst false)
    def step(self):
        #führe den Schritt nuraus, wenn wir noch nicht im Endzustand sind:
        if not self.isInFinalState:
            self.error = not self.runDelta()

            #schaue, ob wir in einem Endzustand sind:
            self.isInFinalState = (self.currentQ in self.F)

            return self.error
        return True

    def printMachine(self):
        if not self.firstPrint:
            #Lösche voherige Ausgabe:
            eraseLines(2 * self.n + 1)
        self.firstPrint = False
        #geben bänder aus:
        for i in range(self.n):
            print("[",end="")
            for c in self.stripes[i]:
                print(c,end = "")
            print("]")
            #drucke lese-/Schreibkopf
            print (" " * (self.positions[i] +1) + "^")

        #und gebe allgemeine Infos aus:
        print("step:  " + str(self.steps) + "\t currentState: " + str(self.currentQ))

    #run the machine until it gets to a final state:
    def run(self, delayInSeconds):
        while not self.isInFinalState:
            self.step()
            self.printMachine()
            if self.error:
                print("ERROR! Please check your Turing Program") #TODO: aussagekräftigere Fehlermeldung?
                break
            time.sleep(delayInSeconds)
        if not self.error:
            self.printMachine()
            print("Maschine terminatet!")

if __name__ == "__main__":

    #Blatt13/Aufgabe01 zum testen:

    F = ['finalState']
    d = [('start',"$$$$",'init',"$$$$",(1,1,1,1)),
        ('init',"****",'a',"*!!!",(0,1,1,1)),
        ('a',"a***",'a',"aa**",(1,1,0,0)),
        ('a',"b***",'b',"b***",(0,0,0,0)),
        ('b',"b***",'b',"b*b*",(1,0,1,0)),
        ('b',"c***",'c',"c***",(0,0,0,0)),
        ('c',"c***",'c',"c**c",(1,0,0,1)),
        ('c',"_***",'counting',"_***",(-1,-1,-1,-1)),
        ('counting',"*abc",'counting',"*abc",(0,-1,-1,-1)),
        ('counting',"*!**",'checkCounter',"*!**",(0,0,0,0)),
        ('counting',"**!*",'checkCounter',"**!*",(0,0,0,0)),
        ('counting',"***!",'checkCounter',"***!",(0,0,0,0)),
        ('checkCounter','*!!!','wordAccepted','*!!!',(0,0,0,0)),
        ('checkCounter','****','wordNotAccepted','****',(0,0,0,0)),
        ('wordAccepted','$***','write1','$***',(1,0,0,0)),
        ('wordAccepted','****','wordAccepted','_***',(-1,0,0,0)),
        ('wordNotAccepted','$***','write0','$***',(1,0,0,0)),
        ('wordNotAccepted','****','wordNotAccepted','_***',(-1,0,0,0)),
        ('write0','****','finalState','0***',(0,0,0,0)),
        ('write1','****','finalState','1***',(0,0,0,0))
        ]

    tm = Turingmachine(d, 'start', F, 4, "aaaaaaaaabbbbbbbbbccccccccc")

    tm.run(0.15)
