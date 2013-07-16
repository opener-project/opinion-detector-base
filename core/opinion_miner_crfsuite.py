#!/usr/bin/env python


import sys
import getopt
from collections import defaultdict
from operator import itemgetter
import logging
from subprocess import Popen,PIPE
from my_lib import extract_groups,get_distance
import tempfile
import os
from feats_to_crf import extract_features

this_folder = os.path.dirname(os.path.realpath(__file__))

# This updates the load path to ensure that the local site-packages directory
# can be used to load packages (e.g. a locally installed copy of lxml).
sys.path.append(os.path.join(this_folder, 'site-packages/pre_build'))
sys.path.append(os.path.join(this_folder, 'site-packages/pre_install'))

from lxml import etree
from VUKafParserPy import KafParser

# Path to the locally installed version of crfsuite.
CRF_SUITE_PATH = os.path.join(this_folder, 'vendor/build/bin/crfsuite')
#CRF_SUITE_PATH = '/Users/ruben/NLP_tools/crfsuite-0.12/bin/crfsuite'

###############################################

#Internal variables, do not modify these ones
__module_dir = os.path.dirname(__file__)
__model_dir = os.path.join(__module_dir,'models')

__crfsuite_model_en = os.path.join(__model_dir,'en','crfsuite.en.19-jun-2013.model')
__crfsuite_model_nl = os.path.join(__model_dir,'nl','crfsuite.nl.19-jun-2013.model')



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
    print>>sys.stderr,'Error parsing input'
    print>>sys.stderr,'Stream input must be a valid KAF file'
    print>>sys.stderr,'Error: ',str(e)
    sys.exit(-1)


my_lang = kaf_obj.getLanguage()

if my_lang == 'nl':
  __crfsuite_model = __crfsuite_model_nl
elif my_lang == 'en':
  __crfsuite_model = __crfsuite_model_en
else:
  print>>sys.stderr,'Error, the language is "'+my_lang+'" and only can be "nl" for Dutch or "en" for English'
  sys.exit(-1)


logging.debug('Language of the KAF file:'+my_lang)
logging.debug('Model for crfsuite '+ __crfsuite_model)

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
  term_id = str(term_obj.getId())
  term_lemma = term_obj.getLemma()
  #if term_lemma is None:
  #  term_lemma = 'None'
  term_pos = term_obj.getPos()
  #if term_pos is None:
  #  term_pos = 'None'
    
  term_span = term_obj.get_list_span()
  polarity = term_obj.get_polarity()
  #if polarity is None: polarity = 'None'
  
  modifier = str(term_obj.get_sentiment_modifier())
  #if modifier is None: modifier = 'None'
  
  #print>>sys.stderr,term_id.encode('utf-8'),term_lemma.encode('utf-8'),term_pos.encode('utf-8'),term_span,polarity.encode('utf-8'),modifier.encode('utf-8')

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



## For each sentence this is the process:
#    1) Extract the features and keep them in a temporary folder
#    2) Call to the program to convert from this features to the CRF features
#    3) Call to the crfsuite tagger
###############
for sent in sentences:
  fic = tempfile.NamedTemporaryFile(delete=False)
  list_term_ids = []

  # Step1 --> extract features
  for t_id in sent:
    token, sent_id = token_data[t_id]
    term_id = term_for_token[t_id]
    list_term_ids.append(term_id)
    term_lemma,term_pos,_,polarity,modifier = term_data[term_id]
    print>>sys.stderr,t_id, term_data[term_id]

    feat_pol = 'None'
    if polarity is None and modifier is None:      feat_pol = 'None'
    elif polarity is not None:      feat_pol = polarity
    elif modifier is not None:      feat_pol = modifier

    feat_ent = entity_for_term.get(term_id,'None')
    feat_prop = property_for_term.get(term_id,'None')


    fic.write(token.encode('utf-8')+'\t')
    fic.write(term_pos.encode('utf-8')+'\t')
    fic.write(term_lemma.encode('utf-8')+'\t')
    fic.write(feat_ent.encode('utf-8')+'\t')
    fic.write(feat_prop.encode('utf-8')+'\t')
    fic.write(feat_pol.encode('utf-8')+'\t')
    fic.write('O\n')
    logging.debug(t_id+' '+token+' '+term_lemma+' '+term_pos+' '+feat_pol)

  fic.write('\n')  #Extra line for crfsuite
  fic.close()

  # Just to print it to the debug
  f_aux = open(fic.name,'r')
  logging.debug('Feature file:\n '+f_aux.read())
  f_aux.close()


  # Step 2 --> convert it to the format of crfsuite
  fic_feats = tempfile.NamedTemporaryFile(delete=False)
  sys.argv = []
  extract_features(fic.name,fic_feats.name)

  #Step 3 --> call to the crfsuite tagger with the model
  crfsuite_tagger_cmd = CRF_SUITE_PATH+' tag -m '+__crfsuite_model+' '+fic_feats.name
  crfsuite_tagger =Popen(crfsuite_tagger_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
  opinion_classes = []
  for out_line in crfsuite_tagger.stdout:
      tag = out_line.strip()
      if tag != '':
          opinion_classes.append(tag)
  logging.debug('Opinion classes: '+' '.join(opinion_classes))
  os.remove(fic.name)
  os.remove(fic_feats.name)
  
  op_exp_groups = extract_groups(opinion_classes,list_term_ids,['positiveExpression','negativeExpression'])
  holder_groups = extract_groups(opinion_classes,list_term_ids,['opinionHolder'])
  target_groups = extract_groups(opinion_classes,list_term_ids,['opinionTarget'])

  logging.debug('Expressions groups: '+str(op_exp_groups))
  logging.debug('Holder groups: '+str(holder_groups))
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

    #my_opinion.map_to_terms(term_for_token)
    opinion_xml = my_opinion.convert_to_xml()
    kaf_obj.addElementToLayer('opinions', opinion_xml)
    logging.debug('OPINION FINAL:'+str(my_opinion))


  ## NEXT SENTENCE


kaf_obj.addLinguisticProcessor('Crfsuite machine learning opinion miner','1.0','opinions', my_time_stamp)
kaf_obj.saveToFile(sys.stdout)
logging.debug('Finished ok')

sys.exit(0)
