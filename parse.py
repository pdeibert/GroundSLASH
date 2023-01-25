import sys
from antlr4 import * # type: ignore
from ASPCoreLexer import ASPCoreLexer
from ASPCoreParser import ASPCoreParser
from ProgramBuilder import ProgramBuilder

# read input program
input_stream = FileStream(sys.argv[1]) # type: ignore

# tokenize
lexer = ASPCoreLexer(input_stream)
stream = CommonTokenStream(lexer) # type: ignore
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
visitor = ProgramBuilder()
statements, query = visitor.visitProgram(tree)

#for s in statements:
#    print(s)

from term import Number, SymbolicConstant, String

cons = statements[-2]
print(cons)

print(cons.substitute({'X': Number(-10)}))

try:
    print(cons.substitute({'Y': Number(-10)}))
except:
    print('Exception raised')

print(cons.substitute({'X': SymbolicConstant("test")}))
print(cons.substitute({'X': String("Test")}))