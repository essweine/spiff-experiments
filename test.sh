#!/usr/bin/bash

./run.py -p Main -b hundred.bpmn -d item_status.dmn -o logs/hundred_0000.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 1 -o logs/hundred_0001.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 5 -o logs/hundred_0005.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 10 -o logs/hundred_0010.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 50 -o logs/hundred_0050.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 100 -o logs/hundred_0100.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 500 -o logs/hundred_0500.log
./run.py -p Main -b hundred.bpmn -d item_status.dmn -n 1000 -o logs/hundred_1000.log
