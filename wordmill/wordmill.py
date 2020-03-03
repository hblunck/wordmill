from __future__ import annotations
import itertools
from typing import List, Set, Type, Iterable, Optional, Tuple


class Node(object):
    """
    Baseclass for all elements within a wordmill network. In particular

    * :class:`Inventory`
    * :class:`Node`
    * :class:`Source`
    * :class:`Sink`

    are derived from this class.
    """
    def __init__(self):
        """
        Constructor.
        """
        # Variables can store necessary input and provided output words.
        self._inputs = []
        self._outputs = []
        # List of input nodes
        self._input_nodes = []
        # List of output nodes
        self._output_nodes = []

    @property
    def inputs(self) -> List[str]:
        """
        List of necessary input word(s)

        Returns:
            List of necessary input word(s)
        """
        return self._inputs

    @property
    def outputs(self) -> List[str]:
        """
        List of necessary output word(s)

        Returns:
            List of necessary output word(s)
        """
        return self._outputs
        
    @property
    def output_nodes(self) -> List[Node]:
        """
        List of output nodes.

        Returns:
            List of output nodes.
        """
        return self._output_nodes
    
    @property
    def input_nodes(self) -> List[Node]:
        """
        List of input nodes.

        Returns:
            List of input nodes.
        """
        return self._input_nodes

    @property
    def neighbors(self) -> Set[Node]:
        """
        Set of "neighbors" (nodes that are connected to this node as either
        input or output nodes
        """
        return set(self._input_nodes) | set(self._output_nodes)

    def form_outbound_edge(self, other_node: Node):
        """
        Form a link to another node that consumes an output of the current node.

        Args:
            other_node: Node to connect to.
        """
        self._output_nodes.append(other_node)

    def form_inbound_edge(self, other_node: Node):
        """
        Form a link to another node that provides and input of the current node.

        Args:
            other_node: Node to connect to.
        """
        self._input_nodes.append(other_node)

    @property
    def word(self) -> str:
        return self._outputs[0]
        
    @property
    def fully_connected(self) -> bool:
        """
        Binary predicate indicating if this node is connected to input and
        output nodes such that any required input can be provided and any
        produced output can be consumed.

        Returns:
            Binary predicate.
        """
        # Check that we have enough input nodes
        if len(self._input_nodes) < len(self._inputs):
            return False
        # Check that we have one suitable inbound neighbor for every input we
        # need.
        if len(set(self._inputs) - set([n.word for n in self._input_nodes])) > 0:
            return False
        # Check that we have enough outbound nodes
        if len(self._output_nodes) < len(self._outputs):
            return False
        # If all checks were passed, return True
        return True


class Inventory(Node):
    """
    Node class that holds inventory of a specific word between procesing steps
    (machines) or between source and machines or machines and sinks.
    """
    def __init__(self, word: str):
        """
        Constructor.

        Args:
            word: Word to store.
        """
        Node.__init__(self)
        self._inputs = tuple([word])
        self._outputs = tuple([word])


class Machine(Node):
    """
    Node class that glues words together to form new output word from two
    input words.

    Output word is obtained by concatenating `left_word` and `right_word`
    in this order.
    """
    def __init__(self, left_word: str, right_word: str):
        """
        Constructor

        Args:
            left_word: "left" input word
            right_word: "right" input word
        """
        Node.__init__(self)
        self._inputs = tuple([left_word, right_word])
        self._outputs = tuple([left_word + right_word])


class Source(Node):
    def __init__(self, word: str):
        """
        Constructor.

        Args:
            word: Word provided by this source.
        """
        Node.__init__(self)
        self._outputs = tuple([word])


class Sink(Node):
    def __init__(self, word: str):
        """
        Constructor

        Args:
            word: Input word consumed by this sink.
        """
        Node.__init__(self)
        self._inputs = tuple([word])
    
    @property
    def word(self) -> str:
        """
        Return word consumed by this node type.

        Returns:
            Input word consumed by sink.
        """
        return self._inputs[0]


