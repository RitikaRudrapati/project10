
import os
import sys

global message

current_subroutine_name = ""
current_subroutine_type = ""

message = ""
file = ""

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

#helper functions for the parser to advance, peek, and check the type of the next token without consuming it
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
    global message
    message += "<class>\n"
    printKeyword("class")
    printIdentifier(indentifer)

def printSymbolTag(symbol):
    global message

    if symbol == "<":
        symbol = "&lt;"
    elif symbol == ">":
        symbol = "&gt;"
    elif symbol == "&":
        symbol = "&amp;"

    message += "<symbol>" + symbol + "</symbol>\n"

def printClassVarDecTag():
    global message
    message += "<classVarDec>\n"
    message += "</classVarDec>\n"

def printKeyword(keyword):
    global message
    message += "<keyword>" + keyword + "</keyword>\n"

def printIdentifier(identifier):
    global message
    message += "<identifier>" + identifier + "</identifier>\n"

def compileClass():
    global message, current_class_name
    # advance and check for 'class' keyword
    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] == "class":
        # advance and check for class name (identifier)
        token = advance(tokens)
        if token and token[0] == "identifier":
            current_class_name = token[1]
            resetClassTable()  # reset the class symbol table for the new class
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

    message += "</class>\n"

def compileClassVarDec():
    global message
    message += "<classVarDec>\n"

    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] in ["static", "field"]:
        kind = token[1]        # <-- save kind
        printKeyword(token[1])
    
    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
        var_type = token[1]    # <-- save type
        printKeyword(token[1])
    elif token and token[0] == "identifier":
        var_type = token[1]    # <-- save type
        printIdentifier(token[1])

    token = advance(tokens)
    if token and token[0] == "identifier":
        define(token[1], var_type, kind)   # <-- add this
        message += "<identifier> " + token[1] + "</identifier>\n"

    while peek(tokens) and peek(tokens)[1] == ",":
        advance(tokens)
        printSymbolTag(",")
        token = advance(tokens)
        if token and token[0] == "identifier":
            define(token[1], var_type, kind)   # <-- add this (same kind/type, new name)
            printIdentifier(token[1])

    # expect ';'
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return

    message += "</classVarDec>\n"


def compileSubroutineDec(keyword):
    global message, current_subroutine_type
    current_subroutine_type = keyword   # <-- add this
    resetSubroutineTable()              # <-- add this

    if keyword == "method":
        define("this", current_class_name, "arg")


    message += "<subroutineDec>\n"

    advance(tokens)
    
    printKeyword(keyword)

    token = advance(tokens)

    if token and token[0] == "keyword" and token[1] in ["void", "int", "char", "boolean"]:
        printKeyword(token[1])
    elif token and token[0] == "identifier":
        current_subroutine_name = token[1]
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
    
    message += "</subroutineDec>\n"

def compileParameterList():
    global message
    #should find a '(' symbol
    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == "(":
        printSymbolTag("(")
    else:
        print("Syntax error: expected '('")
        return
    
    message += "<parameterList>\n"

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
            
    message += "</parameterList>\n"

    token = advance(tokens)
    if token and token[0] == "symbol" and token[1] == ")":
        printSymbolTag(")")
    else:
        print("Syntax error: expected ')'")
        return
    
#compile the subroutine body, which should be in the form '{ varDec* statements }'
def compileSubroutineBody():
    global message

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
    


#done
def compileVarDec():
    global message

    token = advance(tokens)
    if token and token[0] == "keyword" and token[1] == "var":
        printKeyword("var")
    else:
        print("Syntax error: expected 'var'")
        return

    token = advance(tokens)

    if token and token[0] == "keyword" and token[1] in ["int", "char", "boolean"]:
        printKeyword(token[1])
        var_type = token[1]
    elif token and token[0] == "identifier":
        printIdentifier(token[1])
        var_type = token[1]
    else:
        print("Syntax error: expected an int, char, boolean, or class type")
        return
    
    token = advance(tokens)

    if token and token[0] == "identifier":
        printIdentifier(token[1])
        define(token[1], var_type, "var")
    else:
        print("Syntax error: expected varName")
        return
    
    # use peek to check for ',' or ';'
    while peek(tokens) and peek(tokens)[1] == ",":
        advance(tokens)  # consume the ','
        printSymbolTag(",")
        token = advance(tokens)
        if token and token[0] == "identifier":
            define(token[1], var_type, "var")
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
    


