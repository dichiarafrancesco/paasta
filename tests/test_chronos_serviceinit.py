#!/usr/bin/env python

import contextlib
import mock

from paasta_tools.utils import PaastaColors
import chronos_serviceinit


def test_start_chronos_job():
    service = 'my_service'
    instance = 'my_instance'
    job_id = 'my_job_id'
    cluster = 'my_cluster'
    old_schedule = 'R/2015-03-25T19:36:35Z/PT5M'
    job_config = {'beep': 'boop', 'disabled': False, 'schedule': old_schedule}
    with contextlib.nested(
        mock.patch('chronos_serviceinit.chronos_tools.chronos.ChronosClient', autospec=True),
    ) as (
        mock_client,
    ):
        chronos_serviceinit.start_chronos_job(service,
                                              instance,
                                              job_id,
                                              mock_client,
                                              cluster,
                                              job_config)
        assert job_config['schedule'] == old_schedule
        mock_client.update.assert_called_once_with(job_config)
        mock_client.run.assert_called_once_with(job_id)


def test_stop_chronos_job():
    service = 'my_service'
    instance = 'my_instance'
    cluster = 'my_cluster'
    existing_jobs = [{'name': 'job_v1', 'disabled': False},
                     {'name': 'job_v2', 'disabled': False},
                     {'name': 'job_v3', 'disabled': True}]
    with contextlib.nested(
        mock.patch('chronos_serviceinit.chronos_tools.chronos.ChronosClient', autospec=True),
    ) as (
        mock_client,
    ):
        chronos_serviceinit.stop_chronos_job(service, instance, mock_client, cluster, existing_jobs)
        assert mock_client.update.call_count == 3
        assert mock_client.delete_tasks.call_count == 3
        for job in existing_jobs:
            assert job['disabled'] is True
            mock_client.update.assert_any_call(job)
            mock_client.delete_tasks.assert_any_call(job['name'])


def test_format_chronos_job_status_disabled():
    example_disabled_job = {
        'disabled': True,
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_disabled_job)
    assert PaastaColors.red("Disabled") in actual


def test_format_chronos_job_status_enabled():
    example_enabled_job = {
        'disabled': False,
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_enabled_job)
    assert PaastaColors.green("Enabled") in actual


def test_format_chronos_job_no_last_run():
    example_job = {
        'lastError': '',
        'lastSuccess': '',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.yellow("New") in actual


def test_format_chronos_job_failure_no_success():
    example_job = {
        'lastError': '2015-04-20T23:20:00.420Z',
        'lastSuccess': '',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.red("Fail") in actual


def test_format_chronos_job_success_no_failure():
    example_job = {
        'lastError': '',
        'lastSuccess': '2015-04-20T23:20:00.420Z',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.green("OK") in actual


def test_format_chronos_job_failure_and_then_success():
    example_job = {
        'lastError': '2015-04-20T23:20:00.420Z',
        'lastSuccess': '2015-04-21T23:20:00.420Z',
    }
    actual = chronos_serviceinit.format_chronos_job_status(example_job)
    assert PaastaColors.green("OK") in actual


def test_status_chronos_job_is_deployed():
    jobs = [{'name': 'my_service my_instance gityourmom configyourdad'}]
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert actual == 'job_status_output'


def test_status_chronos_job_is_not_deployed():
    jobs = []
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert 'not setup' in actual


def test_status_chronos_job_multiple_jobs():
    jobs = [
        {'name': 'my_service my_instance gityourmom configyourdad'},
        {'name': 'my_service my_instance gityourmom configyourbro'},
    ]
    with mock.patch('chronos_serviceinit.format_chronos_job_status',
                    autospec=True, return_value='job_status_output'):
        actual = chronos_serviceinit.status_chronos_job(
            jobs,
        )
        assert actual == 'job_status_output\njob_status_output'