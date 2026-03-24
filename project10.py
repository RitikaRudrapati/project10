
import os
import sys

#-----------------------------lexer design------------------------------#

tokens = []


#these lists contain jack allowed keywords, operators, or symbols 
keywords = [
    'class', 'constructor', 'function', 'method', 
    'field', 'static', 'var', 'int', 'char', 
    'boolean', 'void', 'true', 'false', 'null', 
    'this', 'let', 'do', 'if', 'else', 
    'while', 'return'
]

operators = ['+', '-', '*', '/', '&', '|', '<', '>', '=']

symbols = [
    '{', '}', '(', ')', '[', ']', 
    '.', ',', ';', '+', '-', '*', 
    '/', '&', '|', '<', '>', '=', '~'
]


def lexer(chars):

    while chars:

        char = advanceChar(chars)

        #check to see if it is a digit

        if char == '/':
            if peekChar(chars) == '/':
                # single line comment
                while peekChar(chars) and peekChar(chars) != '\n':
                    advanceChar(chars)
            elif peekChar(chars) == '*':
                # multi line comment
                advanceChar(chars)  # consume the '*'
                while chars:
                    c = advanceChar(chars)
                    if c == '*' and peekChar(chars) == '/':
                        advanceChar(chars)  # consume closing '/'
                        break
            else:
                # division symbol
                appendToken("symbol", '/') 

        elif char.isdigit():
            digit = char

            #keep consuming the characters until it is no longer a digit anymore
            while peekChar(chars) and peekChar(chars).isdigit():
                digit += advanceChar(chars)

            #append the integer constant token to the list of tokens
            appendToken("integerConstant", digit)

        elif char.isalpha() or char == "_":
            word = char 

            #keep consuming the characters until it is no longer a letter, digit, or underscore
            while peekChar(chars) and (peekChar(chars).isalpha() or peekChar(chars).isdigit() or peekChar(chars) == "_"):
                word += advanceChar(chars)

            if word in keywords:
                #append the keyword token to the list of tokens
                appendToken("keyword", word)
            else:
                appendToken("identifier", word)

        elif char == '"':
            stringConstant = ""

            #keep consuming the characters until we find the closing double quote
            while peekChar(chars) and peekChar(chars) != '"':
                stringConstant += advanceChar(chars)

            #consume the closing double quote
            advanceChar(chars)

            #append the string constant token to the list of tokens
            appendToken("stringConstant", stringConstant)
        
        elif char in symbols:
            appendToken("symbol", char)

        elif char.isspace():
            continue

    
    return tokens
        
def createCharLits(file):
    chars = []
    for line in file:
        for char in line:
            chars.append(char)
    return chars

def advanceChar(chars):
    if chars:
        return chars.pop(0)
    else:
        return None
    
def peekChar(chars):
    if chars:
        return chars[0]
    else:
        return None

def appendToken(tokenType, tokenValue):
    tokens.append((tokenType, tokenValue))


#------------------parser--------------#

def advance(tokens):
    if tokens:
        return tokens.pop(0)
    else:
        return None   
    
def peek(tokens):
    if tokens:
        return tokens[0]
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
    printKeyword("class")
    printIdentifier(indentifer)

def printSymbolTag(symbol):
    print("<symbol>" + symbol + "</symbol>")

def printClassVarDecTag():
    print("<classVarDec>")
    print("</classVarDec>")

def printKeyword(keyword):
    print("<keyword>" + keyword + "</keyword>")

def printIdentifier(identifier):
    print("<identifier>" + identifier + "</identifier>")

def compileClass():
    # advance and check for 'class' keyword
    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] == "class":
        # advance and check for class name (identifier)
        token = advance(tokens)
        if token and token[0] == "identifier":
            printClassTag(token[1])
        else:
            print("Syntax error: expected class name")
            return
    else:
        print("Syntax error: expected 'class' keyword")
        return    

    # advance and check for '{'
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "{":
        printSymbolTag("{")
    else:
        print("Syntax error: expected '{'")
        return

    # use peek to keep compiling classVarDecs as long as it is static or feild
    while peek(tokens) and peek(tokens)[1] in ["static", "field"]:
        compileClassVarDec()
    
    # use peek to keep compiling subroutines as long as next token is 'constructor', 'function', or 'method'
    while peek(tokens) and peek(tokens)[1] in ["constructor", "function", "method"]:
        compileSubroutineDec(peek(tokens)[1])
        
    # expect closing '}'
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "}":
        printSymbolTag("}")
    else:
        print("Syntax error: expected '}'")
        return

    print("</class>")

