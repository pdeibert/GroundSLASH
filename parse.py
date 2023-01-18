import sys
from antlr4 import *
from ASPLexer import ASPLexer
from ASPParser import ASPParser
#from ASPASTListener import ASPASTListener
from ProgramVisitor import ProgramVisitor
#from ASPVisitor import ASPVisitor


# read input program
input_stream = FileStream(sys.argv[1])

# tokenize
lexer = ASPLexer(input_stream)
stream = CommonTokenStream(lexer)
stream.fill()

# output tokens
print("Lexing:")
for token in stream.tokens:
    if token.type != '<EOF>':
        print(f"\t{lexer.symbolicNames[token.type] :15}{token.text}")
print()

# parse
print("Parsing:")
parser = ASPParser(stream)
tree = parser.program()

# traverse parse tree using visitor
visitor = ProgramVisitor()
ast = visitor.visitProgram(tree)
print(ast)