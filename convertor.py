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
       This mothod modifies the original xml file by adding handy attribute to word nodes to 
    Parameters
    ----------

    xml_node : 
        A xml.etree.ElementTree node to convert.

    Return
    ------
    dependency_node :
        The converted xml_node which is the corresponding node in dependency parsing.
    """
    # create a node dictionary to store id:node pairs to index a node with its id
    id2node = dict()
    for node in xml_node.findall('.//node'):
        id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        id2node[id] = node
    for node in xml_node.findall('.//word'):
        id = node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        id2node[id] = node

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

            current_node = word_node

            # go up until hitting the first CONSTITUENCY node
            while True:
                if 'parent' not in current_node.attrib.keys():
                    # means this word node is punct, and its parent is the root node
                    current_node = xml_node
                    break

                parent_id = current_node.attrib['parent']
                # parent node of current node
                parent_node = id2node[parent_id]
                label.append(parent_node.attrib['cat'])
                cs_nodes.append(parent_node)
                current_node = parent_node
                # parent node is the fisrt constituent node
                if current_node.attrib['CONSTITUENT'] == 'YES':
                    break

            # go down until hitting the head leaf node
            while True:
                child_id = current_node.attrib['HEAD']
                child = id2node[child_id]
                cs_nodes.append(child)
                # child node is a leaf node
                if child.tag == 'word':
                    label.append(child.attrib['pos'])
                    head_id = child_id
                    break
                # child node is not a leaf node
                else:
                    label.append(child.attrib['cat'])
                    current_node = child

        # word node is a head node itself, the head node of this node is the head of an upper level constituent
        else:
            current_node = word_node

            # keep hitting constituncy node until the head node of the constituent node
            while True:
                # historical marker(the child node reach CONSTITUENT node from)
                historical_id = ''
                # go up until hitting the CONSTITUENCY node
                while True:
                    if 'parent' not in current_node.attrib.keys():
                        current_node = xml_node
                        break
                    # the id of current node
                    historical_id = current_node.attrib['{http://www.w3.org/XML/1998/namespace}id']
                    parent_id = current_node.attrib['parent']
                    # parent node of current node
                    parent_node = id2node[parent_id]
                    cs_nodes.append(parent_node)
                    label.append(parent_node.attrib['cat'])
                    current_node = parent_node
                    # parent node is the fisrt constituent node
                    if current_node.attrib['CONSTITUENT'] == 'YES':
                        break
                # the head of the current CONSTITUENT node has not been visited
                if historical_id != current_node.attrib['HEAD']:
                    break
                if current_node == xml_node:
                    break

            # this word is the root node
            if current_node.tag == 'sentence':
                label = ['ROOT']
                head_id = 's_0'
                cs_nodes.append(current_node)

            else:
                # go down until hitting the head leaf node
                while True:
                    child_id = current_node.attrib['HEAD']
                    child = id2node[child_id]
                    cs_nodes.append(child)
                    # child node is a leaf node
                    if child.tag == 'word':
                        label.append(child.attrib['pos'])
                        head_id = child_id
                        break
                    # child node is not a leaf node
                    else:
                        label.append(child.attrib['cat'])
                        current_node = child

        label_string = '.'.join(label)
        # add label atribute to this word node
        word_node.set('label', label_string)
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

        # ne node handling
        for ne_node in xml_node.findall('ne'):
            for node in ne_node.findall('node'):
                if node.attrib['func'] == "HD":
                    children_HD.append(node)
                else:
                    children_nonHD.append(node)

            for word_node in ne_node.findall('word'):
                if word_node.attrib['func'] == '--':
                    continue
                if word_node.attrib['func'] == "HD":
                    children_HD.append(word_node)
                else:
                    children_nonHD.append(word_node)

        # each DIRECT child node of current node
        for node in xml_node.findall('node'):
            # Heuristics of determining the head of current node(this constituent):
            # 1. If there is an explicitly marked head within a constituent (HD annotation), the head of the marked constituent is the head
            # 2. Otherwise, if there is no head marking but you have LK, use the head of it as the head
            # 3. And if none of the above(multiple hd), choose the leftmost element.
            if node.attrib['func'] == "HD":
                children_HD.append(node)
            else:
                children_nonHD.append(node)

        for word_node in xml_node.findall('word'):
            if word_node.attrib['func'] == '--':
                continue
            if word_node.attrib['func'] == "HD":
                children_HD.append(word_node)
            else:
                children_nonHD.append(word_node)

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
                attr = 'cat'
                if child.tag == 'word':
                    attr = 'pos'
                if child.attrib[attr] == 'LK':
                    no_lkchild = False
                    # set the func value of the head node
                    child.attrib['func'] = 'HD'
                    # mark the head of current node
                    xml_node.set(
                        'HEAD', child.attrib['{http://www.w3.org/XML/1998/namespace}id'])
                    break
            if no_lkchild:
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

        # ne nodes
        for ne_node in xml_node.findall('ne'):
            for node in ne_node.findall('node'):
                mark_head(node)

    # hitting the leaf node
    else:
        return


def to_conll(out, xml_node):
    """Writes a sentence to the specified file in conll-x format.

    Parameters
    ----------
    out : File
        Output file.
    xml_node: A xml.etree.ElementTree node
        The xml root node of the sentence to be printed out.
    """
    # enumerating the leaf nodes in order
    for word_node in xml_node.findall('.//word'):
        xml_id = word_node.attrib['{http://www.w3.org/XML/1998/namespace}id']
        # col1
        id = xml_id.split('_')[1]
        # col2
        form = word_node.attrib['form']
        # col3
        if 'lemma' not in word_node.attrib.keys():
            lemma = ''
        else:
            lemma = word_node.attrib['lemma']
        # col4 & col5
        stts_pos = word_node.attrib['pos']
        # col6: underscore
        # col7
        head_xml_id = word_node.attrib['HEAD_ID']
        head_id = head_xml_id.split('_')[1]
        # col8
        label = word_node.attrib['label']
        # col9 & col10: underscore

        out.write(id+'\t'+form+'\t'+lemma+'\t'+stts_pos+'\t'+stts_pos +
                  '\t'+'_'+'\t'+head_id+'\t'+label+'\t'+'_'+'\t'+'_'+'\n')

    out.write('\n')


if __name__ == '__main__':
    with open('data/sample-sentences.xml', mode='r') as in_f:
        tree = et.parse(in_f)

    root = tree.getroot()

    with open('data/sample-sentences.conllx', mode='w', encoding='utf8') as out_f:
        s = set()
        for sent in root.findall('.//sentence'):
            # the return node(Node) won't be used in to_conll(), but it will modify the original xml file
            sentence_root = convert(sent)
            to_conll(out_f, sent)
