#!/usr/bin/env python

# Separator of field values.
separator = '\t'

# Field names of the input data.
fields = 'tok pos lem ent pro pol y'

# Attribute templates.
templates = (
    (('tok', -3), ),
    (('pos', -3), ),
    (('lem', -3), ),
    (('ent', -3), ),
    (('pro', -3), ),
    (('pol', -3), ),

    (('tok', -2), ),
    (('pos', -2), ),
    (('lem', -2), ),
    (('ent', -2), ),
    (('pro', -2), ),
    (('pol', -2), ),

    (('tok', -1), ),
    (('pos', -1), ),
    (('lem',  -1), ),
    (('ent', -1), ),
    (('pro', -1), ),
    (('pol',  -1), ),
    
    (('tok', 0), ),
    (('pos', 0), ),
    (('lem',  0), ),
    (('ent', 0), ),
    (('pro', 0), ),
    (('pol',  0), ),
    (('tok', 1), ),
    (('pos', 1), ),
    (('lem',  1), ),
    (('ent', 1), ),
    (('pro', 1), ),
    (('pol',  1), ),
    (('tok', 2), ),
    (('pos', 2), ),
    (('lem', 2), ),
    (('ent', 2), ),
    (('pro', 2), ),
    (('pol',  2), ),
    (('tok', 3), ),
    (('pos', 3), ),
    (('lem', 3), ),
    (('ent', 3), ),
    (('pro', 3), ),
    (('pol', 3), ),
    (('tok',-1),('tok',0)),
    (('pos',-1),('pos',0)),
    (('lem',-1),('lem',0)),
    (('pol',-1),('pol',0)),
    (('tok',0),('tok',1)),
    (('pos',0),('pos',1)),
    (('lem',0),('lem',1)),
    (('pol',0),('pol',1)),
    (('tok',-1),('tok',0),('tok',1)),
    (('pos',-1),('pos',0),('pos',1)),
    (('lem',-1),('lem',0),('lem',1)),
    (('pol',-1),('pol',0),('pol',1)),
    (('tok',-2),('tok',-1),('tok',0)),
    (('pos',-2),('pos',-1),('pos',0)),
    (('lem',-2),('lem',-1),('lem',0)),
    (('tok',0),('tok',1),('tok',2)),
    (('pos',0),('pos',1),('pos',2)),
    (('lem',0),('lem',1),('lem',2)),
    )


import crfutils

def feature_extractor(X):
    # Apply attribute templates to obtain features (in fact, attributes)
    crfutils.apply_templates(X, templates)
    if X:
	# Append BOS and EOS features manually
        X[0]['F'].append('__BOS__')     # BOS feature
        X[-1]['F'].append('__EOS__')    # EOS feature



def extract_features(inputfile,outputfile):
  fi = open(inputfile,'r')
  fo = open(outputfile,'w')
  crfutils.main(feature_extractor,fields=fields,sep=separator,fi=fi,fo=fo)
  fi.close()
  fo.close()
  

if __name__ == '__main__':
    crfutils.main(feature_extractor, fields=fields, sep=separator)


