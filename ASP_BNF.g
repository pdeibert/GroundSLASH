program             :   statements query ;

statements          :   statements statement
                    |   statement
                    |   EPSILON
                    ;

query               :   classical_literal QUERY_MARK
                    |   EPSILON
                    ;

statement           :   CONS body DOT
                    |   CONS DOT
                    |   head CONS DOT
                    |   head CONS body DOT
                    |   head DOT
                    |   WCONS body DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE
                    |   WCONS DOT SQUARE_OPEN weight_at_level SQUARE_CLOSE
                    ;

head                :   disjunction
                    |   choice
                    ;

body                :   body COMMA naf_literal;
                    |   body COMMA NAF aggregate
                    |   body COMMA aggregate
                    |   naf_literal
                    |   NAF aggregate
                    |   aggregate
                    ;

disjunction         :   disjunction OR classical_literal
                    |   classical_literal
                    ;

choice              :   term binop CURLY_OPEN choice_elements CURLY_CLOSE binop term
                    |   term binop CURLY_OPEN choice_elements CURLY_CLOSE
                    |   term binop CURLY_OPEN CURLY_CLOSE binop term
                    |   CURLY_OPEN choice_elements CURLY_CLOSE binop term
                    |   term binop CURLY_OPEN CURLY_CLOSE
                    |   CURLY_OPEN choice_elements CURLY_CLOSE
                    |   CURLY_OPEN CURLY_CLOSE binop term
                    |   CURLY_OPEN CURLY_CLOSE
                    ;

choice_elements     :   choice_elements SEMICOLON choice_element
                    |   choice_element
                    ;

choice_element      :   classical_literal COLON naf_literals
                    |   classical_literal COLON
                    |   classical_literal
                    ;

aggregate           :   term binop aggregate_function CURLY_OPEN aggregate_elements CURLY_CLOSE binop term
                    |   term binop aggregate_function CURLY_OPEN choice_elements CURLY_CLOSE
                    |   term binop aggregate_function CURLY_OPEN CURLY_CLOSE binop term
                    |   aggregate_function CURLY_OPEN choice_elements CURLY_CLOSE binop term
                    |   term binop aggregate_function CURLY_OPEN CURLY_CLOSE
                    |   aggregate_function CURLY_OPEN choice_elements CURLY_CLOSE
                    |   aggregate_function CURLY_OPEN CURLY_CLOSE binop term
                    |   aggregate_function CURLY_OPEN CURLY_CLOSE               
                    ;

aggregate_elements  :   aggregate_elements SEMICOLON aggregate_element
                    |   aggregate_element
                    ;

aggregate_element   :   basic_terms COLON naf_literals
                    |   basic_terms COLON
                    |   basic_terms
                    ;

aggregate_function  :   AGGREGATE_COUNT
                    |   AGGREGATE_MAX
                    |   AGGREGATE_MIN
                    |   AGGREGATE_SUM
                    ;

weight_at_level     :   term AT term COMMA terms
                    |   term AT term
                    |   term COMMA terms
                    |   term
                    ;

naf_literals        :   naf_literals COMMA naf_literals
                    |   naf_literals        
                    ;

naf_literal         :   classical_literal | builtin_atom
                    |   classical_literal
                    |   builtin_atom
                    ;

classical_literal   :   MINUS ID PAREN_OPEN terms PAREN_CLOSE
                    |   MINUS ID PAREN_OPEN PAREN_CLOSE
                    |   MINUS ID
                    |   ID PAREN_OPEN terms PAREN_CLOSE
                    |   ID PAREN_OPEN PAREN_CLOSE
                    |   ID
                    ;

builtin_atom        :   term binop term ;

binop               :   EQUAL
                    |   UNEQUAL
                    |   LESS
                    |   GREATER
                    |   LESS_OR_EQ
                    |   GREATER_OR_EQ
                    ;

terms               :   terms COMMA term
                    |   term                    
                    ;

term                :   ID PAREN_OPEN terms PAREN_CLOSE
                    |   ID PAREN_OPEN PAREN_CLOSE
                    |   ID
                    |   NUMBER
                    |   STRING
                    |   VARIABLE
                    |   ANONYMOUS_VARIABLE
                    |   PAREN_OPEN term PAREN_CLOSE
                    |   MINUS term
                    |   term arithop term
                    ;

basic_terms         :   basic_terms COMMA basic_term
                    |   basic_terms                    
                    ;

basic_term          :   ground_term
                    |   variable_term
                    ;

ground_term         :   SYMBOLIC_CONSTANT
                    |   STRING
                    |   MINUS NUMBER
                    |   NUMBER
                    ;

variable_term       :   VARIABLE
                    |   ANONYMOUS_VARIABLE
                    ;

arithop             :   PLUS
                    |   MINUS
                    |   TIMES
                    |   DIV
                    ;

---------------------------------------------------------------------

ID                  :   [a-z][A-Za-z0-9_]* // include underscore
VARIABLE            :   [A-Z][A-Za-z0-9_]* // include underscore
STRING              :   \"([^\"]|\\\")*\"
NUMBER              :   "0"|[1-9][0-9]*
ANONYMOUS_VARIABLE  :   "_"
DOT                 :   "."
COMMA               :   ","
QUERY_MARK          :   "?"
COLON               :   ":"
SEMICOLON           :   ";"
OR                  :   "|"
NAF                 :   "not"
CONS                :   ":-"
WCONS               :   ":-"
PLUS                :   "+"
MINUS               :   "-"
TIMES               :   "*"
DIV                 :   "/"
AT                  :   "@"
PAREN_OPEN          :   "("
PAREN_CLOSE         :   ")"
SQUARE_OPEN         :   "["
SQUARE_CLOSE        :   "]"
CURLY_OPEN          :   "{"
CURLY_CLOSE         :   "}"
EQUAL               :   "="
UNEQUAL             :   "!=" | "<>"
LESS                :   "<"
GREATER             :   ">"
LESS_OR_EQ          :   "<="
GREATER_OR_EQ       :   ">="
AGGREGATE_COUNT     :   "#count"
AGGREGATE_MAX       :   "#max"
AGGREGATE_MIN       :   "#min"
AGGREGATE_SUM       :   "#sum"
COMMENT             :   "%"([^*\n][^\n]*)?\n
MULTI_LINE_COMMENT  :   "%*"([^*]|\*[^%])*"*%"
BLANK               :   [ \t\n]+
