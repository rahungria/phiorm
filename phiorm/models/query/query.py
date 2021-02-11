import abc
from phiorm.util import tree


class Q(abc.ABC, tree):
    '''
    Object to be passed to models to execute queries
    '''
    def __init__(self, data, left, right, **kwargs):
        # assert len(kwargs) == 1
        super().__init__(data, left=left, right=right)

    @abc.abstractmethod
    def __and__(self, other: 'Q'):
        raise NotImplementedError

    @abc.abstractmethod
    def __invert__(self, other: 'Q'):
        raise NotImplementedError

    @abc.abstractmethod
    def __or__(self, other: 'Q'):
        raise NotImplementedError

    @abc.abstractmethod
    def evaluate(self):
        raise NotImplementedError
