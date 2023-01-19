import sys
from antlr4 import *
from ASPCoreLexer import ASPCoreLexer
from ASPCoreParser import ASPCoreParser
from ASTVisitor import ASTVisitor

# read input program
input_stream = FileStream(sys.argv[1])

# tokenize
lexer = ASPCoreLexer(input_stream)
stream = CommonTokenStream(lexer)
stream.fill()

# output tokens
"""
print("Lexing:")
for token in stream.tokens:
    if token.type != '<EOF>':
        print(f"\t{lexer.symbolicNames[token.type] :15}{token.text}")
print()
"""

# parse
print("Parsing:")
parser = ASPCoreParser(stream)
tree = parser.program()

# traverse parse tree using visitor
visitor = ASTVisitor()
statements, query = visitor.visitProgram(tree)

for s in statements:
    print(s)