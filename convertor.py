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
    # remove all relation nodes since they will influce further operations
    for relation_node in xml_node.findall('.//relation'):
        xml_node.remove(relation_node)

    # traverse the XML tree top-dwon and label the head of each constituent by adding atrribute(HEAD): value(HEADID) pairs to each XML node
    mark_head(xml_node)

    # for each word find its head bottom-up: backtracking from each word node to its head
    for word_node in xml_node.findall('.//word'):
        # label on arc
        label = []
        label.append(word_node.attrib['pos'])
        head_id = ''
        cs_nodes = []
        cs_nodes.append(word_node)
        # word_node is not a head node => the head of this word node is the head of the smallest phrase it's in
        if word_node.attrib['func'] != 'HD':

            current_node = word_node.copy()

            # go up until hitting the first CONSTITUENCY node
            while True:
                parent_id = current_node.attrib['parent']
                # parent node of current node
                parent_node = xml_node.find(
                    ".//node[@{http://www.w3.org/XML/1998/namespace}id = parent_id]")
                label.append(parent_node.attrib['cat'])
                cs_nodes.append(parent_node)
                current_node = parent_node.copy()
                # parent node is the fisrt constituent node
                if current_node.attrib['CONSTITUENT'] == 'YES':
                    break

            # go down until hitting the head leaf node
            while True:
                child_id = current_node.attrib['HEAD']
                child = xml_node.find(
                    ".//node[@{http://www.w3.org/XML/1998/namespace}id = head_id]")
                cs_nodes.append(child)
                # child node is a leaf node
                if child.tag == 'word':
                    label.append(child.attrib['pos'])
                    head_id = child_id
                    break
                # child node is not a leaf node
                else:
                    label.append(child.attrib['cat'])
                    current_node = child.copy()

        # word node is a head node itself, the head node of this node is the head of an upper level constituent
        else:
            current_node = word_node.copy()

            # keep hitting constituncy node until the head node of the constituent node 
            while True:
                # historical marker(the child node reach CONSTITUENT node from)
                historical_id = ''
                # go up until hitting the CONSTITUENCY node
                while True:
                    # the id of current node
                    historical_id = current_node.attrib['{http://www.w3.org/XML/1998/namespace}id']
                    parent_id = current_node.attrib['parent']
                    # parent node of current node
                    parent_node = xml_node.find(
                        ".//node[@{http://www.w3.org/XML/1998/namespace}id = parent_id]")
                    cs_nodes.append(parent_node)
                    label.append(parent_node.attrib['cat'])
                    current_node = parent_node.copy()
                    # parent node is the fisrt constituent node
                    if current_node.attrib['CONSTITUENT'] == 'YES':
                        break
                # the head of the current CONSTITUENT node has not been visited
                if historical_id != current_node.attrib['HEAD']:
                    break

            # this word is the root node
            if current_node.tag == 'sentence':
                label = ['ROOT']
                head_id = '0'
                cs_nodes.append(current_node)

            else:
                # go down until hitting the head leaf node
                while True:
                    child_id = current_node.attrib['HEAD']
                    child = xml_node.find(
                        ".//node[@{http://www.w3.org/XML/1998/namespace}id = head_id]")
                    cs_nodes.append(child)
                    # child node is a leaf node
                    if child.tag == 'word' :
                        label.append(child.attrib['pos'])
                        head_id = child_id
                        break
                    # child node is not a leaf node
                    else:
                        label.append(child.attrib['cat'])
                        current_node = child.copy()

        label_string = '.'.join(label)
        # add label atribute to this word node
        word_node.set('LABEL', label_string)
        # add head node id atrribute
        word_node.set('HEAD_ID', head_id)
        # add cs_nodes
        word_node.set('CS_NODES', cs_nodes)

    # root node
    word = ''
    id = 0
    lemma = ''
    pos = ''
    children = []
    head = None
    label = None
    cs_nodes = None
    # look for the child node of the root node
    for word_node in xml_node.findall('.//word'):
        if word_node.attrib['label'] == 'ROOT':
            children.append(word_node)
            label = word_node.attrib['label']
            cs_nodes = word_node.attrib['CS_NODES']
    
    relation = Relation(label, head)
    root_node = Node(word, id, lemma, pos, cs_nodes, relation, children)

    # return the root node
    return root_node


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
            # Heuristics of determining the head of current node(this constituent):
            # 1. If there is an explicitly marked head within a constituent (HD annotation), the head of the marked constituent is the head
            # 2. Otherwise, if there is no head marking but you have LK, use the head of it as the head
            # 3. And if none of the above(multiple hd), choose the leftmost element.

            if node.attrib['func'] == "HD":
                children_HD.append(node)
            else:
                if node.attrib['cat'] == 'LK':
                    children_nonHD.append(node)

        # mark if this is a constituent with multiple children node(for later backtracking)
        if len(children_HD)+len(children_nonHD) > 1:
            xml_node.set('CONSTITUENT', 'YES')
        else:
            xml_node.set('CONSTITUENT', 'NO')

        # 1.
        if len(children_HD) == 1:
            # head of the current node
            head = children_HD[0]
            # set the func value of the head node
            head.attrib['func'] == 'HD'
            # mark the head of the current node
            xml_node.set(
                'HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])

        # 2.
        elif len(children_HD) == 0:
            no_lkchild = True
            for child in children_nonHD:
                if child.attrib['cat'] == 'LK':
                    no_lkchild = False
                    # set the func value of the head node
                    child.attrib['func'] == 'HD'
                    # mark the head of current node
                    xml_node.set(
                        'HEAD', child.attrib['{http://www.w3.org/XML/1998/namespace}id'])
                    break
            if not no_lkchild:
                # left-most child node is the head
                head = children_nonHD[0]
                # set the func value of the head node
                head.attrib['func'] == 'HD'
                # mark the head of the current node
                xml_node.set(
                    'HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])
        # 3.
        else:
            # left-most child node is the head
            head = children_HD[0]
            # set the func value of the head node
            head.attrib['func'] == 'HD'
            # mark the head of the current node
            xml_node.set(
                'HEAD', head.attrib['{http://www.w3.org/XML/1998/namespace}id'])

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


