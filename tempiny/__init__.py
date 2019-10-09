
import re
import itertools

expr = re.compile(r'\{\{(?P<expr>.*?)\}\}')
stmt = re.compile(r'^\s*##\s*(?P<stmt>\S.*?(?P<indent>:)?)\s*$')

class Template(object):
  def __init__(self, code, default_globals = {}, default_locals = {}):
    self.code = code
    self.default_globals = default_globals
    self.default_locals = default_locals

  def __call__(self, out_stream, _globals = {}, _locals = {}):
    g = dict(**self.default_globals, **_globals)
    l = dict(**self.default_locals,  **_locals, _OUT=out_stream)
    exec(self.code, g, l)

class Tempiny(object):
  C  = dict(stmt_line_start=r'//#', begin_expr='{{', end_expr='}}')
  PY = dict(stmt_line_start=r'##', begin_expr='{{', end_expr='}}')
  TEX = dict(stmt_line_start=r'%#', begin_expr='<<', end_expr='>>')
  def __init__(self, stmt_line_start=PY['stmt_line_start'], begin_expr=PY['begin_expr'], end_expr=PY['end_expr']):
    self.expr = re.compile(rf'{re.escape(begin_expr)}(?P<expr>.*?){re.escape(end_expr)}')
    self.stmt = re.compile(rf'^\s*{re.escape(stmt_line_start)}\s*(?P<stmt>\S.*?(?P<indent>:)?)\s*$')

  def sumup(self, i, b, args):
    if len(args):
      s = ''.join(b).replace('{', '{{').replace('}', '}}').replace('\x00', '{}') #escape '{'  and '}' for python `str.format`
      return '{}_OUT.write({})'.format('  '*i, repr(s) + '.format({})'.format(', '.join('('+a+')' for a in args )) )
    else:
      return '{}_OUT.write({})'.format('  '*i, repr(''.join(b)))

  def parse(self, lines, out, default_globals = {}, default_locals = {}):
    args = []
    b = []
    i = 0
    for l in lines:
      m = self.stmt.match(l)
      if m:
        if(len(b)):
          out.append(self.sumup(i, b, args))
          b = []
          args = []
        if m.group('stmt') == '-':
          i -= 1
        else:
          out.append('  '*i + m.group('stmt'))
          if m.group('indent') is not None:
            i += 1
      else:
        m = self.expr.search(l)
        while m:
          args.append(m.group('expr'))
          m = self.expr.search(l, m.end())
        b.append(self.expr.sub('\x00', l))
    out.append(self.sumup(i, b, args))

  def compile(self, f, filename = '<template>', default_globals = {}, default_locals = {}):
    """ :f: file-like stream"""
    l = []
    self.parse(iter(f), l)
    src = '\n'.join(l)
    return Template(compile(src, filename, 'exec'), default_globals, default_locals)
  

