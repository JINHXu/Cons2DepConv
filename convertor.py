#!/usr/bin/env python3

""" Data Structures and Algorithms for CL III, Assignment 6
    See <https://dsacl3-2019.github.io/a6/> for detailed instructions.
    Course:      Data Structures and Algorithms for CL III - WS1920
    Assignment:  lab 6
    Author:      Jinghua Xu
    Description: A constituency to dependency parsing convertor.
    
    Honor Code:  I pledge that this program represents my own work.
"""

# hint: not a lot of coding

from dataclasses import dataclass
from typing import List

import xml.etree.ElementTree as et

@dataclass
class Node:
    """Representation of a node in a dependency graph.
    
    Attributes:
        word (str): The word form.
        id (int): The id of the node.
        lemma (str): The lemma.
        pos (str): The part of speech tag.
        cs_nodes (List): The list of the constituency nodes (useful for labeling the relation). 
        relation (Relation): The dependency relation, it defines the head node for this node.
        children (List): The list of nodes marked as children of this node.
    """
    word: str
    id: int
    lemma: str
    pos: str
    cs_nodes: List
    relation: 'Relation'
    children: List

    def __repr__(self):
        if self.children:
            return f'{self.word}:{self.id} {self.children}'
        else:
            return f'{self.word}:{self.id}'

@dataclass
class Relation:
    """Representation of a relation in a dependency graph.
    
    Attributes:
        label (str): The relation label.
        head (Node): The head node.
    """
    label: str
    head: Node

def get_label(child, head):
    """Creates the label for the dependency relation between the child node and its head.
    
    Parameters
    ----------
    child : Node
        The dependent node.
    head : Node
        The head node.

    Returns
    -------
    label : string
        The label of the dependency relation.

    """
    # FIXME your code goes here


def convert(xml_node):
    """Recursively converts the XML nodes corresponding to a sentence from constituency to dependency parsing.
    
    Parameters
    ----------

    xml_node : 
        A xml.etree.ElementTree node to convert.
    """
    # hints: 20 lines or so
    # finding, for each word in the sentence, the corresponding head word
    # multiple HD annotations collide, and none of the words are marked as the head by the constituency annotation

    # a bfs? implemented recursively

    # FIXME your code goes here
    # traverse the XML tree to construct dependency tree

    sentence_root = Node()
    # create root node
    return sentence_root

def to_conll(out, sentence_root):
    """Writes a sentence to the specified file in conll-x format.
    
    Parameters
    ----------
    out : File
        Output file.
    sentence_root: Node
        The root node of the sentence to be printed out.
    """
    
    # FIXME your code goes here

if __name__ == '__main__':
    with open('data/sample-sentences.xml', mode='r') as in_f:
        tree = et.parse(in_f)

    root = tree.getroot()
    
    with open('data/sample-sentences.conllx', mode='w', encoding='utf8') as out_f:
        for sent in root.findall('.//sentence'):
            sentence_root = convert(sent)
            to_conll(out_f, sentence_root)