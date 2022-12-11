#!/bin/sh

ansible-playbook -i inventory.ini playbook.yaml > ansible-output.json
