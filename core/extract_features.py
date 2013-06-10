from my_classes import My_annotations,My_kaf
import sys


def resolve_polarity(pol_ch, pol_fe):
    if pol_ch != None:
        return pol_ch
    else:
        return pol_fe

def resolve_element(ele_ch, ele_fe):
    if ele_ch != None:
        return ele_ch
    else:
        return ele_fe

def process_file(kaf_filename, tag_file_chantal, tag_file_femke):
    kaf_obj = My_kaf(kaf_filename)
    anots_chantal = My_annotations(tag_filename_chantal)
    anots_femke = My_annotations(tag_filename_femke)
    
    
    previous_ids = ('-1','-1')
    previous_sent = None
    for t_id in kaf_obj.get_tokens_in_order():
        token,sent = kaf_obj.get_token_sent(t_id)
        lemma,pos,_ = kaf_obj.get_lemma_pos_span(t_id)
        my_entity = str(kaf_obj.get_entity(t_id))
        my_property = str(kaf_obj.get_property(t_id))
        
        
        polarity_chantal,id_pol_ch = anots_chantal.get_polarity(t_id)
        polarity_femke,id_pol_fe = anots_femke.get_polarity(t_id)
        polarity_solved = str(resolve_polarity(polarity_chantal, polarity_femke))
        
        element_chantal,id_ele_ch = anots_chantal.get_opinion_element(t_id)
        element_femke,id_ele_fe = anots_femke.get_opinion_element(t_id)
        element_solved = resolve_element(element_chantal, element_femke)
        
        print>>sys.stderr,t_id, token.encode('utf-8'), 'lemma',lemma.encode('utf-8'),
        print>>sys.stderr, pos.encode('utf-8'), 'ent',str(my_entity).encode('utf-8'), 'prop',str(my_property).encode('utf-8')
        print>>sys.stderr, '\tPolarities'
        print>>sys.stderr, '\t\ttpol_chantal', str(polarity_chantal).encode('utf-8'),str(id_pol_ch).encode('utf-8')
        print>>sys.stderr, '\t\tpol_femke',str(polarity_femke).encode('utf-8'),str(id_pol_fe).encode('utf-8')
        print>>sys.stderr, '\t\tpol_solved',str(polarity_solved).encode('utf-8')
        print>>sys.stderr, '\tOpinion element'
        print>>sys.stderr, '\t\tChantal',str(element_chantal).encode('utf-8'),str(id_ele_ch).encode('utf-8')
        print>>sys.stderr, '\t\tFemke',str(element_femke).encode('utf-8'),str(id_ele_fe).encode('utf-8')
        print>>sys.stderr, '\t\tSolved',str(element_solved).encode('utf-8')
        #Printing the features
        
        
        if element_solved is None:
            my_class = 'O'
            previous_ids = ('-1','-1')
        else:
            if id_ele_ch == previous_ids[0] or id_ele_fe == previous_ids[1]:
                my_class = 'I-'+element_solved
            else:
                previous_ids = (id_ele_ch,id_ele_fe)
                my_class = 'B-'+element_solved
            
            common = (previous_ids and set([id_ele_ch,id_ele_fe]))
            
        if previous_sent is not None and sent != previous_sent:
            print   # EMpty line
        
        previous_sent = sent
        print token.encode('utf-8')+'\t'+pos.encode('utf-8')+'\t'+lemma.encode('utf-8')+'\t'+my_entity.encode('utf-8')+'\t'+my_property.encode('utf-8')+'\t'+polarity_solved.encode('utf-8')+'\t'+my_class.encode('utf-8')
    print #Crfsuite requires an empty line at the end
        
        
    

if __name__ == '__main__':
    ##file_corpus_en = 'opinion_corpus_en.list'
    ##file_corpus_nl = 'opinion_corpus_nl.list'
    
    if len(sys.argv) == 1 :
        print>>sys.stderr,'Usage: '+sys.argv[0]+' opinion_corpus.list'
        print>>sys.stderr,'Example: '+sys.argv[0]+' opinion_corpus_(en|nl).list'
        sys.exit(-1)
    
    file_corpus = sys.argv[1]   
    fic = open(file_corpus,'r')
    for line in fic:
        kaf_filename = line.strip()
        tag_filename_chantal = kaf_filename[:-4]+'.tag.chantal'
        tag_filename_femke = kaf_filename[:-4]+'.tag.femke'
        print>>sys.stderr,'Processing ',kaf_filename
        process_file(kaf_filename, tag_filename_chantal, tag_filename_femke)
    fic.close()
    print>>sys.stderr,"DONE OK!!"
    sys.exit(0)
        
    
  

    
