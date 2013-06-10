VU-opinion-detector-deluxe_NL_EN-kernel
=====================================

crfsuite!!!!

Introduction
------------
This module implements the Deluxe version of the opinion mining using Machine Learning and the crfsuite toolkit (http://www.chokkan.org/software/crfsuite/). The module aims to detect
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
* CRFsuite toolkit: http://www.chokkan.org/software/crfsuite/

Installation
------------

The first step is to install the requirements VUKafParserPy and lxml. For the first one, you should go to the GitHub repository (https://github.com/opener-project/VU-kaf-parser) and follow
the instructions there. For the lxml library, given you have pip installed in your machine, you can run one of these commands:
````shell
sudo pip install lxml
sudo pip install -r requirements.txt
````
The file requirements.txt is contained in our repository.

For the installation of crfsuite, you should go the webpage of this tool (http://www.chokkan.org/software/crfsuite/) and follow the installation details under the Download section.

Finall, the installation of this module is very easy, you need just to clone the repository:
````shell
git clone git@github.com:opener-project/VU-opinion-detector-deluxe_NL_EN-kernel.git
````
Then you need to tell the module where crfsuie is installed in your local machine. For this purpose you have to edit the script *core/opinion_miner_crfsuite.py* and
modify the path of the variable CRF_SUITE_PATH to point to your local binary crfsuite executable.
```shell
## SET THIS VALUE TO YOU LOCAL FOLDER OF MALLET
CRF_SUITE_PATH = 'Users/ruben/NLP_tools/crfsuite-0.12/bin/crfsuite'
````

Description of the system
-------------------------

We have trained two classifiers using the sequential tagger (CRF) of mallet, one English and one for Dutch. The features used to train the expression detector for
each word are:
* the word itself
* lemma
* part-of-speech
* sentiment polarity (positive, negative, intensifier, weakener, shifter...)
* Hotel property of the word
* Named entity of the word


This classifier will output which groups of words define an opinion, as well as its entities (expression, target and holder)

How to run the system with Python
--------------------------------
You can run this module from the command line using Python. The main script is  core/Users/ruben/NLP_tools/crfsuite-0.12/bin/crfsuite'.py. This script reads the KAF from the standard input
and writes the output to the standard output, generating some log information in the standard error output. To process one file just run:
````shell
cat input.kaf |  core/opinion_miner_crfsuite.py > output.kaf
````

This will read the KAF file in "input.kaf" and will store the constituent trees in "output.kaf".

How to train a new model using your annotated data
--------------------------------------------------
Further explanation on how to train a new model using crfsuite and KAF files can be found in the file core/README.train




Contact
------
* Ruben Izquierdo
* Vrije University of Amsterdam
* ruben.izquierdobevia@vu.nl


