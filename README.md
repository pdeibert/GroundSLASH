# GroundSLASH

![Test badge](https://github.com/pdeibert/GroundSLASH/actions/workflows/tests.yaml/badge.svg)
![Coverage badge](https://github.com/pdeibert/GroundSLASH/blob/actions/coverage.svg)

Parser and Grounder for the deep probabilistic programming language (DPPL) SLASH. SLASH is neural-probabilistic extension of the Answer Set Programming (ASP) paradigm. For more information, see:
* [SLASH: Embracing Probabilistic Circuits into Neural Answer Set Programming](https://arxiv.org/abs/2110.03395)
* [Scalable Neural-Probabilistic Answer Set Programming](https://arxiv.org/abs/2306.08397)

GroundSLASH is based is a modification of the [ASPy](https://github.com/pdeibert/ASPy) parser and grounder for Answer Set programs.

Syntactic elements are implemented using classes which provide convenient methods and operators for handling them.

Programs can be either build directly from objects or parsed from a convenient string notation.

The grounding process generally follows the procedure described in [On the Foundations of Grounding in Answer Set Programming](https://arxiv.org/abs/2108.04769).

Related repositories:
* https://github.com/d-ochs/SLASH