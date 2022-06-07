from gwdc_python.jobs import JobBase


def test_job_base_equality(mocker):
    job_data = {
        "client": mocker.Mock(),
        "job_id": 1,
        "name": "test_name",
        "description": "test description",
        "user": "Test User",
        "job_status": {
            "name": "Completed",
            "date": "2021-01-01"
        }
    }
    job_data_changed_id = {**job_data, "job_id": 2}
    job_data_changed_name = {**job_data, "name": "testing_name"}
    job_data_changed_user = {**job_data, "user": "Testing User"}

    assert JobBase(**job_data) == JobBase(**job_data)
    assert JobBase(**job_data) != JobBase(**job_data_changed_id)
    assert JobBase(**job_data) != JobBase(**job_data_changed_name)
    assert JobBase(**job_data) != JobBase(**job_data_changed_user)