def compileClassVarDec():
    print("<classVarDec>")

    # expect 'static' or 'field'
    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] in ["static", "field"]:
        printKeyword(token[1])
    else:
        print("Syntax error: expected 'static' or 'field'")
        return

    # expect a type
    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
        printKeyword(token[1])
    elif token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected an int, char, boolean, or class type")
        return

    # expect first varName
    token = advance(tokens)
    if token and token[0] == "identifier":
        print("<identifier> " + token[1] + " </identifier>")
    else:
        print("Syntax error: expected varName")
        return

    # use peek to check for ',' or ';'
    while peek(tokens) and peek(tokens)[1] == ",":
        advance(tokens)  # consume the ','
        printSymbolTag(",")
        token = advance(tokens)
        if token and token[0] == "identifier":
            printIdentifier(token[1])
        else:
            print("Syntax error: expected variable name after ','")
            return

    # expect ';'
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return

    print("</classVarDec>")


def compileSubroutineDec(keyword):
    print("<subroutineDec>")

    advance(tokens)
    
    printKeyword(keyword)

    token = advance(tokens)

    if token and token[0] == "keyword" and token[1] in ["void", "int", "char", "boolean"]:
        printKeyword(token[1])
    elif token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected return type")
        return

    token = advance(tokens)
    #should find a subroutine name (identifier)
    if token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected subroutine name")
        return
    
    compileParameterList()
    compileSubroutineBody()
    
    print("</subroutineDec>")

def compileParameterList():
    #should find a '(' symbol
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "(":
        printSymbolTag("(")
    else:
        print("Syntax error: expected '('")
        return
    
    print("<parameterList>")

    #expect a parameter list 

    # if next token is not ')' then we have parameters
    if peek(tokens) and peek(tokens)[1] != ")":
        # expect a type
        token = advance(tokens)
        if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
            printKeyword(token[1])
        elif token and token[0] == "identifier":
            printIdentifier(token[1])
        else:
            print("Syntax error: expected type")
            return
        
        # expect a varName
        token = advance(tokens)
        if token and token[0] == "identifier":
            printIdentifier(token[1])
        else:
            print("Syntax error: expected parameter name")
            return

        # handle additional parameters (',' type varName)*
        while peek(tokens) and peek(tokens)[1] == ",":
            advance(tokens)  # consume ','
            printSymbolTag(",")
            
            token = advance(tokens)
            if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
                printKeyword(token[1])
            elif token and token[0] == "identifier":
                printIdentifier(token[1])
            else:
                print("Syntax error: expected parameter type after ','")
                return
            
            token = advance(tokens)
            if token and token[0] == "identifier":
                printIdentifier(token[1])
            else:
                print("Syntax error: expected parameter name after ','")
                return
            
    print("</parameterList>")

    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == ")":
        printSymbolTag(")")
    else:
        print("Syntax error: expected ')'")
        return
    
#done
def compileSubroutineBody():
    print("<subroutineBody>")

    #should find a '{' symbol
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "{":
        printSymbolTag("{")
    else:
        print("Syntax error: expected {'")
        return
    
    #expect varDecs
    while peek(tokens) and peek(tokens)[1] == "var":
        compileVarDec()
    
    
    compileStatements()

    #should find a '}' symbol
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "}":
        printSymbolTag("}")
    else:
        print("Syntax error: expected }'")
        return
    
    print("</subroutineBody>")


#done
def compileVarDec():
    print("<varDec>")

    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] == "var":
        printKeyword("var")
    else:
        print("Syntax error: expected 'var'")
        return

    token = advance(tokens)

    if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
        printKeyword(token[1])
    elif token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected an int, char, boolean, or class type")
        return
    
    token = advance(tokens)

    if token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected varName")
        return
    
    # use peek to check for ',' or ';'
    while peek(tokens) and peek(tokens)[1] == ",":
        advance(tokens)  # consume the ','
        printSymbolTag(",")
        token = advance(tokens)
        if token and token[0] == "identifier":
            printIdentifier(token[1])
        else:
            print("Syntax error: expected variable name after ','")
            return

    # expect ';'
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return
    
    print("</varDec>")


#--------------------------------statements-----------------------------#

