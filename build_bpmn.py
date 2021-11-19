#!/usr/bin/env python

import argparse, sys
import logging

from random import sample
from string import ascii_letters, digits
from lxml import etree

logger = logging.getLogger(__name__)

def make_id():
    return ''.join(sample(ascii_letters + digits, 6))

nsmap = {
    'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
    'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
    'camunda': 'http://camunda.org/schema/1.0/bpmn',
    'di': 'http://www.omg.org/spec/DD/20100524/DI',
}

bpmn = nsmap['bpmn']
camunda = nsmap['camunda']

parser = etree.XMLParser()
defs = parser.makeelement(f'{{{bpmn}}}definition', nsmap=nsmap)
start = parser.makeelement(f'{{{bpmn}}}startEvent', id='Start_Event', name='Start')
end = parser.makeelement(f'{{{bpmn}}}endEvent', id='End_Event', name='End')

def create_process(name):
    proc = parser.makeelement(f'{{{bpmn}}}process', id=name, isExecutable='true')
    defs.append(proc)
    proc.append(start)
    return proc

def create_flow(parent, child):
    flow = parser.makeelement(f'{{{bpmn}}}sequenceFlow', id='Flow_' + make_id(), sourceRef=parent.attrib['id'], targetRef=child.attrib['id'])
    outgoing = parser.makeelement(f'{{{bpmn}}}outgoing', nsmap=nsmap)
    incoming = parser.makeelement(f'{{{bpmn}}}incoming', nsmap=nsmap)
    outgoing.text = incoming.text = flow.attrib['id']
    parent.append(outgoing)
    child.append(incoming)
    return flow

def add_business_rule_task(name, dmn_ref, parent):
    task = parser.makeelement(f'{{{bpmn}}}businessRuleTask', id='Task_' + make_id(), name=name)
    task.attrib[f'{{{camunda}}}decisionRef'] = dmn_ref
    return task, create_flow(parent, task)

if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--n-tasks', dest='n_tasks', type=int, required=True)
    arg_parser.add_argument('-f', '--filename', dest='filename', required=True)
    arg_parser.add_argument('-p', '--process', dest='process', default='Main')
    arg_parser.add_argument('-d', '--dmn-ref', dest='dmn_ref', default='Item_Status_Decision')
    args = arg_parser.parse_args()

    try:
        proc = create_process(args.process)
        parent = start
        for n in range(args.n_tasks, 0, -1):
            parent, flow = add_business_rule_task(f'Task {n}', args.dmn_ref, parent)
            proc.append(parent)
            proc.append(flow)
        create_flow(parent, end)
        defs.append(proc)
        with open(args.filename, 'wb') as fh:
            fh.write(etree.tostring(defs, pretty_print=True))
    except Exception as exc:
        logger.error(exc, exc_info=True)
        sys.exit(1)
