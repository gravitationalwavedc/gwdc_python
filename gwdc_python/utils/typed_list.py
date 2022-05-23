from collections import UserList
from collections.abc import Sequence


class TypedList(UserList):
    def __init__(self, item_type, data=[]):
        self.item_type = item_type
        self._validate(data)
        super().__init__(data)

    def _validate(self, data):
        if isinstance(data, Sequence):
            for datum in data:
                self._check_type(datum)
        else:
            self._check_type(data)

    def _check_type(self, value):
        if not isinstance(value, self.item_type):
            raise TypeError(f"{self.__class__.__name__}s must contain only {self.item_type.__name__} objects")

    def __add__(self, other):
        self._validate(other)
        return super().__add__(other)

    def __iadd__(self, other):
        self._validate(other)
        return super().__iadd__(other)

    def __setitem__(self, i, item):
        self._validate(item)
        return super().__setitem__(i, item)

    def __setslice__(self, i, j, other):
        self._validate(other)
        return super().__iadd__(other)

    def extend(self, other):
        self._validate(other)
        return super().extend(other)

    def append(self, item):
        self._validate(item)
        return super().append(item)

    def insert(self, i, item):
        self._validate(item)
        return super().insert(i, item)
