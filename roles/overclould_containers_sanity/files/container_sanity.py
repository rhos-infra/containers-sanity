#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from subprocess import CalledProcessError
from subprocess import check_output
from subprocess import STDOUT


def getstatusoutput(cmd):
    try:
        data = check_output(cmd,
                            shell=True,
                            universal_newlines=True,
                            stderr=STDOUT)
        status = 0
    except CalledProcessError as ex:
        data = ex.output
        status = ex.returncode
    if data[-1:] == '\n':
        data = data[:-1]
    return status, data


def run_cmd(cmd, node='127.0.0.1'):
    output_dict = {}
    status, output = getstatusoutput(cmd)
    output_dict[node] = output
    return output_dict


def check_docker_service_is_running_on_node(node):
    print ("\t Check that docker service is running on the node \n")
    result = run_cmd("sudo systemctl is-active docker")
    print ("status of docker daemon on {} : {}".format(node, result[node]))
    assert "active" == result[node]


def check_docker_containers_running_state_on_node(node):
    print ("\t Check that docker containers have running state on the node \n")
    docker_containers_names = run_cmd(
        'sudo docker ps --format \'table {{.Names}}\' \
        | awk \'{if(NR>1)print}\' \
        | sort')

    docker_containers = {}
    docker_containers[node] = \
        {key: None for key in docker_containers_names[node].split('\n')}

    for name in docker_containers[node].keys():
        cmd = 'sudo docker ps -f name=%s ' \
              '--format \'table {{.Status}}\' \
              | awk \'{if(NR>1)print}\' \
              | sort' % (name)
        docker_containers[node][name] = run_cmd(cmd)[node]
        print (name + ": " + docker_containers[node][name] + "\n")
        assert "Up" in docker_containers[node][name]


def check_docker_container_volume(node):
    print ("\t Check that dir for docker containers volumes exist \n")
    docker_container_volumes = run_cmd('sudo ls -l /var/lib/docker/containers')
    assert "No such file or directory" not in docker_container_volumes[node]


# gets container param - the name of docker container
# returns dictionary with command that is about to be run in container and the
#         string of the expected process to match for
def container2dict(container):
    if "cron" in container:
        return {'cmd': "ps -aux", 'process': "crond"}

    switcher = {
        "horizon": {'cmd': "ps -aux", 'process': "httpd"},
        "swift_xinetd_rsync": {'cmd': "ps -aux", 'process': "xinet"},
        "swift_rsync": {'cmd': "ps -aux", 'process': "rsync"},
        "nova_migration_target": {'cmd': "ps -aux", 'process': "sshd"},
        "clustercheck": {'cmd': "clustercheck", 'process': "clus"},
    }

    return switcher.get(container, {'cmd': "ps -aux",
                                    'process': container[:4]})


def check_openstack_services_in_docker_containers(node):
    print ("\t Check that openstack services running in docker containers \n")
    docker_containers_process = {}
    docker_containers_names = run_cmd(
        'sudo docker ps --format \'table {{.Names}}\' \
        | awk \'{if(NR>1)print}\' \
        | sort')

    docker_containers_process[node] = \
        {key: container2dict(key) for key in
         docker_containers_names[node].split('\n')}

    for container in docker_containers_process[node].keys():
        cmd = \
            'sudo docker exec %s %s \
            | grep %s \
            | grep -v %s' \
              % (container,
                 docker_containers_process[node][container].get('cmd'),
                 docker_containers_process[node][container].get('process'),
                 docker_containers_process[node][container].get('cmd'))

        docker_containers_process[node][container] = run_cmd(cmd)[node]
        print (node + "\n" + container + "\n" +
               docker_containers_process[node][container] + "\n")
        assert len(docker_containers_process[node][container]) != 0


def main():
    node = '127.0.0.1'
    check_docker_service_is_running_on_node(node)
    check_docker_containers_running_state_on_node(node)
    check_docker_container_volume(node)
    check_openstack_services_in_docker_containers(node)


if __name__ == "__main__":
    main()

