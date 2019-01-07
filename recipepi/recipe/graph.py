""" RecipePi Graph Backend
Code used to represent the backend data for recipes
"""


def _get_id():
    current_id = 0
    while True:
        current_id += 1
        yield current_id


ID = _get_id()


class Graph:
    def __init__(self, name):
        self.name = name
        self.nodes = set()

    def depth(self):
        return max([item.depth() for item in self.nodes])

    def graphviz(self, linesep='\n'):
        lines = [
            'digraph "{}" {{'.format(self.name),
            '    label="{}"'.format(self.name.capitalize()),
            '    labelloc=t',
            '    fontsize=24',
            '    rankdir=LR',
            '    bgcolor=black',
        ]
        for node in sorted(self.nodes):
            node_graphviz = node.graphviz()
            if node_graphviz:
                lines.append('    ' + node_graphviz)
        edges = set()
        for tail in self.nodes:
            for head in tail.outgoing:
                edges.add((tail.id, head.id))
        for edge in sorted(edges):
            lines.append('    {} -> {} [color=gray fontcolor=gray]'.format(*edge))
        lines.append('}')
        return linesep.join(lines)


class Node:
    def __init__(self, graph: Graph):
        super().__init__()
        self.id = next(ID)
        self.graph = graph
        self.incoming = set()
        self.outgoing = set()
        self.graph.nodes.add(self)

    def __del__(self):
        for inc in self.incoming:
            inc.outgoing.remove(self)
        for out in self.outgoing:
            out.incoming.remove(self)
        self.graph.nodes.remove(self)

    def __repr__(self):
        return "Node({})".format(self.id)

    def graphviz(self):
        raise NotImplementedError()

    def depth(self, direction: str = "down"):
        if direction.lower() == "down" and self.outgoing:
            return max([item.depth(direction) for item in self.outgoing]) + 1
        elif direction.lower() == "up" and self.incoming:
            return max([item.depth(direction) for item in self.incoming]) + 1
        return 1

    def traverse(self, direction="down"):
        yield self
        if direction == "down":
            for node in self.outgoing:
                for item in node.traverse(direction):
                    yield item
        if direction == "up":
            for node in self.incoming:
                for item in node.traverse(direction):
                    yield item

    def __lt__(self, other):
        return self.id < other.id

    def __hash__(self):
        return self.id


class NodeGroup:
    def __init__(self, *args):
        self.nodes = set(args)

    def __add__(self, other):
        if isinstance(other, NodeGroup):
            return NodeGroup(*self.nodes, *other.nodes)
        elif isinstance(other, Node):
            return NodeGroup(*self.nodes, other)

    def __repr__(self):
        return "NodeGroup" + str(self.nodes)


def connect(tail, head):
    """ Connect every node with no outgoings in `tail` to every node with no incomings in `head`
    """
    if isinstance(tail, Node) and isinstance(head, Node):
        tail.outgoing.add(head)
        head.incoming.add(tail)
        return
    if isinstance(tail, NodeGroup):
        tails = [node for node in tail.nodes if not node.outgoing]
    else:
        tails = [tail]
    if isinstance(head, NodeGroup):
        heads = [node for node in head.nodes if not node.outgoing]
    else:
        heads = [head]
    group = NodeGroup()
    for t in tails:
        for h in heads:
            connect(t, h)
            group += t
            group += h
    return group
