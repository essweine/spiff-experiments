#!/usr/bin/env python

import argparse, sys
import random
import json

import yaml

from SpiffWorkflow.bpmn.serializer import BpmnSerializer
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine


import logging
logger = logging.getLogger()
console = logging.StreamHandler()
logger.addHandler(console)

class Parser(BpmnDmnParser):

    OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
    OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)

class CustomScriptEngine(PythonScriptEngine):

    def __init__(self):
        super().__init__(scriptingAdditions={'random': random})

def parse(process, bpmn_files, dmn_files):

    parser = Parser()
    parser.add_bpmn_files(bpmn_files)
    if dmn_files:
        parser.add_dmn_files(dmn_files)
    script_engine=CustomScriptEngine()
    return BpmnWorkflow(parser.get_spec(process), script_engine=script_engine)

def complete_form(task, responses):

    if task.data is None:
        task.data = {}

    for field in task.task_spec.form.fields:
        response = responses.get(task.task_spec.name, { }).get(field)
        if field.type == "long":
            response = int(response)
        task.update_data_var(field.id, response)

def set_task_data(task, n_items):

    with open('nyt.json') as fh:
        data = { 'items': [ ] }
        for i in range(n_items):
            data['items'].append(json.loads(fh.readline()))
        logger.info(f'Adding {len(json.dumps(data))} bytes of data to {task.task_spec.name}')
        task.update_data(data)

def run(workflow, responses, n_items):

    if n_items is not None:
        first = [ t for t in workflow.get_tasks() if isinstance(t.task_spec, BusinessRuleTask) ][0]
        set_task_data(first, n_items)
    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()
    while len(ready_tasks) > 0:
        for task in ready_tasks:
            if isinstance(task.task_spec, UserTask):
                complete_form(task, responses)
            workflow.complete_task_from_id(task.id)
        workflow.do_engine_steps()
        ready_tasks = workflow.get_ready_user_tasks()

if __name__ == '__main__':

    parser = argparse.ArgumentParser('Simple BPMN runner')
    parser.add_argument('-p', '--process', dest='process')
    parser.add_argument('-b', '--bpmn', dest='bpmn', nargs='+')
    parser.add_argument('-d', '--dmn', dest='dmn', nargs='*')
    parser.add_argument('-r', '--responses', dest='responses')
    parser.add_argument('-n', '--n_items', dest='n_items', type=int)
    parser.add_argument('-l', '--level', dest='level', default='INFO')
    parser.add_argument('-f', '--format', dest='format', default='%(created)f %(message)s')
    parser.add_argument('-o', '--output', dest='output')
    args = parser.parse_args()

    """
    args.process = 'Main'
    args.bpmn = ['single.bpmn' ]
    args.dmn = [ 'item_status.dmn']
    args.n_items = 1
    """

    try:
        logger.setLevel(args.level)
        formatter = logging.Formatter(args.format)
        console.setFormatter(formatter)
        if args.output is not None:
            handler = logging.FileHandler(args.output)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        responses = yaml.safe_load(open(args.responses)) if args.responses else { }
        wf = parse(args.process, args.bpmn, args.dmn)
        run(wf, responses, args.n_items)
    except Exception as exc:
        logger.error(exc, exc_info=True)
        sys.exit(1)
