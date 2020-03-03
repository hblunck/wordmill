import pytest
import networkx as nx

from wordmill.wordmill import AssemblySystem
from wordmill.algorithms import form_linear_assembly

grid_test_algorithm_isomorphism = [
    # Structure
    # - AssemblySystem
    # - Edge list of directed edges that can be transformed to a MultiDiGraph that should be
    #   isomorphic to the assembly system graph
    [
        AssemblySystem.generate(
            form_linear_assembly,
            'ab'
        ),
        [
            ('Source_a', 'Inv_a'),
            ('Source_b', 'Inv_b'),
            ('Inv_a', 'Machine_a+b'),
            ('Inv_b', 'Machine_a+b'),
            ('Machine_a+b', 'Inventory_ab'),
            ('Inventory_ab', 'Sink_ab'),
        ]
    ],
    [
        AssemblySystem.generate(
            form_linear_assembly,
            'ab',
            'ba'
        ),
        [
            # Production of 'ab'
            ('Source_a', 'Inv_a1'),
            ('Source_b', 'Inv_b1'),
            ('Inv_a1', 'Machine_a+b'),
            ('Inv_b1', 'Machine_a+b'),
            ('Machine_a+b', 'Inventory_ab'),
            ('Inventory_ab', 'Sink_ab'),
            # Production of 'ba'
            ('Source_a', 'Inv_a2'),
            ('Source_b', 'Inv_b2'),
            ('Inv_a2', 'Machine_b+a'),
            ('Inv_b2', 'Machine_b+a'),
            ('Machine_b+a', 'Inventory_ba'),
            ('Inventory_ba', 'Sink_ba'),
        ]
    ]
]


@pytest.mark.parametrize('assembly_system, edge_list', grid_test_algorithm_isomorphism)
def test_algorithms_isomorphism(assembly_system, edge_list):
    assert nx.is_isomorphic(assembly_system.to_digraph(), nx.MultiDiGraph(edge_list))
