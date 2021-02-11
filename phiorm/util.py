class tree:
    def __init__(self, data, left=None, right=None):
        self.data = data
        self.left: 'tree|None' = left
        self.right: 'tree|None' = right

    def inorder(self):
        if self.left:
            yield from self.left.inorder()
        yield self.data
        if self.right:
            yield from self.right.inorder()

    def preorder(self):
        yield self.data
        if self.left:
            yield from self.left.preorder()
        if self.right:
            yield from self.right.preorder()

    def postorder(self):
        if self.left:
            yield from self.left.postorder()
        if self.right:
            yield from self.right.postorder()
        yield self.data
