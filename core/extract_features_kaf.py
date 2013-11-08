#!/usr/bin/env python
import sys

def extract_features_kaf(kaf_obj):
    
    token_data = {} ## token_data['w_1'] = ('house','s_1')
    tokens_in_order = []
    term_data = {}  # tid --> (term_lemma,term_pos,term_span,polarity,modifier)
    term_for_token = {}
    entity_for_term = {}
    property_for_term = {}
    
    ## Extracting tokens
    for token, s_id, w_id in kaf_obj.getTokens():
        token_data[w_id] = (token,s_id)
        tokens_in_order.append(w_id)


    ## Extracting terms
    for term_obj in kaf_obj.getTerms():
        term_id = str(term_obj.getId())
        term_lemma = term_obj.getLemma()
        term_pos = term_obj.getPos()
        term_span = term_obj.get_list_span()
        polarity = term_obj.get_polarity()
        modifier = str(term_obj.get_sentiment_modifier())
        term_data[term_id] = (term_lemma,term_pos,term_span,polarity,modifier)
        for tok_id in term_span:
            term_for_token[tok_id] = term_id
    ##############################
    
    
    
    ## Extracting entities
    for ent_obj in kaf_obj.getSingleEntities():
        for t_id in ent_obj.get_span():
            entity_for_term[t_id] = ent_obj.get_type()
    print>>sys.stderr,'Entities:'+str(entity_for_term)

    ## Extracting properties
    for prop_obj in kaf_obj.getSingleProperties():
        for t_id in prop_obj.get_span():
            property_for_term[t_id] = prop_obj.get_type()
    print>>sys.stderr,'Properties:'+str(property_for_term)
    
    return token_data, tokens_in_order, term_data, term_for_token, entity_for_term, property_for_term
  
  
  