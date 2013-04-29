#!/usr/bin/env python

from lxml import etree
import sys
import getopt
from VUKafParserPy import KafParser
from collections import defaultdict
from operator import itemgetter
import logging
from subprocess import Popen,PIPE
from my_lib import extract_groups,get_distance
import tempfile
import os

## SET THIS VALUE TO YOU LOCAL FOLDER OF MALLET
MALLET_PATH = '/Users/ruben/mallet-2.0.7'

###############################################

#Internal variables, do not modify these
__module_dir = os.path.dirname(__file__)
__mallet_class_path = os.path.join(MALLET_PATH,'class')+':'+os.path.join(MALLET_PATH,'lib','mallet-deps.jar')
__mallet_model_exp = os.path.join(__module_dir,'models','model.mallet.exp.en')
__mallet_model_hol_tar = os.path.join(__module_dir,'models','model.mallet.hol.tar.en')


class Opinion:
  def __init__(self):
    self.polarity = ''
    self.strength = 1
    self.exp_ids = []
    self.tar_ids = []
    self.hol_ids = []
    
  
  def map_to_terms(self,mapping):
    ##Map exp_ids
    aux = self.exp_ids[:]
    self.exp_ids = []
    for t_id in aux:
      term = mapping.get(t_id)
      if term not in self.exp_ids: self.exp_ids.append(term)
    
    aux = self.tar_ids[:]
    self.tar_ids = []
    for t_id in aux:
      term = mapping.get(t_id)
      if term not in self.tar_ids: self.tar_ids.append(term)
      
    aux = self.hol_ids[:]
    self.hol_ids = []
    for t_id in aux:
      term = mapping.get(t_id)
      if term not in self.hol_ids: self.hol_ids.append(term)
    
    
  def __repr__(self):
    s = 'Polarity ' + self.polarity
    
    s += '\nStrength: '+str(self.strength)
    s += '\nExpression ids: '+' '.join(self.exp_ids)
    s += '\nTarget ids: ' + ' '.join(self.tar_ids)
    s += '\nHolder ids: ' + ' '.join(self.hol_ids)
    return s
    
  def convert_to_xml(self):
    op_ele = etree.Element('opinion')
    
    ## Holder
    op_hol = etree.Element('opinion_holder')
    op_ele.append(op_hol)
    span_op_hol = etree.Element('span')
    op_hol.append(span_op_hol)
    for id in self.hol_ids:
      span_op_hol.append(etree.Element('target',attrib={'id':id}))
   
    ## TARGET
    op_tar = etree.Element('opinion_target')
    op_ele.append(op_tar)
    span_op_tar = etree.Element('span')
    op_tar.append(span_op_tar)
    for id in self.tar_ids:
      span_op_tar.append(etree.Element('target',attrib={'id':id}))   
     
    ## Expression
    pol = self.polarity
    if pol == 'positiveExpression': pol='positive'
    elif pol == 'negativeExpression': pol='negative'
    op_exp = etree.Element('opinion_expression',attrib={'polarity':pol,
                                                       'strength':str(self.strength)})
    op_ele.append(op_exp)
    span_exp = etree.Element('span')
    op_exp.append(span_exp)
    for id in self.exp_ids:
      span_exp.append(etree.Element('target',attrib={'id':id}))
    
    ##
    return op_ele

  

######## MAIN ROUTINE ############                

## Check if we are reading from a pipeline
if sys.stdin.isatty():
    print>>sys.stderr,'Input stream required.'
    print>>sys.stderr,'Example usage: cat myUTF8file.kaf.xml |',sys.argv[0]
    sys.exit(-1)
########################################

logging.basicConfig(stream=sys.stderr,format='%(asctime)s - %(levelname)s\n\t%(message)s',level=logging.DEBUG)


## Processing the parameters
my_time_stamp = True
try:
    opts, args = getopt.getopt(sys.argv[1:],"",["no-time"])
    for opt, arg in opts:
        if opt == "--no-time":
            my_time_stamp = False
except getopt.GetoptError:
    pass
#########################################

logging.debug('Include timestamp: '+str(my_time_stamp))

# Parsing the KAF file
try:
    kaf_obj = KafParser(sys.stdin)
except Exception as e:
    print>>sys.stdout,'Error parsing input'
    print>>sys.stdout,'Stream input must be a valid KAF file'
    print>>sys.stdout,'Error: ',str(e)
    sys.exit(-1)
    
    
lang = kaf_obj.getLanguage()

if lang != 'en':
  print>>sys.stdout,'Language error in KAF. Found '+lang+' and must be en (English)'
  sys.exit(-1)
  
