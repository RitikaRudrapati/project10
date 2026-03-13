#-----------------------------lexer design------------------------------#

#this list will store all the toxers my design will find 
tokens = []

#still have to check for comments 
#still have to edit keywords 
#still have to 

#these lists contain jack allowed keywords, operators, or symbols 
keywords = ['int', 'float', 'if', 'else', 'while', 'for', 'return']
operators = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=']
symbols = ['(', ')', '{', '}', ';', ',']

def lexer(file):
    #read the file as one big string
    with open(file, 'r') as f:
        code = f.read()

    #start as an empty token and build it up char by char
    currentToken = ''

    #loop through every char
    for char in code:

        #check if the char is a letter, number, or an underscore
        if char.isalnum() or char == "_":
            currentToken += char

        # whitespace means token ended
        elif char.isspace():
            if currentToken != "":
                #decide if the token is a keyword, identifier, or integer constant
                classify(currentToken, tokens)
                #reset the current token for the next one
                currentToken = ""

        # symbol encountered
        elif char in symbols:
            if currentToken != "":
                classify(currentToken, tokens)
                currentToken = ""

            tokens.append(("symbol", char))

    # last token at end of file
    if currentToken != "":
        classify(currentToken, tokens)

    return tokens

#classify the token as a keyword, identifier, or integer constant and add it to the tokens list            
def classify(word, tokens):

    if word in keywords:
        tokens.append(("keyword", word))
    elif word.isdigit():
        tokens.append(("integerConstant", word))
    else:
        tokens.append(("identifier", word))


#------------------parser--------------#

def parser(tokens):
    #this will be the list of parsed tokens 
    parsedTokens = []

def advance(tokens):
    if tokens:
        return tokens.pop(0)
    else:
        return None   
    
def tokenType(token):
    if token:
        return token[0]
    else:
        return None

def findKeyword(token):
    if token and token[0] == "keyword":
        return token[1]
    else:
        return None

def printClassTag(indentifer):
    print("<class>")
    print("<keyword> class </keyword>")
    print("<identifier>" + indentifer + "</identifier>")

def printSymbolTag(symbol):
    print("<symbol>" + symbol + "</symbol>")

def printClassVarDecTag():
    print("<classVarDec>")
    print("</classVarDec>")

def compileClass():
    if tokenType(advance(tokens)) == "keyword" and findKeyword(tokens[0]) == "class":

        if tokenType(advance(tokens)) == "identifier":
            printClassTag(tokens[1][1])

            if tokenType(advance(tokens)) == "symbol" and tokens[0][1] == "{":
                printSymbolTag(tokens[0][1])

                if tokenType(advance(tokens)) == "symbol" and tokens[0][1] == "}":
                    printSymbolTag(tokens[0][1])
                #check for class var dec and subroutine dec here
                if advance(tokens) is not None:
                    compileClassVarDec()
                    

            else:
                print("Syntax error: expected '{' symbol")
    else:
        print("Syntax error: expected 'class' keyword")

def compileClassVarDec():
    if tokenType(advance(tokens)) == "keyword" and findKeyword(tokens[0]) in ["static", "field"]:
        if tokenType(advance(tokens)) == "int" or tokenType(advance(tokens)) == "char" or tokenType(advance(tokens)) == "boolean" or tokenType(advance(tokens)) == "identifier":
            if tokenType(advance(tokens)) == "symbol" and tokens[0][1] == ";":
                printClassVarDecTag()
            elif tokenType(advance(tokens)) == "symbol" and tokens[0][1] == ",":
                #do i call class var dec again here? 
                printClassVarDecTag()
            
    return

def compileSubroutineDec():
    return

def compileParameterList():
    return

def compileSubroutineBody():
    return

def compileVarDec():
    return

def compileStatements():
    return

#------------------main function------------------#





