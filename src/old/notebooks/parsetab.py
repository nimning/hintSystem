
# parsetab.py
# This file is automatically generated. Do not edit.
_tabversion = '3.2'

_lr_method = 'LALR'

_lr_signature = 'Go\xa2\x90\xa0\xc6\x11\x99\xad\xd9\xaf\x8cv\x1f[\x89'
    
_lr_action_items = {'LBRACKET':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[3,3,-20,3,-21,3,3,3,3,-19,3,3,-15,3,3,3,3,-10,3,3,3,-17,3,3,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'RPAREN':([2,4,10,13,15,16,18,22,23,25,26,27,28,29,30,31,32,33,34,35,36,],[-20,-21,-19,-15,30,31,-10,-17,-8,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'DIVIDE':([2,4,8,10,11,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,17,17,17,-15,17,17,-10,17,-9,-12,-13,-14,-16,-11,-6,-5,17,-7,17,]),'RBRACKET':([2,4,11,13,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,27,-15,-10,-8,-9,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'FACTORIAL':([2,4,8,10,11,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,18,18,18,-15,18,18,-10,18,-9,-12,-13,-14,-16,-11,18,18,18,18,18,]),'NUMBER':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[2,2,-20,2,-21,2,2,2,2,-19,2,2,-15,2,2,2,2,-10,2,2,2,-17,2,2,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'RSET':([2,4,5,10,12,13,14,18,22,23,25,26,27,28,29,30,31,32,33,34,35,36,],[-20,-21,13,-19,28,-15,29,-10,-17,-8,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'TIMES':([2,4,8,10,11,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,19,19,19,-15,19,19,-10,19,-9,-12,-13,-14,-16,-11,-6,-5,19,-7,19,]),'LSET':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[5,5,-20,5,-21,5,5,5,5,-19,5,5,-15,5,5,5,5,-10,5,5,5,-17,5,5,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'PLUS':([2,4,8,10,11,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,20,20,20,-15,20,20,-10,20,-9,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'LPAREN':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[7,7,-20,7,-21,7,7,7,7,-19,7,7,-15,7,7,7,7,-10,7,7,7,-17,7,7,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'VARIABLE':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[4,4,-20,4,-21,4,4,4,4,-19,4,4,-15,4,4,4,4,-10,4,4,4,-17,4,4,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'COMMA':([2,4,8,10,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,22,26,-15,22,22,-10,-8,-9,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'EXP':([2,4,8,10,11,13,14,16,18,23,25,27,28,29,30,31,32,33,34,35,36,],[-20,-21,21,21,21,-15,21,21,-10,21,-9,-12,-13,-14,-16,-11,21,21,21,-7,21,]),'MINUS':([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,],[9,9,-20,9,-21,9,9,24,9,24,24,9,-15,24,9,24,9,-10,9,9,9,-17,24,9,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),'$end':([1,2,4,6,8,10,13,18,22,23,25,26,27,28,29,30,31,32,33,34,35,36,],[-2,-20,-21,0,-1,-19,-15,-10,-17,-8,-9,-18,-12,-13,-14,-16,-11,-6,-5,-3,-7,-4,]),}

_lr_action = { }
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = { }
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'list':([0,5,7,],[1,12,15,]),'expression':([0,1,3,5,7,8,9,10,11,12,14,15,16,17,19,20,21,23,24,25,32,33,34,35,36,],[8,10,11,14,16,23,25,23,23,10,23,10,23,32,33,34,35,23,36,23,23,23,23,23,23,]),'statement':([0,],[6,]),}

_lr_goto = { }
for _k, _v in _lr_goto_items.items():
   for _x,_y in zip(_v[0],_v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = { }
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statement","S'",1,None,None,None),
  ('statement -> expression','statement',1,'p_statement_expr_list','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',95),
  ('statement -> list','statement',1,'p_statement_expr_list','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',96),
  ('expression -> expression PLUS expression','expression',3,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',100),
  ('expression -> expression MINUS expression','expression',3,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',101),
  ('expression -> expression TIMES expression','expression',3,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',102),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',103),
  ('expression -> expression EXP expression','expression',3,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',104),
  ('expression -> expression expression','expression',2,'p_expression_ops','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',105),
  ('expression -> MINUS expression','expression',2,'p_expression_uminus','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',115),
  ('expression -> expression FACTORIAL','expression',2,'p_expression_factorial','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',119),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',123),
  ('expression -> LBRACKET expression RBRACKET','expression',3,'p_expression_group','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',124),
  ('expression -> LSET list RSET','expression',3,'p_expression_set','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',128),
  ('expression -> LSET expression RSET','expression',3,'p_expression_set','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',129),
  ('expression -> LSET RSET','expression',2,'p_expression_set','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',130),
  ('expression -> LPAREN list RPAREN','expression',3,'p_expression_tuple','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',137),
  ('list -> expression COMMA','list',2,'p_nonempty_list','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',141),
  ('list -> list expression COMMA','list',3,'p_nonempty_list','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',142),
  ('list -> list expression','list',2,'p_nonempty_list','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',143),
  ('expression -> NUMBER','expression',1,'p_expression_number_variable','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',150),
  ('expression -> VARIABLE','expression',1,'p_expression_number_variable','/Users/yoavfreund/projects/Webwork.Improvement.Project/AdaptiveHints/src/webwork/expr_parser/webwork_parser.py',151),
]