## Extracting tokens
token_data = {} ## token_data['w_1'] = ('house','s_1')
tokens_in_order = []
for token, s_id, w_id in kaf_obj.getTokens(): 
  token_data[w_id] = (token,s_id)
  tokens_in_order.append(w_id)

  
## Extracting terms
term_data = {}
term_for_token = {}
for term_obj in kaf_obj.getTerms():
  term_id = term_obj.getId()
  term_lemma = term_obj.getLemma()
  term_pos = term_obj.getPos()
  term_span = term_obj.get_list_span()
  polarity = term_obj.get_polarity()
  modifier = term_obj.get_sentiment_modifier()
  print>>sys.stderr,term_id,term_lemma,term_pos,term_span,polarity,modifier
  
  term_data[term_id] = (term_lemma,term_pos,term_span,polarity,modifier)
  for tok_id in term_span:
    term_for_token[tok_id] = term_id
  
## Extracting entities
entity_for_term = {}
for ent_obj in kaf_obj.getSingleEntities():
  for t_id in ent_obj.get_span():
    entity_for_term[t_id] = ent_obj.get_type()
print>>sys.stderr,'Entities:'+str(entity_for_term)
  
## Extracting properties
property_for_term = {}
for prop_obj in kaf_obj.getSingleProperties():
  for t_id in prop_obj.get_span():
    property_for_term[t_id] = prop_obj.get_type()
print>>sys.stderr,'Properties:'+str(property_for_term)

    
    
## Detect the opinion expressions
## Features:
## tok#Our lem#our pos#Q pol#NoPol
## Possible values for pol: 4642 NoPol
## intensifier
## negative
## polarityShifter
## positive
## weakener

sentences = []
previous = 'BEGIN'
current = []
for t_id in tokens_in_order:
  _,sent_id = token_data[t_id]
  if previous == 'BEGIN' or sent_id == previous:
    current.append(t_id)
  else:
    sentences.append(current)
    current = [t_id]
  previous = sent_id
if len(current)!=0: sentences.append(current)

    
    
