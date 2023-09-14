from dataclasses import dataclass
from enum import Enum


@dataclass
class JobStatus:
    """Contains the status of a job in a more readable format."""
    status: str
    date: str


class TimeRange(Enum):
    """Enum to help with the time range field in the public job search."""
    ANY = "all"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"
    YEAR = "1y"


class Cluster(Enum):
    """Enum to identify which cluster to submit a job to."""
    DEFAULT = None
    OZSTAR = 'ozstar'
    CIT = 'cit'
