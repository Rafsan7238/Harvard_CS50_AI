import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP Conj VP | S Conj S
NP -> N | Det NP | NP PP | Det AP NP
VP -> V | V NP | V PP | V NP PP | Adv VP | VP Adv
AP -> Adj | Adj AP
PP -> P S | P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    word_list = []

    # regex to select words with at least 1 alphabetic character   
    pattern = re.compile('[a-z]')

    sentence = sentence.lower()
    words = nltk.word_tokenize(sentence)

    word_list = [word for word in words if pattern.match(word)]
    return word_list


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    
    np_chunks = []

    # traverse all the subtrees of type NP, and append it to np_chunks if it doesn't contain any other NP subtree
    for subtree in tree.subtrees(lambda t: t.label() == 'NP'):
        if not contains_NP_subtrees(subtree):
            np_chunks.append(subtree)

    return np_chunks


def contains_NP_subtrees(tree):

    """
    Return True if the tree contains any subtree of NP type, else return False.
    """

    for subtree in tree.subtrees():

        if subtree == tree:
            continue

        elif subtree.label() == 'NP':
            return True

    return False


if __name__ == "__main__":
    main()
