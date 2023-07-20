import sys

comp_binary = { '0' : '0101010', '1' : '0111111', '-1' :  '0111010', 'D' :  '0001100', 'A' : '0110000', 'M' : '1110000', '!D' : 
               '0001101', '!A' : '0110001', '!M' : '1110001', '-D' : '0001111', '-A' : '0110011', '-M' : '1110011', 'D+1' : '0011111', '1+D' : 
               '0011111', 'A+1' : '0110111', '1+A' : '0110111', 'M+1' : '1110111', '1+M' : '1110111', 'D-1' : '0001110', 'A-1' : '0110010', 'M-1' : 
               '1110010', 'D+A' : '0000010', 'A+D' : '0000010', 'D+M' : '1000010', 'M+D' : '1000010', 'D-A' : '0010011', 'D-M' : '1010011', 'A-D' : 
               '0000111', 'M-D' : '1000111', 'D&A' : '0000000', 'A&D' : '0000000', 'D&M' : '1000000', 'M&D' : '1000000', 'D|A' : '0010101', 'A|D' : 
               '0010101', 'D|M' : '1010101', 'M|D' : '1010101' }

dest_binary = { 'null' : '000', 'M' : '001', 'D' : '010', 'DM' : '011','A' : '100', 'AM' : '101', 'AD' : '110', 'ADM' : '111'}

jump_binary = { 'null' : '000', 'JGT' : '001', 'JEQ' : '010', 'JGE' : '011', 'JLT' : '100', 'JNE' : '101', 'JLE' : '110', 'JMP' : '111'}

symbols = {
         "R0" :  "0",
         "R1" :  "1",
         "R2" :  "2",
         "R3" :  "3",
         "R4" :  "4",
         "R5" :  "5",
         "R6" :  "6",
         "R7" :  "7",
         "R8" :  "8",
         "R9" :  "9",
         "R10" :  "10",
         "R11" :  "11",
         "R12" :  "12",
         "R13" :  "13",
         "R14" :  "14",
         "R15" :  "15",
         "SCREEN" : "16384",
         "KBD" :  "24576"
}
        
def dest2bin(mnemonic):
    # returns the binary code for the destination part of a C-instruction
     return dest_binary[mnemonic]

def comp2bin(mnemonic):
    # returns the binary code for the comp part of a C-instruction
   return comp_binary[mnemonic]

def jump2bin(mnemonic):
    # returns the binary code for the jump part of a C-instruction
    return jump_binary.get(mnemonic)
    
def commandType(command):
    # returns "A_COMMAND", "C_COMMAND", or "L_COMMAND"
    # depending on the contents of the 'command' string
    if command.count('@') == 1:
        return "A_COMMAND"
    elif command.count('(') == 1:
        return "L_COMMAND"
    else:
        return "C_COMMAND"

def getSymbol(command):
    # given an A_COMMAND or L_COMMAND type, returns the symbol as a string,
    # eg (XXX) returns 'XXX'
    # @sum returns 'sum'
    if command.count('@') == 1:
        return command.split('@')[1]
    else:
        return command.split('(')[1].split(')')[0]
    
def getDest(command):
    # return the dest mnemonic in the C-instruction 'commmand'
    if command.count('=') == 1:
        return command.split('=')[0]
    else: 
        return "null"

def getComp(command):
    # return the comp mnemonic in the C-instruction 'commmand'
    hasEQ = False
    hasSC = False

    if command.count('=') == 1: 
        hasEQ = True
    
    if command.count(';') == 1:
        hasSC = True

    if hasEQ & hasSC:
        return (command.split('=')[1].split(';')[0])
    elif hasEQ:
        return (command.split('=')[1])
    elif hasSC:
        return (command.split(';')[0])
    else:
	    return (command)

def getJump(command):
    # return the jump mnemonic in the C-instruction 'commmand'
    if command.count(';') == 1:
        return command.split(';')[1]
    else:
        return ("null")

######################   
###    NEW STUF    ###
###################### 

def processA(line, lineNo, nextRAM):
    # Convert an A-instruction line of assmebly to a binary code that is 
    # 0 followed by a 15 bit address. Will use the symbol table to lookup
    # a symbol and replace it with a value. If label is not is symbol table
    # add it with correct RAM address (next in sequence)
    # Note: mini-format langauge is helpful
    sym = getSymbol(line)
    
    for key in symbols:
        if symbols[key] == sym:
            sym = key

    if symbols[sym] == False:
        symbols[sym] = str(nextRAM)
    
    # convert to binary
    return '{0:016b}'.format(int(symbols[sym]))

def processC(line):
    # Convert a C-instruction line of code to the correct computation,destination, 
    # and jump binary codes. These should be preceded by 111, which signifies the
    # C-instruction
    part1 = comp2bin(getComp(line))
    part2 = dest2bin(getDest(line))
    part3 = jump2bin(getJump(line))
    return "111" + part1 + part2 + part3

def processL(line, lineNo):
    # When an L-Instruction (label in the form (LABEL)) is encountered, 
    # the label should be placed into the symbol table with the correct line
    x = getSymbol(line)
    symbols[x] = int(lineNo)

def pass_1(lines):
    # scan each line of file and find L_COMMANDS
    # place them in the symbol table with appropriate ROM numbers
    # initialize ROM to 1
    lineNum = 0

    for line in lines:
        if commandType(line) == "L_COMMAND":
            processL(line, lineNum)
        else:
            lineNum += 1

def pass_2(lines):
    # Scan lines and write correct binary code to stdout.
    # initialize RAM to 16. Increase if new symbol encountered
    nextRAM = 16
    lineCount = 0

    outData = []

    for line in lines:
        type = commandType(line)
        
        if type == 'A_COMMAND':
            sym = getSymbol(line)
            if sym in symbols:
                nextRAM += 1
            outData.append(processA(line, lineCount, nextRAM))

        elif type == 'C_COMMAND':
            outData.append(processC(line))
    
    lineCount += 1

    return outData


    
def main():
    # open the file and pass it off to pass_1 and pass_2
    # place any other error checking here.
    input = sys.argv
    if (len(sys.argv) != 2): raise Exception("Only one input file is acceptable")
    fileName = sys.argv[1]
    if fileName.endswith(".asm") == False: raise Exception("Incorrect input file type.")
    file = open(fileName, "r")

    # create array to hold actual lines of code
    lines = []

    for line in file:
        x = line.split("//")[0].strip()
    
        if x.startswith("//") == False and len(x) != 0:
            lines.append(x)

    # write to .hack file
    outName = fileName.split(".")[0]
    sys.stdout = open(outName + '.hack','wt')

    # pass the array to pass1 and pass2
    pass_1(lines)
    data = pass_2(lines)

    for element in data:
        print(element)

if __name__ == "__main__":
    main()

