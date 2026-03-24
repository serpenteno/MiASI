grammar SmartHome;

// Parser

program
    : statement+ EOF
    ;

statement
    : ifStatement
    | forStatement
    | command
    ;

ifStatement
    : IF LPAREN condition RPAREN ifBlock
      (ELSE elseBlock)?
    ;

ifBlock: LBRACE statement+ RBRACE ;
elseBlock: LBRACE statement+ RBRACE ;

forStatement
    : FOR ID IN roomList LBRACE statement+ RBRACE
    ;

roomList
    : LBRACKET ID (COMMA ID)* RBRACKET
    ;

condition
    : device DOT property IS STATE # stateCondition
    | device DOT property COMPARE NUMBER # compareCondition
    ;

command
    : SET device DOT property ASSIGN value SEMI # setCommand
    | TURN onOff device DOT LIGHT SEMI # lightCommand
    | IGNORE device DOT property SEMI # ignoreCommand
    | UNIGNORE device DOT property SEMI # unignoreCommand
    ;

device: ID ;
property: TEMP | LIGHT | WINDOW ;
value: NUMBER | STATE ;
onOff: ON | OFF ;

// Lexer

IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
IN: 'in' ;
IS: 'is' ;
SET: 'set' ;
TURN: 'turn' ;
IGNORE: 'ignore' ;
UNIGNORE: 'unignore' ;
ON: 'on' ;
OFF: 'off' ;

TEMP: 'temp' ;
LIGHT: 'light' ;
WINDOW: 'window' ;

STATE: 'open' | 'closed' ;

LPAREN: '(' ;
RPAREN: ')' ;
LBRACE: '{' ;
RBRACE: '}' ;
LBRACKET: '[' ;
RBRACKET: ']' ;
ASSIGN: '=' ;
COMPARE: '>' | '>=' | '<' | '<=' ;
DOT: '.' ;
SEMI: ';' ;
COMMA: ',' ;

NUMBER: [0-9]+ ('.' [0-9]+)? ;
ID: [a-zA-Z_][a-zA-Z0-9_]* ;

WS: [ \t\r\n]+ -> skip ;
COMMENT: '#' ~[\r\n]* -> skip ;
