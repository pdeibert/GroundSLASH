# GroundSLASH

![Test badge](https://github.com/pdeibert/GroundSLASH/actions/workflows/tests.yaml/badge.svg)
![Coverage badge](https://github.com/pdeibert/GroundSLASH/blob/actions/coverage.svg)

Parser and Grounder for the deep probabilistic programming language (DPPL) SLASH. SLASH is neural-probabilistic extension of the Answer Set Programming (ASP) paradigm. For more information, see:
* [SLASH: Embracing Probabilistic Circuits into Neural Answer Set Programming](https://arxiv.org/abs/2110.03395)
* [Scalable Neural-Probabilistic Answer Set Programming](https://arxiv.org/abs/2306.08397)

GroundSLASH is a fork of the [ASPy](https://github.com/pdeibert/ASPy) parser and grounder for Answer Set programs, extended to the SLASH language.

Syntactic elements (terms, literals, rules, ...) are implemented using classes which provide convenient methods and operators for handling them.

Programs can be either constructed directly from objects or parsed and build automatically from a convenient string notation.

The grounding process generally follows the procedure described in [On the Foundations of Grounding in Answer Set Programming](https://arxiv.org/abs/2108.04769).

This library serves the following purposes:
* Provide an easy to use parser and grounder for SLASH
* Serve as a starting point for further experimental extensions to the input language using a high-level programming language (i.e., Python)

Related repositories:
* https://github.com/d-ochs/SLASH
* https://github.com/pdeibert/GLASH