"""
Function tests the `wordmill.wordmill` module of base classes.
"""
import pytest

from wordmill.wordmill import Node, Source, Sink, Machine, Inventory


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
            ('out', Sink('a'))
        ]
    ],
    [
        Sink('a'),
        [
            ('in', Source('a'))
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
            ('in', Source('a')),
            ('out', Sink('ab')),
            ('in', Source('b')),
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
