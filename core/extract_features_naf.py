#!/usr/bin/env python
import sys

def extract_features_naf(naf_obj):
    
    token_data = {} ## token_data['w_1'] = ('house','s_1')
    tokens_in_order = []
    term_data = {}  # tid --> (term_lemma,term_pos,term_span,polarity,modifier)
    term_for_token = {}
    entity_for_term = {}
    property_for_term = {}
    
    # EXTRACTING TOKENS
    for token in naf_obj.get_tokens():
        w_id = token.get_id()
        token_value = token.get_text()
        sent = token.get_sent()
        token_data[w_id] = (token_value,sent)
        tokens_in_order.append(w_id)
    ######################
    
    for term_obj in naf_obj.get_terms():
        t_id = term_obj.get_id()
        t_lemma = term_obj.get_lemma()
        t_pos = term_obj.get_pos()
        obj_span = term_obj.get_span()
        span_ids = obj_span.get_span_ids()
        senti_obj = term_obj.get_sentiment()
        polarity = modifier = None
        if senti_obj is not None:
            polarity = senti_obj.get_polarity()
            modifier = senti_obj.get_modifier()   
        term_data[t_id] = (t_lemma,t_pos,span_ids,polarity,modifier) 
        for tok_id in span_ids:
            term_for_token[tok_id] = t_id
            
            
    for entity in naf_obj.get_entities():
        ent_id = entity.get_id()
        ent_type = entity.get_type()
        for references in entity.get_references():
            for span_obj in references:
                span_ids = span_obj.get_span_ids()
                for t_id in span_ids:
                    entity_for_term[t_id] = ent_type

    for prop_obj in naf_obj.get_properties():
        prop_type = prop_obj.get_type()
        for references in prop_obj.get_references():
            for span_obj in references:
                span_ids = span_obj.get_span_ids()
                for t_id in span_ids:
                    property_for_term[t_id] = prop_type
                        
    return token_data, tokens_in_order, term_data, term_for_token, entity_for_term, property_for_term
  
  
  