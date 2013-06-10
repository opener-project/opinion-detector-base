'''
Created on May 8, 2013

@author: ruben
'''

import os
import codecs
from VUKafParserPy import KafParser


class My_annotations:
	def __init__(self, tag_filename):
		self.anots = {}
		if os.path.exists(tag_filename):
			fic = codecs.open(tag_filename, 'rb', 'utf-8')
			self.anots = {}
			for line in fic:
				fields = line.split('\t')
				token_id = fields[0]
				token = fields[1]
				lemma = fields[2]
				polarity = fields[5]
				pol_id = fields[6]
				ty = fields[7]
				id_type = fields[8]
				self.anots[token_id] = (polarity, pol_id, ty, id_type, token)
			
	def get_token(self, token_id):
		if token_id in self.anots:
			return self.anots[token_id][4]
		return 'NONE'
			
	# # Possible polarities in our training corpus
	# # 119 contrastMarker
	# # 397 intensifier
	# # 334 negative
	# # 242 negativeFactual --> negative
	# # 22 negativeStrong	--> negative
	# # 82 opinionMarker	--> ""
	# # 190 polarityShifter
	# # 872 positive
	# # 290 positiveFactual
	# # 103 positiveStrong
	# # 127 weakener
	def get_polarity(self, token_id):
		final_pol = None
		pol_id = '-1'
		if token_id in self.anots:
			final_pol = self.anots[token_id][0]
			pol_id = self.anots[token_id][1]
			# Map some values:
			if final_pol == "negativeFactual": final_pol = 'negative'
			elif final_pol == "negativeStrong": final_pol = 'negative'
			elif final_pol == "positiveFactual": final_pol = 'positive'	
			elif final_pol == "positiveStrong": final_pol = 'positive'
		if final_pol == '':
			final_pol = None
		return final_pol,pol_id
	
		
	# # Possible values for the opinion element in our corpus
	# #	94 negativeExpression
	# # 85 opinionHolder
	# # 137 opinionTarget
	# # 129 positiveExpression
	# # 25 strongNegativeExpression
	# # 64 strongPositiveExpression
	def get_opinion_element(self, token_id):
		final_opi = None
		ele_id = '-1'
		if token_id in self.anots:
			final_opi = self.anots[token_id][2]
			ele_id = self.anots[token_id][3]
			
			# Doing some mapping to simplify the problem
			if final_opi == 'strongNegativeExpression': final_opi = 'negativeExpression'
			elif final_opi == 'strongPositiveExpression': final_opi = 'positiveExpression'
		if final_opi == '': final_opi = None
		return final_opi,ele_id
		
	def is_empty(self):
		return len(self.anots) == 0
		


class My_kaf:
	def __init__(self,kaf_filename):
		kaf_obj = KafParser(kaf_filename)
		## Extracting tokens
		self.token_data = {} ## token_data['w_1'] = ('house','s_1')
		self.tokens_in_order = []
		for token, s_id, w_id in kaf_obj.getTokens(): 
			self.token_data[w_id] = (token,s_id)
			self.tokens_in_order.append(w_id)
			
		## Extracting terms
		self.term_data = {}
		self.term_for_token = {}
		for term_obj in kaf_obj.getTerms():
			term_id = term_obj.getId()
			term_lemma = term_obj.getLemma()
			term_pos = term_obj.getPos()
			term_span = term_obj.get_list_span()
			self.term_data[term_id] = (term_lemma,term_pos,term_span)
			for tok_id in term_span:
				self.term_for_token[tok_id] = term_id
				
		## Extracting entities
		self.entity_for_term = {}
		for ent_obj in kaf_obj.getSingleEntities():
			for t_id in ent_obj.get_span():
				self.entity_for_term[t_id] = ent_obj.get_type()
			
		self.property_for_term = {}
		for prop_obj in kaf_obj.getSingleProperties():
			for t_id in prop_obj.get_span():
				self.property_for_term[t_id] = prop_obj.get_type()
	
	def get_token_sent(self,my_id):
		return self.token_data[my_id]
	
	
	
	def get_lemma_pos_span(self,my_id):
		term_id = self.term_for_token[my_id]
		return self.term_data[term_id]
	
	def get_entity(self,my_token_id):
		term_id = self.term_for_token[my_token_id]
		return self.entity_for_term.get(term_id)

	
	def get_property(self,my_token_id):
		term_id = self.term_for_token[my_token_id]
		return self.property_for_term.get(term_id)	
	
	def get_tokens_in_order(self):
		for token in self.tokens_in_order: yield token
				
				