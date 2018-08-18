"""
dc-test /usr/test/app/batch/test_get_incomplete_data.py
"""
from datetime import datetime, timedelta
from unittest import mock

import pytest
import time

from src.app.batch import get_incomplete_data
from src.app.batch.get_incomplete_data import IncompleteDataGetter
from src.app.models.job_log import JobLogDAO, JobLogStatus, JobLogType
from test.app.db_test_helper import db_test_session


class TestIncompleteDataGetter:
    class Test_get_and_register_data:
        def test_not_implemented(self):
            with pytest.raises(NotImplementedError):
                IncompleteDataGetter.get_and_register_data(None, None)

    class Test_get_incomplete_data_key:
        def test_not_implemented(self):
            with pytest.raises(NotImplementedError):
                IncompleteDataGetter.get_incomplete_data_key(None)

    class Test_wait_to_run_next_process:
        def test_wait(self):
            with db_test_session() as session:
                with mock.patch.object(get_incomplete_data, 'sleep') as m_sleep:
                    # setup
                    job_log = JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                    session.commit()

                    # run
                    IncompleteDataGetter.wait_to_run_next_process(job_log)

                    # verify
                    m_sleep.assert_called_once()

        def test_no_wait(self):
            with db_test_session() as session:
                with mock.patch.object(get_incomplete_data, 'sleep') as m_sleep:
                    # setup
                    job_log = JobLogDAO(session).add_or_update(JobLogType.VIDEO, JobLogStatus.DONE)
                    job_log.updated_at = datetime.now() + timedelta(minutes=2)
                    session.commit()

                    # run
                    IncompleteDataGetter.wait_to_run_next_process(job_log)

                    # verify
                    m_sleep.assert_not_called()
