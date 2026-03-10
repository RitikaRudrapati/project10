#-----------------------------lexer design------------------------------#

#this list will store all the toxers my design will find 
tokens = []

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







