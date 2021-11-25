
# Introduction

Tempiny is a tiny and really simple template engine.

The main feature is to be able to execute arbitrary python code inside the template,
which makes it really powerful for code generation for example.

See the skbs project to have a sense of what it can achieve !


# Install

Simply pip install it :

    pip install tempiny

# Template syntax

First an example to demonstrate all its features :


    This text will be printed as it is
    
    Lines starting with '##' (or a user-configured prefix) are python code.
    
    ## a=5 # this won't be printed
    ## # this is a comment in the python script. Won't be printed.
    
    if/else/for/while/with/try/except etc blocks don't need indentation. Instead, a line containing only '## -' marks the block end.
    
    ## for i in range(a) :
    ##   b = a + 1 # you may indent
    ## c = a +2 # or not, still in the for block.
    This text will be printed 5 times (a = {{a}}) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    ##   for j in range(3) :
    You can also nest loops
    ##   -
    ## # ↑ end of inner loop
    ## -
    ## # end of outer loop
    
    Expression can be as complex you want as long as they are valid python expression returning something that can be transformed to a string :
    {{ ";".join( str(i) + f' - {a=},{b=},{c=}' for i in range(2)) }}


will be output as :

    This text will be printed as it is
    
    Lines starting with '##' (or a user-configured prefix) are python code.
    
    
    if/else/for/while/with/try/except etc blocks don't need indentation. Instead, a line containing only '## -' marks the block end.
   
    This text will be printed 5 times (a = 5) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    You can also nest loops
    You can also nest loops
    You can also nest loops
    This text will be printed 5 times (a = 5) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    You can also nest loops
    You can also nest loops
    You can also nest loops
    This text will be printed 5 times (a = 5) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    You can also nest loops
    You can also nest loops
    You can also nest loops
    This text will be printed 5 times (a = 5) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    You can also nest loops
    You can also nest loops
    You can also nest loops
    This text will be printed 5 times (a = 5) Btw, between a double brace (2 '{'), you can put expression that will be converted to str, and printed instead.
    To escape it, The prefered way is to declare variables containing the tokens (as done in skbs)
    You can also nest loops
    You can also nest loops
    You can also nest loops
   
   Expression can be as complex you want as long as they are valid python expression returning something that can be transformed to a string :
   0 - a=5,b=6,c=7;1 - a=5,b=6,c=7


Basically, there are 3 contexts : 

## Code context

Each line starting by the code prefix (specified in `plugin.py`, or '##' by default) is basically python code except for the block delimitation :
in python, the indentation level delimits a block while with tempiny, for practical use, indentation doesn't matter, and a block is ended by a single dash ( "-" ).

Example : 

    ## a = 5
    ## for i in range(a) :
    ##   b = 2 + i
    ##   # Do come stuff
    ## c=3 # this is still in the for
    ## -
    ## # end of the for


Any python code is allowed. This is the reason you should use templates **only from trusted sources**.

## Text context

Any line that doesn't start with the code prefix is "text", and will be output as is each time the execution flow reaches it.
Basically, you can imagine (by the way, this is actually how it is implemented...) each Text context is like a call to `print` 

For example, the following : 

    This is a text
    ## for i in range(3):
    To see
    ## -
    how it works

Will output : 

    This is a test
    To see
    To see
    To see
    how it works

## Expression context

Inside a Text context, you may want to print an expression (for example a variable value or the result of a python call etc.)
You can do it by surrounding it with the expression delimiters (specified in `plugin.py` or '{{' and '}}' by default).
It will be replaced by the expression value at the time of execution. Example:

    ## for i in range(3)
    Item number {{i}}
    ## -

Will print :

    Item number 0
    Item number 1
    Item number 2

Any python expression is allowed.

Once again, you should only execute trusted templates.

# API

    from tempiny import Tempiny # import tempiny

There are 3 built-in dialects:

    Tempiny.C  = dict(stmt_line_start=r'//#', begin_expr='{{', end_expr='}}')
    Tempiny.PY = dict(stmt_line_start=r'##', begin_expr='{{', end_expr='}}')
    Tempiny.TEX = dict(stmt_line_start=r'%#', begin_expr='<<', end_expr='>>')

To configure a Tempiny instance :

    T = Tempiny(
      stmt_line_start=PY['stmt_line_start'], # Code prefix. 
      begin_expr=PY['begin_expr'], # Expression delimiter (begin)
      end_expr=PY['end_expr'] # Expression delimiter (end)
    )

Note that you can use any string for these tokens.

`Tempiny.compile(self, f:Iterable[str], filename='<template>', default_globals={}, default_locals=None) -> Template`:
This method compiles a template. `f` should be an iterable of strings (an open file is ok). `default_globals` is a dict
you can provide to have a default global scope when calling the template. You should probably leave `default_locals`
to None except if you know what you are doing.

Example :

    with open('test_template', 'r') as f:
      template = T.compile(f, 'test_template')


`Template.__call__(self, out_stream, _globals={}, _locals=None) -> (dict, Exception)`
This method permits to call the template, outputting in `out_stream` (it should at least have a `write(s:str)` method.
You can provide a global scope (it will be shallow-copied before entering the template) through `_globals` to 
pass values to the template. You can also provide a local scope through `_locals`, but it can lead to unexpected
behaviour (not defined errors inside function or list-comprehension). Except if you know what to do, let it None, it
will contain the same content as the globals.
It returns the new locals (to retrieve names defined or modified from the template), and None if no exception occurred,
or the exception if one raised.

Example:

    with open('result', 'w') as f:
      template(f, {'author': 'Léo Flaventin Hauchecorne', 'date' : 2016})

    
# License Notice

Tempiny is a tiny template engine
Copyright © 2016-2020 Léo Flaventin Hauchecorne

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA


