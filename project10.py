#-----------------------------lexer design------------------------------#

#this list will store all the toxers my design will find 
tokens = []

#still have to check for comments 
#still have to edit keywords 
#still have to maek sure my  lexer can handle string constants 

#these lists contain jack allowed keywords, operators, or symbols 
keywords = [
    'class', 'constructor', 'function', 'method', 
    'field', 'static', 'var', 'int', 'char', 
    'boolean', 'void', 'true', 'false', 'null', 
    'this', 'let', 'do', 'if', 'else', 
    'while', 'return'
]
operators = ['+', '-', '*', '/', '=', '==', '!=', '<', '>', '<=', '>=']
symbols = [
    '{', '}', '(', ')', '[', ']', 
    '.', ',', ';', '+', '-', '*', 
    '/', '&', '|', '<', '>', '=', '~'
]
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
    compileSubroutineDec()
    
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
    while token and token[0] == "keyword" and token[1] in ["let", "if", "while", "do", "return"]:
        print("<statements>")
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
    
    if advance(tokens)[1] == "let":
        printKeyword("let")
        token = advance(tokens)
    else:
        print("Syntax error: expected 'let'")
        return
    
    print("letStatement>")
    
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
    
    if peek(tokens) and peek(tokens)[1] == "else":
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

    print("</whileStatement>")
    return

def compileDo():
    print("<DoStatement>")

    if advance(tokens)[1] == "do":
        printKeyword("do")
    else:
        print("Syntax error: expected 'do'")
        return

    compileSubroutineCall()

    if advance(tokens)[1] == ";":
        printSymbolTag(";")
    else:
        print("Syntax error: expected ';'")
        return
    
    print("</DoStatement>")
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
    else:
        printSymbolTag(";")

    print("</returnStatement>")
    return

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
    term = checkTerm()
    if term != None:
        if term == "IntegerConstant" or term == "StringConstant":
            printConstant(advance(tokens))
        elif term == "keywordConstant":
            printKeywordConstant(advance(tokens))
        elif term == "identifier":
            varName = advance(tokens) #consume the identifier token
            if peek(tokens) and peek(tokens)[1] == "[":
                printIdentifier(varName)
                advance(tokens) #consume the identifier token
                printSymbolTag("[")
                compileExpression()
                if advance(tokens)[1] == "]":
                    printSymbolTag("]")
                else:
                    print("Syntax error: expected ']'")
                    return
            elif peek(tokens) and peek(tokens)[1] == "(":
                compileSubroutineCall()
            else:    
                printIdentifier(varName)

        elif term == "symbol":
            if checkTerm() == "unaryOp":
                printSymbolTag(advance(tokens)[1]) #consume the unary operator
                compileTerm()

    else:
        print("Syntax error: expected term")
        return

    print("</expression>")
    return

def compileSubroutineCall():
    print("<subroutineCall>")


    print("</subroutineCall>")
    return

def checkTerm():
    token = peek(tokens)
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
        else:
            return "op"
    else:
        return None


#------------------main function------------------#