class AssemblySystem(object):
    """
    An AssemblySystem instance is a directed graph of :class:`Node` instances
    that transforms inputs (provided by :class:`Source` instances) into a set
    of output words (consumed by :class:`Sink` instances), using
    :class:`Machine` and :class:`Inventory` instances.
    """
    def __init__(self, nodes: Optional[Set[Node]] = None):
        """
        Constructor.

        Args:
            nodes: Set of nodes that constitute this assembly network.

        Note:
            Calling the constructor directly is not the recommended way of
            instantiating this class. Instead, call
            :meth:`AssemblySystem.discover` with a (set of) :class:`Node`
            instances that form part of the network and let the full set
            of nodes be discovered automatically or (most likely use-case)
            call :class:`AssemblySystem.generate` with a set of input words,
            output words, and a generating algorithm to create an assembly
            system "from scratch".
        """
        if nodes is None:
            nodes = set()
        self._nodes = nodes
       
    def get_nodes_of_type(self, cls: Type[Node]) -> List[Node]:
        """
        Get all nodes of a given class that are part of the system.

        Args:
            cls: Class by which to filter.

        Returns:
            All nodes in the system that are a subclass of `cls`.
        """
        return [
            n
            for n in self._nodes
            if isinstance(n, cls)
        ]

    @classmethod
    def discover(cls, subset: Iterable[Node]) -> AssemblySystem:
        """
        Automatically discover a full assembly system by following connections
        between :class:`Node` instances.

        Args:
            subset: Subset of :class:`Node` instances that are part of the
                assembly network. E.g. all sources or sinks.

        Returns:
            AssemblySystem instance generated from the discovered nodes.

        Note:
            It is recommended to use a set of nodes from which the full
            assembly system can be discovered also in the case on multiple
            components in the graph (i.e. separate assembly systems for
            different output words that are not connected through material
            flow). Thus it is recommended (and also easiest) to pass either
            the set of sources or sinks (or both).

        Raises:
            ValueError: If one of the discovered nodes is insufficiently
                connected to input/output nodes.
        """
        untreated_nodes = set(subset)
        discovered_nodes = set()
        while len(untreated_nodes) > 0:
            n = untreated_nodes.pop()
            untreated_nodes |= (n.neighbors - discovered_nodes)
            discovered_nodes.add(n)
        if not all([n.fully_connected for n in discovered_nodes]):
            raise ValueError('Found node with insufficient inbound/outbound edges.')
        return AssemblySystem(discovered_nodes)

    @classmethod
    def generate(
            cls,
            func,
            *words: List[str],
            **kwargs
    ) -> AssemblySystem:
        """
        Generate an AssemblySystem by supplying a set of output words and a
        generating function.

        Args:
            func: Generating function, as provided in :module:`wordmill.algorithms`
            words: Any other unnamed parameters are assumed to be strings
                indicating the output words.
            kwargs: Any other named arguments are passed as additional arguments
                to `func`.

        Note:
            In this function, it is assumed that the assembly system is to build
            from atomic inputs (single characters).
        """
        sinks = {
            w: Sink(w)
            for w in words
        }
        sources = {
            inp: Source(inp)
            for inp in set(itertools.chain(*words))
        }
        func(sources, sinks, **kwargs)
        return AssemblySystem.discover(sources.values())
    
    def to_digraph(self) -> 'networkx.MultiDiGraph':
        """
        Create a :class:`networkx.MultiDiGraph` instance from the assembly system.
        Requires the `NetworkX <https://networkx.github.io/>` library.

        Returns:
            MultiDiGraph.
        """
        import networkx as nx
        g = nx.MultiDiGraph()
        for n in self._nodes:
            for sink in n.output_nodes:
                g.add_edge(n, sink)
        return g
    
    def to_graphviz(self) -> str:
        """
        Return string representation that can be rendered using
        `GraphViz <https://www.graphviz.org/>`_.

        Returns:
            GraphViz String representation.
        """
        class_to_shape = {
            Inventory: 'invtriangle',
            Machine: 'box',
            Sink: 'trapezium',
            Source: 'invtrapezium'
        }
        node_dict = {str(i): n for i, n in enumerate(self._nodes)}
        s = 'digraph wordmill {\n'
        for key, n in node_dict.items():
            s += '\t"{}" [shape={}, label="{}"];\n'.format(key, class_to_shape[n.__class__], n.word)
        invert_node_dict = {v: k for k, v in node_dict.items()}
        for key, source in node_dict.items():
            for sink in source.output_nodes:
                s += '\t"{}" -> "{}";\n'.format(invert_node_dict[source], invert_node_dict[sink])
        s += '}'
        return s


def form_edge(source, sink):
    assert len(set(source.outputs) & set(sink.inputs)) > 0, 'Source and sink have no common product to share'
    source.form_outbound_edge(sink)
    sink.form_inbound_edge(source)


def split_word(word: str, pos: int) -> Tuple[str, str]:
    return word[:pos], word[pos:]
