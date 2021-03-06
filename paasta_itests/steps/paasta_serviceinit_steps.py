# Copyright 2015 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import time

from behave import when, then
import mock

sys.path.append('../')
import paasta_tools
from paasta_tools import marathon_serviceinit
from paasta_tools import marathon_tools
from paasta_tools.utils import _run
from paasta_tools.utils import decompose_job_id


@when(u'we run the marathon app "{job_id}"')
def run_marathon_app(context, job_id):
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']
    app_config = {
        'id': app_id,
        'cmd': '/bin/sleep 1m',
    }
    with mock.patch('paasta_tools.bounce_lib.create_app_lock'):
        paasta_tools.bounce_lib.create_marathon_app(app_id, app_config, context.marathon_client)


@when(u'we wait for it to be deployed')
def wait_for_deploy(context):
    print "Sleeping 10 seconds to wait for deployment..."
    time.sleep(10)


@then(u'marathon_serviceinit status_marathon_job should return "{status}" for "{job_id}"')
def status_marathon_job(context, status, job_id):
    normal_instance_count = 1
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']

    output = marathon_serviceinit.status_marathon_job(
        service,
        instance,
        app_id,
        normal_instance_count,
        context.marathon_client
    )
    assert status in output


@then(u'marathon_serviceinit restart should get new task_ids for "{job_id}"')
def marathon_restart_gets_new_task_ids(context, job_id):
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']
    normal_instance_count = 1
    cluster = context.system_paasta_config['cluster']

    old_tasks = context.marathon_client.get_app(app_id).tasks
    marathon_serviceinit.restart_marathon_job(
        service,
        instance,
        app_id,
        normal_instance_count,
        context.marathon_client,
        cluster
    )
    print "Sleeping 5 seconds to wait for %s to be restarted." % service
    time.sleep(5)
    new_tasks = context.marathon_client.get_app(app_id).tasks
    print "Tasks before the restart: %s" % old_tasks
    print "Tasks after  the restart: %s" % new_tasks
    print  # sacrificial line for behave to eat instead of our output
    assert old_tasks != new_tasks


@then(u"paasta_serviceinit status exits with return code 0 and the correct output")
def chronos_status_returns_healthy(context):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s test-service.job status' % context.soa_dir
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0
    assert "Stopped" in output
    assert "New" in output


@then(u"paasta_serviceinit status --verbose exits with return code 0 and the correct output")
def chronos_status_verbose_returns_healthy(context):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s test-service.job status --verbose' % context.soa_dir
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0
    assert "Running Tasks:" in output


@when(u"we paasta_serviceinit emergency-stop the chronos job")
def chronos_emergency_stop_job(context):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s test-service.job stop' % context.soa_dir
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0


@when(u"we paasta_serviceinit emergency-start the chronos job")
def chronos_emergency_start_job(context):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s test-service.job start' % context.soa_dir
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0


@when(u"we paasta_serviceinit emergency-restart the chronos job")
def chronos_emergency_restart_job(context):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s test-service.job restart' % context.soa_dir
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0


@when(u'we run paasta serviceinit "{command}" on "{job_id}"')
def paasta_serviceinit_command(context, command, job_id):
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s %s %s' % (context.soa_dir, job_id, command)
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0


@when(u'we run paasta serviceinit --appid "{command}" on "{job_id}"')
def paasta_serviceinit_command_appid(context, command, job_id):
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']
    cmd = '../paasta_tools/paasta_serviceinit.py --soa-dir %s --appid %s %s %s' \
          % (context.soa_dir, app_id, job_id, command)
    print 'Running cmd %s' % cmd
    (exit_code, output) = _run(cmd)
    print 'Got exitcode %s with output:\n%s' % (exit_code, output)
    print  # sacrificial line for behave to eat instead of our output

    assert exit_code == 0


@when(u'we wait for "{job_id}" to launch exactly {task_count:d} tasks')
def wait_launch_tasks(context, job_id, task_count):
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']
    client = context.marathon_client
    marathon_tools.wait_for_app_to_launch_tasks(client, app_id, task_count, exact_matches_only=True)


@then(u'"{job_id}" has exactly {task_count:d} requested tasks in marathon')
def marathon_app_task_count(context, job_id, task_count):
    (service, instance, _, __) = decompose_job_id(job_id)
    app_id = marathon_tools.create_complete_config(service, instance, None, soa_dir=context.soa_dir)['id']
    client = context.marathon_client

    tasks = client.list_tasks(app_id=app_id)
    assert len(tasks) == task_count


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
