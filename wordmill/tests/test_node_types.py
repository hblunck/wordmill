"""
Function tests the `wordmill.wordmill` module of base classes.
"""
import pytest

from wordmill import Node, Source, Sink, Machine, Inventory, form_edge


grid_test_Node_properties = [
    # Structure
    # - Class to test
    # - Input arguments
    # - Dictionary, keyed by property names, with expected property values as values
    [
        Source,
        {
            'word': 'test'
        },
        {
            'word': 'test',
            'outputs': ('test',),
            'inputs': [],
            'fully_connected': False,
            'neighbors': set()
        }
    ],
    [
        Sink,
        {
            'word': 'test'
        },
        {
            'word': 'test',
            'outputs': [],
            'inputs': ('test',),
            'fully_connected': False,
            'neighbors': set()
        }
    ],
    [
        Inventory,
        {
            'word': 'test'
        },
        {
            'word': 'test',
            'outputs': ('test',),
            'inputs': ('test',),
            'fully_connected': False,
            'neighbors': set()
        }
    ],
    [
        Machine,
        {
            'left_word': 'test',
            'right_word': 'word'
        },
        {
            'word': 'testword',
            'outputs': ('testword',),
            'inputs': ('test', 'word'),
            'fully_connected': False,
            'neighbors': set()
        }
    ],
]

# From this, create a more elaborate test suite, where every tested property has its own row
full_grid_test_Node_properties = [
    (cls, kwargs, property_name, expected_values)
    for cls, kwargs, property_dict in grid_test_Node_properties
    for property_name, expected_values in property_dict.items()
]


@pytest.mark.parametrize('cls, kwargs, property_name, expected_value', full_grid_test_Node_properties)
def test_Node_properties(cls, kwargs, property_name, expected_value):
    """
    Test properties of instances of :class:`Node` and derived classes.
    """
    n = cls(**kwargs)
    assert getattr(n, property_name) == expected_value


grid_test_Node_fully_connected = [
    # Structure
    # - Node instance
    # - List of tuples of neighbors to add
    #   - first entry is string indicating if this is a input or output edge
    #   - Second entry is node instance to connect
    [
        Source('a'),
        [
            ('out', Inventory('a'))
        ]
    ],
    [
        Sink('a'),
        [
            ('in', Inventory('a'))
        ]
    ],
    [
        Inventory('a'),
        [
            ('in', Source('a')),
            ('out', Sink('a'))
        ]
    ],
    [
        Machine('a', 'b'),
        [
            ('in', Inventory('a')),
            ('out', Inventory('ab')),
            ('in', Inventory('b')),
        ]
    ]
]


@pytest.mark.parametrize('n, neighbors', grid_test_Node_fully_connected)
def test_Node_fully_connected(n: Node, neighbors):
    """
    Check binary predicate if node is fully connected.
    """
    # No node should be fully connected without any neighbors
    assert not n.fully_connected
    # Now start adding neighbors iteratively
    for i, (direction, neighbor) in enumerate(neighbors):
        assert len(n.neighbors) == i
        if direction == 'in':
            n.form_inbound_edge(neighbor)
            assert neighbor in n.input_nodes and neighbor in n.neighbors
        else:
            n.form_outbound_edge(neighbor)
            assert neighbor in n.output_nodes and neighbor in n.neighbors
        # Node should be fully connected if this was the last neighbor to
        # add. Predicate should return False otherwise.
        assert n.fully_connected == (i == len(neighbors) - 1)


grid_test_Node_split_word = [
    ('Test', 1, 'T', 'est'),
    ('Test', 2, 'Te', 'st'),
    ('Test', 3, 'Tes', 't'),
]


@pytest.mark.parametrize(
    'input_word, split_pos, left_output, right_output',
    grid_test_Node_split_word
)
def test_Node_split_word(input_word, split_pos, left_output, right_output):
    """
    Test checks the :meth:`Node.split_word` helper function.
    """
    # Test that using the split position results in the expected split
    assert Node.split_word(input_word, split_pos) == (left_output, right_output)
    # Test that assigning an invalid value to pos throws an error
    with pytest.raises(AssertionError, match='Parameter pos out of valid range.'):
        Node.split_word(input_word, 0)
    with pytest.raises(AssertionError, match='Parameter pos out of valid range.'):
        Node.split_word(input_word, len(input_word))


grid_test_Node_form_edges = [
    # These test cases should be okay
    (Source('a'), Inventory('a'), 'success'),
    (Inventory('a'), Machine('a', 'b'), 'success'),
    (Machine('a', 'b'), Inventory('ab'), 'success'),
    (Inventory('a'), Sink('a'), 'success'),
    # Here we should have problems identifying shared products
    (Source('a'), Inventory('b'), 'no_shared_product'),
    (Inventory('a'), Machine('b', 'c'), 'no_shared_product'),
    (Machine('a', 'b'), Inventory('a'), 'no_shared_product'),
    (Inventory('a'), Sink('b'), 'no_shared_product'),
    # Here we should have problems because we should not be able connect nodes of these types
    # directly.
    (Source('a'), Sink('a'), 'wrong_class_type'),
    (Source('a'), Machine('a', 'b'), 'wrong_class_type'),
    (Inventory('a'), Inventory('a'), 'wrong_class_type'),
    (Machine('a', 'b'), Machine('ab', 'c'), 'wrong_class_type'),
    (Machine('a', 'b'), Sink('ab'), 'wrong_class_type')
]


@pytest.mark.parametrize(
    'source, sink, expected_result',
    grid_test_Node_form_edges
)
def test_Node_form_edges(source, sink, expected_result):
    """
    Function test both the :meth:`Node.form_inbound_edge` and :meth:`Node.form_outbound_edge`
    methods.
    """
    if expected_result == 'success':
        source.form_outbound_edge(sink)
        sink.form_inbound_edge(source)
    else:
        if expected_result == 'no_shared_product':
            match = 'Source and sink have no common product to share'
        elif expected_result == 'wrong_class_type':
            match = 'other_node has to be be an instance of one of the following classes: *'
        with pytest.raises(ValueError, match=match):
            source.form_outbound_edge(sink)
        with pytest.raises(ValueError, match=match):
            sink.form_inbound_edge(source)
