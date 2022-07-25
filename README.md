# Syn2Vec

Official repository for the paper titled "Syn2Vec: Synset Colexification Graphs for Lexical Semantic Similarity"

## Overview: 
Code is split into two main parts. Everything in BabelNet_java_code is needed to grab all necessary 
information from BabelNet using the Java API. This generates several (large) files that are then processed 
in python. Everything in syn2vec contains all python code to:

1. Generate full synset colexification graph using all lexemes from all 499 languages.
2. Embed the generated graph --> gives us synset (node) embeddings
3. Construct word embeddings for evaluation words.
4. Evaluate on LSIM task.

All steps below clearly indicate whether the code for that step
is under BabelNet_java_code or syn2vec. We
have split the steps in this way because we ran the code in BabelNet_java_code
on a local machine and the code in syn2vec on a larger server.

## Step-by-step:

### Setup

To get the BabelNet Java API up and running, visit https://babelnet.org/guide. 
You will also need the BabelNet indices downloaded offline. You must request
the download from the Sapienza NLP group, see https://babelnet.org/downloads for details.
In all three java scripts, you will need to set input/output directories to what you want
before running. 

For all python code, please run from 

src/syn2vec/

since many directories are hard-coded as relative paths. Download
multisimlex from https://multisimlex.com/#download. Files must be
downloaded individually. Then place each file into 

src/syn2vec/datasets/multisimlex/

### Generate full synset colexification graph

#### BabelNet Java Code

Export the BabelNet database into text files whose lines have the form:

LANG\~BabelSynsetID\~lexeme

by running syn2vec_getAllSynsetsBabelNet_iterator.java.

Export synset type information into text files whose lines have the form:

BabelSynsetID\~type

by running syn2vec_getBablNetSynsetTypes.java.

#### Syn2Vec code

Next, run colexAllBabelNet.py. Set --exp_dir to where you want all experiment
files to be saved. Set --synset_text_files_dir and --synset_types_files_dir to
the output directories from the previous BabelNet step.

### Embed the generated graph

#### Syn2Vec code

Run embed_graph.py. Set --input to the .edgelist graph file created from
previous step and --output to the desired location for the node (synset)
embeddings.

### Construct word embeddings for evaluation words

#### Syn2Vec code

First, run generate_eval_wordlists.py to get the evaluation words in Multisimlex.
These will be used to query BabelNet. Set --output_dir to the desired output
location for the files.

#### BabelNet Java Code

Run syn2vec_getSynsetsBabelNet.java,
pointing the script to the files generated from previous step.

#### Syn2Vec code

Run get_word_embeddings.py.
Set --word2syn_dir to the output directory from previous step. Each word
in the evaluation word lists will have its own .pkl embedding file after
this step is complete.

### Evaluate on LSIM task

Run LSIM.py. Set --word_vectors_dir to the output directory from
the previous step (--local_save_folder in get_word_embeddings.py).