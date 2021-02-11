from phiorm.models.query import query


class psqlQ(query.Q):
    def __init__(self, query=None, left=None, right=None, _kwargs={},**kwargs):
        self.query = query
        self._kwargs = _kwargs
        self.negative = False
        self.left = left
        self.right = right
        if not self.query:
            # build this object from the first kwarg
            for k in kwargs:
                self._kwargs = {str(k): kwargs.pop(k)}
                self.build_query(**{str(k): self._kwargs[k]})
                break
            # build all children Q from the rest (defaults to AND)
            for k in kwargs:
                new_self = type(self)(**self._kwargs)&type(self)(**kwargs)
                self.copy_constructor(new_self)
                break
        super().__init__(
            data=self, left=self.left, right=self.right, **self._kwargs
        )

    def build_query(self, **kwargs):
        assert len(kwargs) == 1
        for k in kwargs:
            if kwargs[k] is None:
                self.query = f"{k} IS %({k})s"
            else:
                self.query = f"{k}=%({k})s"

    def copy_constructor(self, new: 'psqlQ'):
        self.query = new.query
        self._kwargs = new._kwargs
        self.negative = new.negative
        self.left = new.left
        self.right = new.right
        self.data = new.data


    def __invert__(self) -> 'psqlQ':
        inv = type(self)(query=self.query, left=self.left, right=self.right)
        inv.negative = self.negative
        if not inv.negative:
            inv.query = inv.query.replace('=', '!=').replace('IS', 'IS NOT')
        else:
            inv.query = inv.query.replace('!=', '=').replace('IS NOT', 'IS')
        inv.negative = not inv.negative
        return inv

    def __and__(self, other: 'psqlQ') -> 'psqlQ':
        q = type(self)(query="AND", left=self, right=other)
        return q

    def __or__(self, other: 'psqlQ') -> 'psqlQ':
        q = type(self)(query="OR", left=self, right=other)
        return q

    def evaluate(self):
        return ' '.join(q.query for q in self.inorder())

    def kwargs(self):
        d = {}
        for q in self.inorder():
            d.update(q._kwargs)
        return d
