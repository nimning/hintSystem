def answer_filter(answer_string, parse_tree, eval_tree, correct_string, correct_tree, correct_eval, user_vars):
   def flatten(tree):
      if len(tree)==1:
        return tree
      elif len(tree)==2:
      	return tree[0]+flatten(tree[1])
      elif len(tree)==3:
      	return tree[0]+flatten(tree[1])+flatten(tree[2])
      else:
        return 'error, len(tree)='+str(len(tree))
  
   if len(eval_tree) > 1:
      print answer_string,eval_tree,'flatten=',flatten(eval_tree)
      return True
   else:
      return False
