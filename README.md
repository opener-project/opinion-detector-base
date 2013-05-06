VU-opinion-detector-deluxe_NL_EN-kernel
=====================================

Introduction
------------
This module implements the Deluxe version of the opinion mining using Machine Learning and the mallet toolkit (http://mallet.cs.umass.edu/). The module aims to detect
opinions and extract three elements for each opinion:
* Opinion expression
* Opinion holder
* Opinion target

This module works for **English** and **Dutch**, and it has been trained using a small corpus annotated manually by 2 annotators at the VUA. The input of this module has to be a KAF
file, preferably with text, term (with pos and polarity), entity and property layers, as they will be used to extract the features for the system. In case there are some layers missing
in the input KAF, the module will still work, but some features won't be available and the performance can be punished. The output is the KAF file extended with
the opinion layer.

Requirements
-----------
* VUKafParserPy: parser in python for KAF files (https://github.com/opener-project/VU-kaf-parser)
* lxml: library for processing xml in python
* Mallet toolkit: http://mallet.cs.umass.edu

Installation
-----------
The installation of this module is very easy, you need just to clone the repository:
````shell
git clone git@github.com:opener-project/VU-opinion-detector-deluxe_NL_EN-kernel.git
````
Then you need to tell the module where Mallet is installed in your local machine. For this purpose you have to edit the script *core/opinion_miner_mallet.py* and
modify the path of the variable MALLET_PATH to point to your local folder of Mallet.
```shell
## SET THIS VALUE TO YOU LOCAL FOLDER OF MALLET
MALLET_PATH = '/Users/ruben/mallet-2.0.7'
````

Description of the system
-------------------------
The system works in 2 stages:
* Detection of expression
* Detection of holders/targets

We have trained two independent classifiers using the sequential tagger (CRF) of mallet, one for each task. The features used to train the expression detector for
each word are:
* the word itself
* lemma
* part-of-speech
* sentiment polarity (positive, negative, intensifier, weakener, shifter...)

This classifier will output which groups of words define a positive or a negative expression. This information is used as a feature for the target and holder detector,
which specifically uses this set of features for each token:
* the word
* the lemma
* the part-of-speech
* if the word is part of a Named Entity, and the type of entity (person, location,...)
* if the word is part of a property/aspect, and the type of property/aspect (staff, cleanliness,money,...)

The output of this second classifier are the holders and targets for each expression detected in the first step. Finally the system links this information
and generates the final opinion layer in the output KAF.

How to run the system with Python
--------------------------------
You can run this module from the command line using Python. The main script is  core/opinion_miner_mallet_en.py. This script reads the KAF from the standard input
and writes the output to the standard output, generating some log information in the standard error output. To process one file just run:
````shell
cat input.kaf |  core/opinion_miner_mallet.py > output.kaf
````

This will read the KAF file in "input.kaf" and will store the constituent trees in "output.kaf".



Contact
------
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl


