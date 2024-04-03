# GroundSLASH

![Test badge](https://github.com/pdeibert/GroundSLASH/actions/workflows/tests.yaml/badge.svg?branch=main)
![Coverage badge](https://github.com/pdeibert/GroundSLASH/blob/main/coverage.svg)

Parser and Grounder for the deep probabilistic programming language (DPPL) SLASH. SLASH is neural-probabilistic extension of the Answer Set Programming (ASP) paradigm. For more information, see:
* [ASP-Core-2 Input Language Format](https://arxiv.org/abs/1911.04326)
* [SLASH: Embracing Probabilistic Circuits into Neural Answer Set Programming](https://arxiv.org/abs/2110.03395)
* [Scalable Neural-Probabilistic Answer Set Programming](https://arxiv.org/abs/2306.08397)

GroundSLASH is a fork of the [ASPy](https://github.com/pdeibert/ASPy) parser and grounder for Answer Set programs, extended to the SLASH language.

The grounding process generally follows the procedure described in [On the Foundations of Grounding in Answer Set Programming](https://arxiv.org/abs/2108.04769).

This library serves the following purposes:
* Provide an easy-to-use parser and grounder for SLASH
* Serve as a starting point for further experimental extensions to the input language using a high-level programming language (i.e., Python)

## Installation

To install, run `pip install .`. If you wish to modify the project, install the package using the extra `dev` option: `pip install .[dev]`.

Before using `GroundSLASH` for the first time, the ANTLR parser files need to be generated using the ANTLR runtime installed on the host system. To do so, simply run `ground_slash init` in a terminal. If this for some reason fails, you can manually generate the parse by calling `antlr4 -Dlanguage=Python3 -visitor -no-listener SLASH.g4` from the `ground_slash/parser` directory of the installed package.

## Usage

### Command Line Interface

The package provides a convenient `ground_slash` command line tool:
```
ground_slash -f <infile> [-o <outfile]
```
If no output file is specified, the grounded program will simply be output to the console (if successful).

### Python

Programs are usually automatically build from a convenient string notation of the input language. As an example, consider an [MNIST-addition](https://arxiv.org/abs/1805.10872) task with two images:
```python
from ground_slash.program import Program
from ground_slash.grounding import Grounder

mnist_prog = r'''
% input images
img(i1). img(i2).

% neural-probabilistic predicate 'digit' for each image
#npp(digit(X), [0,1,2,3,4,5,6,7,8,9]) :- img(X).

% sum of digits
addition(I1,I2,D1+D2) :- digit(I1,D1), digit(I2,D2), I1<I2.
% commutativity
addition(I2,I1,S) :- addition(I1,I2,S), I1<I2.
'''

# parse program
prog = Program.from_string(mnist_prog)
# ground program
ground_prog = Grounder(prog).ground()
```
This should result in the following ground program (the order of statements may differ):
```python
str(ground_prog)
```
```
img(i1).
img(i2).

#npp(digit(i1), [0,1,2,3,4,5,6,7,8,9]) :- img(i1).
#npp(digit(i2), [0,1,2,3,4,5,6,7,8,9]) :- img(i2).

addition(i1,i2,0) :- digit(i1,0), digit(i2,0), i1<i2.
addition(i1,i2,1) :- digit(i1,0), digit(i2,1), i1<i2.
addition(i1,i2,2) :- digit(i1,0), digit(i2,2), i1<i2.
addition(i1,i2,3) :- digit(i1,0), digit(i2,3), i1<i2.
addition(i1,i2,4) :- digit(i1,0), digit(i2,4), i1<i2.
addition(i1,i2,5) :- digit(i1,0), digit(i2,5), i1<i2.
addition(i1,i2,6) :- digit(i1,0), digit(i2,6), i1<i2.
addition(i1,i2,7) :- digit(i1,0), digit(i2,7), i1<i2.
addition(i1,i2,8) :- digit(i1,0), digit(i2,8), i1<i2.
addition(i1,i2,9) :- digit(i1,0), digit(i2,9), i1<i2.
...
addition(i1,i2,9) :- digit(i1,9), digit(i2,0), i1<i2.
addition(i1,i2,10) :- digit(i1,9), digit(i2,1), i1<i2.
addition(i1,i2,11) :- digit(i1,9), digit(i2,2), i1<i2.
addition(i1,i2,12) :- digit(i1,9), digit(i2,3), i1<i2.
addition(i1,i2,13) :- digit(i1,9), digit(i2,4), i1<i2.
addition(i1,i2,14) :- digit(i1,9), digit(i2,5), i1<i2.
addition(i1,i2,15) :- digit(i1,9), digit(i2,6), i1<i2.
addition(i1,i2,16) :- digit(i1,9), digit(i2,7), i1<i2.
addition(i1,i2,17) :- digit(i1,9), digit(i2,8), i1<i2.
addition(i1,i2,18) :- digit(i1,9), digit(i2,9), i1<i2.

addition(i2,i1,0) :- addition(i1,i2,0), i1<i2.
...
addition(i2,i1,18) :- addition(i1,i2,18), i1<i2.
```

### Development

Modifications to the input language require the parser to be modified. `GroundSLASH` uses ANTLR4 to generate a parser based on a specified grammar. The grammar (in EBNF notation) can be found under `ground_slash/parser/SLASH.g4`. To generate the parser files, either run `ground_slash init` if the package is already installed, or generate them manually by calling `antlr4 -Dlanguage=Python3 -visitor -no-listener SLASH.g4` from the directory of the grammar file.

The parse tree is then converted into an internal representation using `ground_slash/parser/program_builder.py`. Internally, syntactic elements (terms, literals, rules, ...) are implemented using classes which provide convenient methods and operators for handling them, allowing for easy modification and extensions. New types of terms, literals, and statements can be derived from these classes, which reside in `ground_slash/program`.

The grounder and all associated functionality can be found in `ground_slash/grounder`.

## Additional Resources

Related repositories:
* https://github.com/ml-research/SLASH
* https://github.com/pdeibert/GLASH