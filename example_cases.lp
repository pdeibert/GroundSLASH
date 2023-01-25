%* ----- facts ----- *%

% should be parsed identically
fact1.
fact2().

% should be parsed identically
fact2(entity).
fact3(entity) :- .

%* ----- constraints ----- *%

:- constr1(X).

%* ----- normal rules ----- *%

%* ----- disjunctive rules ----- *%

%* ----- arithmetical terms ----- *%
head(X) :- body(2+X*3*(2+1)).