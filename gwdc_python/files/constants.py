# Can NOT be an enum
class JobType:
    # If the job is a normal job run by the system
    NORMAL_JOB = 0
    # Job was created via a job upload
    UPLOADED_JOB = 1
    # Job is an exernal job
    EXTERNAL_JOB = 2
