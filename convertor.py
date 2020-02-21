#!/usr/bin/env python3

""" Data Structures and Algorithms for CL III, Assignment 6
    See <https://dsacl3-2019.github.io/a6/> for detailed instructions.
    Course:      Data Structures and Algorithms for CL III - WS1920
    Assignment:  lab 6
    Author:      Jinghua Xu
    Description: A constituency to dependency parsing convertor.
    
    Honor Code:  I pledge that this program represents my own work.
"""

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
    
    Return
    ------
    dependency_node :
        The converted xml_node which is the corresponding node in dependency parsing.
    """

    # traverse the XML tree top-dwon and label the head of each constituent by adding atrribute(HEAD): value(HEADID) pairs to each XML node
    mark_head(xml_node)

    # for each word find its head bottom-up: backtracking from each word node
    for word_node in xml_node.findall('.//word'):
        



    # build the nodes
    return

def mark_head(xml_node):
    """
    Helper function of convert(): traverse the XML tree top-down and mark the head for each node(comstituent), and mark constituent for later backtracking

    Parameters
    ----------
    xml_node : A xml.etree.ElementTree node to start the top-down traversal from.
    """
    # not hitting the terminal node
    if xml_node.tag != 'word':
        children_HD = []
        children_nonHD = []
        
        # each DIRECT child node of current node
        for node in xml_node.findall('node'):
            ## Heuristics of determining the head of current node(this constituent):
            ## 1. If there is an explicitly marked head within a constituent (HD annotation), the head of the marked constituent is the head
            ## 2. Otherwise, if there is no head marking but you have LK, use the head of it as the head
            ## 3. And if none of the above(multiple hd), choose the leftmost element.

            if node.attrib['func'] == "HD":
                children_HD.append(node)
            else:
                if node.attrib['cat'] == 'LK':
                    children_nonHD.append(node)
        ## 1.
        if len(children_HD) == 1:
            # head of the current node
            head = children_HD[0]
            # set the func value of the head node
            head.attrib['func'] == 'HD'
            # mark the head of the current node
            xml_node.set('HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])
        
        ## 2.
        elif len(children_HD) == 0:
            no_lkchild = True
            for child in children_nonHD:
                if child.attrib['cat'] == 'LK':
                    no_lkchild = False
                    # set the func value of the head node
                    child.attrib['func'] == 'HD'
                    # mark the head of current node
                    xml_node.set('HEAD', child.attrib['{http://www.w3.org/XML/1998/namespace}id'])
                    break
            if not no_lkchild:
                # left-most child node is the head
                head = children_nonHD[0]
                # set the func value of the head node
                head.attrib['func'] == 'HD'
                # mark the head of the current node
                xml_node.set('HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])
        ## 3.
        else:
            # left-most child node is the head
            head = children_HD[0]
            # set the func value of the head node
            head.attrib['func'] == 'HD'
            # mark the head of the current node
            xml_node.set('HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])
        
        # recursive calls
        for node in xml_node.findall('node'):
            mark_head(node)
    # hitting the leaf node
    else:
        return
        


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
            # for node in sent.findall(".//node[@{http://www.w3.org/XML/1998/namespace}id='s8_508']"):
                # print(node)
        
            # print(sent.attrib['{http://www.w3.org/XML/1998/namespace}id'])
        
            sentence_root = convert(sent)
            to_conll(out_f, sentence_root)