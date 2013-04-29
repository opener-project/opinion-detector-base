#!/usr/bin/env python

def extract_groups(my_dict, list_ids):
  prev = 'nothing'
  groups = []
  current = []
  cur_ele = ''
  for t_id in list_ids:
    ele = my_dict.get(t_id,None)
    if ele is not None:
      if ele == prev:
        current.append(t_id)
      else:
        if len(current)!=0:
          groups.append((cur_ele,current))
        current = [t_id]
        cur_ele = ele
    else:
      if len(current) != 0:
        groups.append((cur_ele,current))
      current = [] 
    prev = ele
  if len(current) != 0:
    groups.append((cur_ele,current))
  return groups

def extract_from_opennlp(text,id_list):
  
  type_for_id = {}
  groups = []
  idx = 0
  num_term = 0
  tokens = text.strip().split(' ')
  while idx < len(tokens):
    token = tokens[idx]
    if token[0]=='[' and token.find('_')==-1:
      #The beginning of something...
      type = token[1:]
      idx+=1
      new_group_str = []
      new_group_id = []
      stop = False
      while not stop and tokens[idx]!=']':
        if num_term < len(id_list): id_term = id_list[num_term]
        else: id_term = '-1'
        
        new_group_str.append(tokens[idx])
        new_group_id.append(id_term)
        type_for_id[id_term]=type
        num_term += 1
        idx+=1
        if idx == len(tokens):  ## In some cases opennlp at the end of the line does goed_positive] with no whitespace
          if new_group_str[-1][-1]==']':  ## To remove the glued ] in case
            new_group_str[-1] = new_group_str[-1][:-1]
          stop = True
               
      groups.append((type,new_group_str,new_group_id))
    else:
      num_term += 1
    idx += 1
  return groups,type_for_id
  
def get_min(l):
  min = None
  for ele in l:
    digits = ''
    for c in ele:
      if c.isdigit(): digits+=c
    value = int(digits)
    if min==None or value<min:
      min = value
  return min
  
def get_max(l):
  max = -1
  for ele in l:
    digits = ''
    for c in ele:
      if c.isdigit(): digits+=c
    value = int(digits)
    if value>max:
      max = value
  return max
  
def get_distance(list1, list2):
  min_1 = get_min(list1)
  max_1 = get_max(list1)
  min_2 = get_min(list2)
  max_2 = get_max(list2)
  
  if max_1 < min_2:
    distance = min_2 - max_1
  elif max_2 < min_1:
    distance = min_1 - max_2
  else:
    distance = 0
  return distance
  
    
    
    
if __name__ == "__main__":
  
  t = '[opinionTarget Het_none bed_none ] is_none een_none goedkoop_positiveExpression [opinionTarget het_none ] bed_none'
  t = ' '.join([u'het_none', u'is_none', u'een_none', u'[positiveExpression', u'goedkoop_positive', u']', u'bad_none', u'maar_none', u'douche_none', u'is_none', u'[negativeExpression', u'vies_negative', u']', u'._none'])
  print t
  ids = ['t_13', 't_14', 't_15', 't_16', 't_17', 't_18', 't_19', 't_20', 't_21', 't_22']

  extract_from_opennlp(t,ids)
  