#check to see if the next token is a statement, and if it is, compile the statement, and keep doing this until there are no more statements to compile, and then return
def compileStatements():
    global message 

    while peek(tokens) and peek(tokens)[0] == "keyword" and peek(tokens)[1] in ["let", "if", "while", "do", "return"]:
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
    
    
    return

#check to see if the next token is a let statement, and if it is, compile the let statement, which should be in the form 'let varName = expression;' or 'let varName[expression] = expression;'
def compileLet():
    global message
    
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
    


#compile an if statement, which can be either 'if (expression) {statements}' or 'if (expression) {statements} else {statements}'
def compileIf():
    global message


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
    
        

#compile a while statement 
def compileWhile():
    global message

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
    
    #check to see if there is an expression after the '(' symbol, and if there is, compile the expression
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
    
    #check to see if it this an empty while loop or if there are statements to compile, and if there are statements, compile the statements
    compileStatements()

    if advance(tokens)[1] == "}":
        printSymbolTag("}")
    else:
        print("Syntax error: expected '}'")
        return
    
    
    return


#compile a do statement, calling compileSubroutineCall to handle the subroutine call, and then expect a ';' symbol at the end
def compileDo():
    global message

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
    
    return

#compile a return statement, which can be either 'return;' or 'return expression;'
def compileReturn():
    global message

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



#helper functions to print the different types of terms
def printConstant(term):
    global message

    if term[0] == "integerConstant":
        message += "<integerConstant>" + term[1] + "</integerConstant>\n"
    else:
        message += "<stringConstant>" + term[1] + "</stringConstant>\n"

def printKeywordConstant(term):
    global message
    message += "<keywordConstant>" + term[1] + "</keywordConstant>\n"

def compileExpression():
    global message
    message += "<expression>\n"

    message += "<term>\n"
    compileTerm()  
    message += "</term>\n"

    # handle (op term)*
    while peek(tokens) and peek(tokens)[1] in operators:
        printSymbolTag(advance(tokens)[1])  # print the op
        message += "<term>\n"
        compileTerm()
        message += "</term>\n"

    message += "</expression>\n"

#compile a term, which can be an integer constant, string constant, keyword constant, varName, varName[expression], subroutineCall, (expression), or unaryOp term
def compileTerm():
    global message
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
                message += "<term>\n"
                compileTerm()
                message += "</term>\n"

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

#compile the subroutine call, which can be either subroutineName(expressionList) or (className|varName).subroutineName(expressionList)

def compileSubroutineCall(varName):
    global message
    printIdentifier(varName[1])

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
         
#keep compiling expressions until we find a ')' symbol, but do not consume the ')' symbol
def compileExpressionList():
    global message
    message += "<expressionList>\n"
    
    if peek(tokens) and peek(tokens)[1] != ")":
        compileExpression()

        while peek(tokens) and peek(tokens)[1] == ",":
            advance(tokens) #consume the ','
            printSymbolTag(",")
            compileExpression()

    message += "</expressionList>\n"
    return

#check what type of term by peeking and return the type as a string, but do not consume the token
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



#-------------------------project 11-------------------------#


#-----------------symbol table-------------------#

class_symbol_table = {"static": {}, "field": {}}
subroutine_symbol_table = {"arg": {}, "var": {}}
current_class_name = ""
current_subroutine_type = ""  # 'function', 'constructor', or 'method'

def resetClassTable():
    global class_symbol_table
    class_symbol_table = {"static": {}, "field": {}}

def resetSubroutineTable():
    global subroutine_symbol_table
    subroutine_symbol_table = {"arg": {}, "var": {}}

def define(name, type, kind):
    if kind in ("static", "field"):
        index = len(class_symbol_table[kind])
        class_symbol_table[kind][name] = {"type": type, "index": index}
    elif kind in ("arg", "var"):
        index = len(subroutine_symbol_table[kind])
        subroutine_symbol_table[kind][name] = {"type": type, "index": index}