def compileStatements():
    token = peek(tokens)
    print("<statements>")

    while token and token[0] == "keyword" and token[1] in ["let", "if", "while", "do", "return"]:
        token = peek(tokens)
        if token[1] == "let":
            compileLet()
        elif token[1] == "if":
            compileIf()
        elif token[1] == "while":
            compileWhile()
        elif token[1] == "do":
            compileDo()
        elif token[1] == "return":
            compileReturn()
        else:
            print("Syntax error: expected statement")
            return
    
    print("</statements>")
    
    return

def compileLet():
    print("<letStatement>")
    
    if advance(tokens)[1] == "let":
        printKeyword("let")
        token = advance(tokens)
    else:
        print("Syntax error: expected 'let'")
        return
    
    
    if token and token[0] == "identifier":
        printIdentifier(token[1])
    else:
        print("Syntax error: expected varName")
        return
    
    while peek(tokens) and peek(tokens)[1] == "[":
        advance(tokens) 
        printSymbolTag("[")
        compileExpression()
        if advance(tokens)[1] == "]":
            printSymbolTag("]")
        else:
            print("Syntax error: expected ']'")
            return
        
    if advance(tokens)[1] == "=":
        printSymbolTag("=")
        compileExpression()
    else:
        print("Syntax error: expected '='")
        return
    
    if advance(tokens)[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return
    
    print("</letStatement>")

def compileIf():
    print("<ifStatement>")
    if advance(tokens)[1] == "if":
        printKeyword("if")
    else:
        print("Syntax error: expected 'if'")
        return

    if advance(tokens)[1] == "(":
        printSymbolTag("(")
        compileExpression()
        if advance(tokens)[1] == ")":
            printSymbolTag(")")
        else:
            print("Syntax error: expected ')'")
            return
    else:
        print("Syntax error: expected '('")
        return
    
    if advance(tokens)[1] == "{":
        printSymbolTag("{")
        compileStatements()
        if advance(tokens)[1] == "}":
            printSymbolTag("}")
        else:
            print("Syntax error: expected '}'")
            return
    else:
        print("Syntax error: expected '{'")
        return
    
    
    while peek(tokens) and peek(tokens)[1] == "else":
        advance(tokens)
        printKeyword("else")

        if advance(tokens)[1] == "{":
            printSymbolTag("{")
            compileStatements()
        else:
            print("Syntax error: expected '{'")
            return
    
        if advance(tokens)[1] == "}":
            printSymbolTag("}")
        else:
            print("Syntax error: expected '}'")
            return
    
    print("</ifStatement>")
        

def compileWhile():
    print("<whileStatement>")
    if advance(tokens)[1] == "while":
        printKeyword("while")
    else:
        print("Syntax error: expected 'while'")
        return
    
    if advance(tokens)[1] == "(":
        printSymbolTag("(")
    else:
        print("Syntax error: expected '('")
        return
    
    compileExpression()

    if advance(tokens)[1] == ")":
        printSymbolTag(")")
    else:
        print("Syntax error: expected ')'")
        return

    if advance(tokens)[1] == "{":
        printSymbolTag("{")
    else:
        print("Syntax error: expected '{'")
        return
    
    compileStatements()

    if advance(tokens)[1] == "}":
        printSymbolTag("}")
    else:
        print("Syntax error: expected '}'")
        return
    
    
    print("</whileStatement>")
    return

def compileDo():
    print("<doStatement>")

    if advance(tokens)[1] == "do":
        printKeyword("do")
    else:
        print("Syntax error: expected 'do'")
        return

    token = advance(tokens)
    
    if token and token[0] == "identifier":
        compileSubroutineCall(token)
    else:
        print("Syntax error: expected subroutine name")
        return
    
    if advance(tokens)[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return
    
    print("</doStatement>")
    return

def compileReturn():
    print("<returnStatement>")

    if advance(tokens)[1] == "return":
        printKeyword("return")
    else:
        print("Syntax error: expected 'return'")
        return
    
    if peek(tokens) and peek(tokens)[1] != ";":
        compileExpression()
    
    token = advance(tokens)

    if token and token[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return

    print("</returnStatement>")

#--------------------------------expressions-----------------------------#

def printConstant(term):
    if term[0] == "integerConstant":
        print("<integerConstant>" + term[1] + "</integerConstant>")
    else:
        print("<stringConstant>" + term[1] + "</stringConstant>")

def printKeywordConstant(term):
    print("<keywordConstant>" + term[1] + "</keywordConstant>")

def compileExpression():
    print("<expression>")

    print("<term>")
    compileTerm()  
    print("</term>")

    # handle (op term)*
    while peek(tokens) and peek(tokens)[1] in operators:
        printSymbolTag(advance(tokens)[1])  # print the op
        print("<term>")
        compileTerm()
        print("</term>")

    print("</expression>")

def compileTerm():
    term = checkTerm()

    if term != None:
        if term == "IntegerConstant" or term == "StringConstant":
            printConstant(advance(tokens))
        elif term == "keywordConstant":
            printKeywordConstant(advance(tokens))
        elif term == "identifier":
            varName = advance(tokens) #consume the identifier token
            if peek(tokens) and peek(tokens)[1] == "[":
                printIdentifier(varName[1])

                #should i comment out or not 
                advance(tokens) #consume the identifier token

                printSymbolTag("[")
                compileExpression()
                if advance(tokens)[1] == "]":
                    printSymbolTag("]")
                else:
                    print("Syntax error: expected ']'")
                    return
            elif peek(tokens) and peek(tokens)[1] in ["(", "."]:
                compileSubroutineCall(varName)
            else:    
                printIdentifier(varName[1])

        elif term == "unaryOp":
                printSymbolTag(advance(tokens)[1])  # consume the unary op
                print("<term>")
                compileTerm()
                print("</term>")

        elif term == "other symbol":
            printSymbolTag(advance(tokens)[1]) #consume the symbol "("
            compileExpression()
            token = advance(tokens)
            if token and token[0] == "symbol" and token[1]== ")":
                printSymbolTag(")")
            else:
                print("Syntax error: expected ')'")
                return

    else:
        print("Syntax error: expected term")
        return

    return

def compileSubroutineCall(varName):
    print("<subroutineCall>")
    printIdentifier(varName[1])

    # remove the "if token and token[0] == identifier" check entirely
    # just directly check what comes next with peek
    if peek(tokens) and peek(tokens)[1] == "(":
        advance(tokens)  # consume '('
        printSymbolTag("(")
        compileExpressionList()
        token = advance(tokens)
        if token and token[1] == ")":
            printSymbolTag(")")
        else:
            print("Syntax error: expected ')'")
            return

    elif peek(tokens) and peek(tokens)[1] == ".":
        advance(tokens)  # consume '.'
        printSymbolTag(".")
        token = advance(tokens)
        if token and token[0] == "identifier":
            printIdentifier(token[1])
        else:
            print("Syntax error: expected subroutine name after '.'")
            return
        
        token = advance(tokens)
        if token and token[1] == "(":
            printSymbolTag("(")
            compileExpressionList()
            token = advance(tokens)
            if token and token[1] == ")":
                printSymbolTag(")")
            else:
                print("Syntax error: expected ')'")
                return
        else:
            print("Syntax error: expected '('")
            return
    else:
        print("Syntax error: expected '(' or '.'")
        return
         
    print("</subroutineCall>")


def compileExpressionList():
    print("<expressionList>")
    
    if peek(tokens) and peek(tokens)[1] != ")":
        compileExpression()

        while peek(tokens) and peek(tokens)[1] == ",":
            advance(tokens) #consume the ','
            printSymbolTag(",")
            compileExpression()

    print("</expressionList>")
    return

def checkTerm():
    token = peek(tokens)
    if token == None:
        return None
    
    if token[0] == "integerConstant":
        return "IntegerConstant"
    elif token[0] == "stringConstant":
        return "StringConstant"
    elif token[0] == "keyword" and token[1] in ["true", "false", "null", "this"]:
        return "keywordConstant"
    elif token[0] == "identifier":
        return "identifier"
    elif token[0] == "symbol" and token[1] in symbols:
        if token[1] in ["-", "~"]:
            return "unaryOp"
        elif token[1] in operators:
            return "op"
        else:
            return "other symbol"
    else:
        return None


#------------------main function------------------#


def readFiles(path):
    #conver the path to a list of chars
    with open(path, 'r') as f:
        return list(f.read())
    
def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Enter the path to the file or directory to translate: ")

    if os.path.isdir(path):
        # get all .jack files in the directory
        jackFiles = [f for f in os.listdir(path) if f.endswith(".jack")]
        for jackFile in jackFiles:
            fullPath = os.path.join(path, jackFile)
            processFile(fullPath)
    elif os.path.isfile(path) and path.endswith(".jack"):
        processFile(path)
    else:
        print("Error: expected a .jack file or directory containing .jack files")


def processFile(path):
    global tokens
    tokens = [] #reset the list of tokens for each file
    with open(path, 'r') as f:
        chars = createCharLits(f)
        lexer(chars)
        print(tokens)
        #compileClass()

main()