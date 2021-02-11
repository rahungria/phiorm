import phiorm.util as util
from . import query


class psqlQ(query.Q):
    def __init__(self, query=None, data=None, left=None, right=None, **kwargs):
        if data is None:
            data=self
        self.query = query
        self._kwargs = kwargs
        self.inverted = False
        if not self.query:
            for k in self._kwargs:
                if kwargs[k] is None:
                    self.query = f"{k} IS %({k})s"
                else:
                    self.query = f"{k}=%({k})s"
        super().__init__(data, left=left, right=right, **self._kwargs)

    def build_query(self, **kwargs):
        assert len(kwargs) == 1
        for k in kwargs:
            if kwargs[k] is not None:
                self.query = f"{k}=%({k})s"
            else:
                self.query = f"{k} is %({k})s"

    def __invert__(self) -> 'psqlQ':
        inv = type(self)(query=self.query)
        inv.left, inv.right = self.left, self.right
        if not inv.inverted:
            inv.query = inv.query.replace('=', '!=').replace('IS', 'IS NOT')
        else:
            inv.query = inv.query.replace('!=', '=').replace('IS NOT', 'IS')
        return inv

    def __and__(self, other: 'psqlQ') -> 'psqlQ':
        q = type(self)(query="AND")
        q.left, q.right = self, other
        return q

    def __or__(self, other: 'psqlQ') -> 'psqlQ':
        q = type(self)(query="OR")
        q.left, q.right = self, other
        return q

    def evaluate(self):
        return ' '.join(q.query for q in self.inorder())

    def kwargs(self):
        d = {}
        for q in self.inorder():
            d.update(q._kwargs)
        return d
