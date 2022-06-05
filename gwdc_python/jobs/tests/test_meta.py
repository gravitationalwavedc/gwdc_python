from gwdc_python.jobs.meta import JobMeta


class TrivialClass(metaclass=JobMeta):
    pass


def test_filter():
    pass


class JobClass(metaclass=JobMeta):
    FILE_LIST_FILTERS = {"test": test_filter}


def test_job_meta_methods():
    assert not hasattr(TrivialClass, "get_test_file_list")
    assert not hasattr(TrivialClass, "get_test_files")
    assert not hasattr(TrivialClass, "save_test_files")

    assert hasattr(JobClass, "get_test_file_list")
    assert hasattr(JobClass, "get_test_files")
    assert hasattr(JobClass, "save_test_files")


def test_get_file_list(mocker):
    mock_job = JobClass()
    mock_job.get_full_file_list = mocker.Mock()
    mock_job.get_test_file_list()
    assert mock_job.get_full_file_list.call_count == 1
    assert mock_job.get_full_file_list.return_value.filter_list.call_count == 1