for sent in sentences:
  ## For each sentence
  fic = tempfile.NamedTemporaryFile(delete=False)

  for t_id in sent:
    token, sent_id = token_data[t_id]
    term_id = term_for_token[t_id]
    term_lemma,term_pos,_,polarity,modifier = term_data[term_id]
    feat_pol = ''
    if polarity is None and modifier is None:
      feat_pol = 'NoPol'
    elif polarity is not None:
      feat_pol = polarity
    elif modifier is not None:
      feat_pol = modifier
    else:
      feat_pol = 'NoPol'
  
    fic.write('tok#'+token.encode('utf-8'))
    fic.write(' lem#'+term_lemma.encode('utf-8'))
    fic.write(' pos#'+term_pos.encode('utf-8'))
    fic.write(' pol#'+feat_pol.encode('utf-8'))
    fic.write('\n')
    logging.debug(t_id+' '+token+' '+term_lemma+' '+term_pos+' '+feat_pol)
    
  fic.close()
  
  ## How to call to the mallet...
  #java -cp "/Users/ruben/mallet-2.0.7/class:/Users/ruben/mallet-2.0.7/lib/mallet-deps.jar"
  #cc.mallet.fst.SimpleTagger --model-file $1 $2
  input_file_exp = fic.name
  cmd = 'java -cp "'+__mallet_class_path+'" cc.mallet.fst.SimpleTagger --model-file '+__mallet_model_exp+' '+input_file_exp
  exp_pro = Popen(cmd,stdout=PIPE,shell=True)
  output_exp = exp_pro.stdout.readlines()
  exp_pro.terminate()
  os.remove(input_file_exp)
  logging.debug('Temporary file for opinion expression detection '+input_file_exp)
  
  ##Associate with output
  opinion_exp_for_token = {}
  for idx in range(len(sent)):
    t_id = sent[idx]
    opinion_exp = output_exp[idx].strip()
    if opinion_exp in ['positiveExpression','negativeExpression']:
      opinion_exp_for_token[t_id]=opinion_exp
    ## Possible values of opinion_exp: NoExp  positiveExpression  negativeExpression

  logging.debug('Opinion expressions for tokens: '+str(opinion_exp_for_token))
  
  ## Now holders and targets
  ## Example features tok#this lem#this pos#D exp#NoOpExp ent#NoEnt prop#NoProp NoTarOrHol
  fic2 = tempfile.NamedTemporaryFile(delete=False)

  for t_id in sent:
    token, sent_id = token_data[t_id]
    term_id = term_for_token[t_id]
    term_lemma,term_pos,_,polarity,modifier = term_data[term_id]
    
    feat_op_exp = opinion_exp_for_token.get(t_id,'NoOpExp')
    feat_ent = entity_for_term.get(term_id,'NoEnt')
    feat_prop = property_for_term.get(term_id,'NoProp')
    
    fic2.write('tok#'+token.encode('utf-8'))
    fic2.write(' lem#'+term_lemma.encode('utf-8'))
    fic2.write(' pos#'+term_pos.encode('utf-8'))
    fic2.write(' exp#'+feat_op_exp.encode('utf-8'))
    fic2.write(' ent#'+feat_ent.encode('utf-8'))
    fic2.write(' prop#'+feat_prop.encode('utf-8'))
    fic2.write('\n')
  fic2.close()
  
  ## Calling to the mallet classifier
  input_file_hol_tar = fic2.name
  cmd = 'java -cp "'+__mallet_class_path+'" cc.mallet.fst.SimpleTagger --model-file '+__mallet_model_hol_tar+' '+input_file_hol_tar
  exp_hol_tar = Popen(cmd,stdout=PIPE,shell=True)
  output_hol_tar = exp_hol_tar.stdout.readlines()
  exp_hol_tar.terminate()
  os.remove(input_file_hol_tar)
  logging.debug('Temporary file for opinion target/holder detection '+input_file_hol_tar)
  
  ##Associate with output
  holder_for_token = {}
  target_for_token = {}
  for idx in range(len(sent)):
    t_id = sent[idx]
    opinion_element = output_hol_tar[idx].strip()
    if opinion_element == 'opinionTarget':
      target_for_token[t_id] = opinion_element
    elif opinion_element == 'opinionHolder':
      holder_for_token[t_id] = opinion_element
      
  logging.debug('Holders for tokens: '+str(holder_for_token))
  logging.debug('Targets for tokens: '+str(target_for_token))
  
  
  # Print now get all the information in the form of "chunks" and assign expressions, targets and holders
  ## Detecting opinion expressions
  #opinion_exp_for_token['w_2']='negativeExpression'
  #opinion_exp_for_token['w_3']='negativeExpression'
  #opinion_exp_for_token['w_1']='positiveExpression'
  #opinion_exp_for_token['w_7']='negativeExpression'
  

  #print 'EXTRACTING EXPRESSIONS'
  #for t_id in sent:
  #  print t_id,opinion_exp_for_token.get(t_id)
  op_exp_groups = extract_groups(opinion_exp_for_token,sent)
  logging.debug('Expressions groups: '+str(op_exp_groups))
  
  
  #print 'EXTRACTING HOLDERS'
  #holder_for_token['w_10']='opinionHolder'
  #holder_for_token['w_12']='opinionHolder'

  #for t_id in sent:
  #  print t_id,holder_for_token.get(t_id)
  holder_groups = extract_groups(holder_for_token,sent)
  logging.debug('Holder groups: '+str(holder_groups))
  
  #print 'EXTRACTING TARGETS'
  #for t_id in sent:
  #  print t_id,target_for_token.get(t_id)
  target_groups = extract_groups(target_for_token,sent)
  logging.debug('Target groups: '+str(target_groups))


  ## Linking stuff
  for exp in op_exp_groups:

    pol, ids = exp
    logging.debug('Resolving expression:'+pol+' '+str(ids))

    my_opinion = Opinion()
    my_opinion.polarity = pol
    my_opinion.exp_ids = ids
    
    #Look for target
    candi_tar = []
    for tar in target_groups:
      _,tar_ids = tar
      distance = get_distance(my_opinion.exp_ids,tar_ids)
      candi_tar.append((tar_ids,distance))
      logging.debug('Candidate target '+str(tar_ids)+' distance:'+str(distance))
    if len(candi_tar) != 0 :
      candi_tar_sorted = sorted(candi_tar,key=itemgetter(1),reverse=True)
      my_opinion.tar_ids = candi_tar_sorted[0][0]
    #####
    
    #Look for holder
    candi_hol = []
    for hol in holder_groups:
      _,hol_ids = hol
      distance = get_distance(my_opinion.exp_ids,hol_ids)
      logging.debug('Candidate holder '+str(hol_ids)+' distance:'+str(distance))

      candi_hol.append((hol_ids,distance))
    if len(candi_hol) != 0 :
      candi_hol_sorted = sorted(candi_hol,key=itemgetter(1),reverse=True)
      my_opinion.hol_ids = candi_hol_sorted[0][0]
      
    my_opinion.map_to_terms(term_for_token)
    opinion_xml = my_opinion.convert_to_xml()
    kaf_obj.addElementToLayer('opinions', opinion_xml)
    logging.debug('OPINION FINAL:'+str(my_opinion))

  
  ## NEXT SENTENCE
kaf_obj.addLinguisticProcessor('Mallet machine learning opinion miner','1.0','opinions', my_time_stamp)    
kaf_obj.saveToFile(sys.stdout)
logging.debug('Finished ok')

sys.exit(0)