---
plugin_type: install
description: Check overcloud containers sanity
subparsers:
    containers-sanity:
        help: Checks overcloud containers sanity
        include_groups: ['Ansible options', 'Inventory', 'Common options', 'Answers file']
        groups:
            - title: check overcloud containers sanity
              options:
                  host-ip:
                      type: Value
                      help: 'ip of the machine that containers are running on'
                      required: False
                  host-username:
                      type: Value
                      help: 'username to ssh to the machine that containers are running on'
                      required: False
                  host-key_file:
                      type: Value
                      help: 'Private SSH key for the user <username>'
                      required: False
