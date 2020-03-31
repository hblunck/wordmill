import pytest
import networkx as nx

from wordmill import AssemblySystem
from wordmill.algorithms import form_linear_assembly, form_component_assembly, \
    form_product_focussed_team_assembly, form_bio_inspired_assembly

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
    ],
    [
        AssemblySystem.generate(
            form_component_assembly,
            'abcd'
        ),
        [
            ('Source_a', 'Inv_a'),
            ('Source_b', 'Inv_b'),
            ('Source_c', 'Inv_c'),
            ('Source_d', 'Inv_d'),
            ('Inv_a', 'Machine_a+b'),
            ('Inv_b', 'Machine_a+b'),
            ('Inv_c', 'Machine_c+d'),
            ('Inv_d', 'Machine_c+d'),
            ('Machine_a+b', 'Inv_ab'),
            ('Machine_c+d', 'Inv_cd'),
            ('Inv_ab', 'Machine_ab+cd'),
            ('Inv_cd', 'Machine_ab+cd'),
            ('Machine_ab+cd', 'Inv_abcd'),
            ('Inv_abcd', 'Sink_abcd'),
        ]
    ],
    [
        AssemblySystem.generate(
            form_product_focussed_team_assembly,
            'abc'
        ),
        [
            # Define inventory and sink for output product
            ('Inv_abc', 'Sink_abc'),
            # Define two machines that can serve the final inventory
            ('Machine_a+bc', 'Inv_abc'),
            ('Machine_ab+c', 'Inv_abc'),
            # Provide inputs to machine a+bc
            ('Source_a', 'Inv_a_1'),
            ('Inv_a_1', 'Machine_a+bc'),
            ('Source_b', 'Inv_b_1'),
            ('Inv_b_1', 'Machine_b+c'),
            ('Source_c', 'Inv_c_1'),
            ('Inv_c_1', 'Machine_b+c'),
            ('Machine_b+c', 'Inv_bc'),
            ('Inv_bc', 'Machine_a+bc'),
            # Provide inputs to machine ab+c
            ('Source_a', 'Inv_a_2'),
            ('Inv_a_2', 'Machine_a+b'),
            ('Source_b', 'Inv_b_2'),
            ('Inv_b_2', 'Machine_a+b'),
            ('Machine_a+b', 'Inv_ab'),
            ('Inv_ab', 'Machine_ab+c'),
            ('Source_c', 'Inv_c_2'),
            ('Inv_c_2', 'Machine_ab+c'),
        ]
    ],
    [
        AssemblySystem.generate(
            form_bio_inspired_assembly,
            'ABC'
        ),
        [
            # Connect sources to inventories of word length 1
            ('Source_a', 'Inv_a'),
            ('Source_b', 'Inv_b'),
            ('Source_c', 'Inv_c'),
            # Create machines and inventories for word length 2
            ('Inv_a', 'Machine_a+b'),
            ('Inv_b', 'Machine_a+b'),
            ('Inv_b', 'Machine_b+c'),
            ('Inv_c', 'Machine_b+c'),
            ('Machine_a+b', 'Inv_ab'),
            ('Machine_b+c', 'Inv_bc'),
            # Create macines and inventories for word length 3
            ('Inv_ab', 'Machine_ab+c'),
            ('Inv_c', 'Machine_ab+c'),
            ('Inv_a', 'Machine_a+bc'),
            ('Inv_bc', 'Machine_a+bc'),
            ('Machine_a+bc', 'Inv_abc'),
            ('Machine_ab+c', 'Inv_abc'),
            # Connect final inventory to sink
            ('Inv_abc', 'Sink_abc')
        ]
    ]
]


@pytest.mark.parametrize('assembly_system, edge_list', grid_test_algorithm_isomorphism)
def test_algorithms_isomorphism(assembly_system, edge_list):
    assert nx.is_isomorphic(assembly_system.to_digraph(), nx.MultiDiGraph(edge_list))
