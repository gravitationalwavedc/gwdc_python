from .meta import JobMeta


class JobBase(metaclass=JobMeta):
    """Base class from which GWDC jobs will inherit.
    """

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, job_id={self.job_id})"