def varCount(kind):
    if kind in ("static", "field"):
        return len(class_symbol_table[kind])
    elif kind in ("arg", "var"):
        return len(subroutine_symbol_table[kind])
    return 0

def kindOf(name):
    # Subroutine scope takes priority over class scope
    for kind in subroutine_symbol_table:
        if name in subroutine_symbol_table[kind]:
            return kind
    for kind in class_symbol_table:
        if name in class_symbol_table[kind]:
            return kind
    return None

def typeOf(name):
    for kind in subroutine_symbol_table:
        if name in subroutine_symbol_table[kind]:
            return subroutine_symbol_table[kind][name]["type"]
    for kind in class_symbol_table:
        if name in class_symbol_table[kind]:
            return class_symbol_table[kind][name]["type"]
    return None

def indexOf(name):
    for kind in subroutine_symbol_table:
        if name in subroutine_symbol_table[kind]:
            return subroutine_symbol_table[kind][name]["index"]
    for kind in class_symbol_table:
        if name in class_symbol_table[kind]:
            return class_symbol_table[kind][name]["index"]
    return None

def writePushVar(name):
    kind = kindOf(name)
    index = indexOf(name)

    if kind == "static":
        writePush("static", index)
    elif kind == "field":
        writePush("this", index)
    elif kind == "arg":
        writePush("argument", index)
    elif kind == "var":
        writePush("local", index)


def writePopVar(name):
    kind = kindOf(name)
    type = typeOf(name)
    index = indexOf(name)

    if kind == "static":
        writePop("static", index)
    elif kind == "field":
        writePop("this", index)
    elif kind == "arg":
        writePop("argument", index)
    elif kind == "var":
        writePop("local", index)


def writePushConstant(value):
    writePush("constant", value)

def writeArithmetic(command):
    global message
    if command == "+":
        message += "add\n"
    elif command == "-":
        message += "sub\n"
    elif command == "*":
        message += "call Math.multiply 2\n"
    elif command == "/":
        message += "call Math.divide 2\n"
    elif command == "&":
        message += "and\n"
    elif command == "|":
        message += "or\n"
    elif command == "<":
        message += "lt\n"
    elif command == ">":
        message += "gt\n"
    elif command == "=":
        message += "eq\n"
    elif command == "neg":
        message += "neg\n"
    elif command == "not":
        message += "not\n"

def writeUnaryArithmetic(command):
    global message
    if command == "-":
        message += "neg\n"
    elif command == "~":
        message += "not\n"

def writeFunction(name, nLocals):
    global message
    message += "function " + name + " " + str(nLocals) + "\n"

def writeCall(name, nArgs):
    global message
    message += "call " + name + " " + str(nArgs) + "\n"

def writeReturn():
    global message
    message += "return\n"

def writeKeywordConstant(keywordConstant):
    if keywordConstant == "true":
        writePushConstant(0)
        writeArithmetic("not")   # <-- not writeUnaryArithmetic
    elif keywordConstant in ["false", "null"]:
        writePushConstant(0)
    elif keywordConstant == "this":
        writePush("pointer", 0)  # <-- not writePushVar, "this" means pointer 0
        
def writePop(segment, index):
    global message
    message += "pop " + segment + " " + str(index) + "\n"

def writePush(segment, index):
    global message
    message += "push " + segment + " " + str(index) + "\n"



#read the files and return a list of characters
def readFiles(path):
    #conver the path to a list of chars
    with open(path, 'r') as f:
        return list(f.read())

#code taken from my project 7&8  
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
    global message

    message = "" #reset the message for each file
    tokens = [] #reset the list of tokens for each file

    with open(path, 'r') as f:
        chars = createCharLits(f)
        lexer(chars)
        
        compileClass()
        
        writeToFile(path)

        print("Output written to " + path.split(".")[0] + ".xml")


def writeToFile(path):
    global message

    #code credit to stack overflow for this part: https://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
    folder = os.path.dirname(path)
    base_name = os.path.basename(path).split(".")[0]
    output_path = os.path.join(folder, base_name + ".xml")    

    with open(output_path, "w") as outfile:
        outfile.write(message)

#run the main function
main()

print("Class table:", class_symbol_table)
print("Subroutine table:", subroutine_symbol_table)