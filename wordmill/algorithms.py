from wordmill.wordmill import Node, Machine, Inventory, form_edge, split_word
import math
from typing import Dict


def form_linear_assembly(sources: Dict[str, Node], sinks: Dict[str, Node]):
    inventories_to_supply = []
    for w_out, sink in sinks.items():
        inv = Inventory(w_out)
        form_edge(inv, sink)
        inventories_to_supply.append(inv)

    while len(inventories_to_supply) > 0:
        inv = inventories_to_supply.pop()
        w_left, w_right = split_word(inv.word, 1)
        m = Machine(w_left, w_right)
        form_edge(m, inv)
        inv_left = Inventory(w_left)
        form_edge(sources[w_left], inv_left)
        form_edge(inv_left, m)
        inv_right = Inventory(w_right)
        form_edge(inv_right, m)
        if w_right in sources:
            form_edge(sources[w_right], inv_right)
        else:
            inventories_to_supply.append(inv_right)


def form_component_assembly(sources: Dict[str, Node], sinks: Dict[str, Node]):
    inventories_to_supply = []
    for w_out, sink in sinks.items():
        inv = Inventory(w_out)
        form_edge(inv, sink)
        inventories_to_supply.append(inv)

    while len(inventories_to_supply) > 0:
        inv = inventories_to_supply.pop()
        if inv.word in sources:
            form_edge(sources[inv.word], inv)
        else:
            w_left, w_right = split_word(inv.word, math.floor(len(inv.word)/2.0))
            m = Machine(w_left, w_right)
            form_edge(m, inv)
            inv_left = Inventory(w_left)
            form_edge(inv_left, m)
            inv_right = Inventory(w_right)
            form_edge(inv_right, m)
            inventories_to_supply.append(inv_left)
            inventories_to_supply.append(inv_right)


def form_bio_inspired_assembly(sources: Dict[str, Node], sinks: Dict[str, Node]):
    inventories_to_supply = []
    created_inventories = dict()
    created_machines = dict()
    for w_out, sink in sinks.items():
        inv = Inventory(w_out)
        form_edge(inv, sink)
        inventories_to_supply.append(inv)
        created_inventories[w_out] = inv
    while len(inventories_to_supply) > 0:
        inv = inventories_to_supply.pop()
        w = inv.word
        if w in sources:
            form_edge(sources[w], inv)
        else:
            for i in range(1, len(w)):
                w_left, w_right = split_word(w, i)
                if (w_left, w_right) in created_inventories:
                    m = created_inventories[(w_left, w_right)]
                else:
                    m = Machine(w_left, w_right)
                    created_inventories[(w_left, w_right)] = m
                form_edge(m, inv)
                
                if w_left in created_inventories:
                    inv_left = created_inventories[w_left]
                else:
                    inv_left = Inventory(w_left)
                    inventories_to_supply.append(inv_left)
                    created_inventories[w_left] = inv_left
                form_edge(inv_left, m)
                
                if w_right in created_inventories:
                    inv_right = created_inventories[w_right]
                else:
                    inv_right = Inventory(w_right)
                    inventories_to_supply.append(inv_right)
                    created_inventories[w_right] = inv_right
                form_edge(inv_right, m)


def form_product_focussed_team_assembly(sources: Dict[str, Node], sinks: Dict[str, Node]):
    inventory_pairs = []
    for w_out, sink in sinks.items():
        inv = Inventory(w_out)
        form_edge(inv, sink)
        for i in range(1, len(w_out)):
            w_left, w_right = split_word(w_out, i)
            m = Machine(w_left, w_right)
            form_edge(m, inv)
            inv_left = Inventory(w_left)
            inv_right = Inventory(w_right)
            form_edge(inv_left, m)
            form_edge(inv_right, m)
            inventory_pairs.append((inv_left, inv_right))
    
    for inv_left, inv_right in inventory_pairs:
        created_inventories = {
            inv_left.word: inv_left,
            inv_right.word: inv_right
        }
        inventories_to_supply = [inv_left, inv_right]
        created_machines = dict()
        while len(inventories_to_supply) > 0:
            inv = inventories_to_supply.pop()
            w = inv.word
            if w in sources:
                form_edge(sources[w], inv)
            else:
                for i in range(1, len(w)):
                    w_left, w_right = split_word(w, i)
                    if (w_left, w_right) in created_machines:
                        m = created_inventories[(w_left, w_right)]
                    else:
                        m = Machine(w_left, w_right)
                        created_inventories[(w_left, w_right)] = m
                    form_edge(m, inv)
                    
                    if w_left in created_inventories:
                        inv_left = created_inventories[w_left]
                    else:
                        inv_left = Inventory(w_left)
                        inventories_to_supply.append(inv_left)
                        created_inventories[w_left] = inv_left
                    form_edge(inv_left, m)
                    
                    if w_right in created_inventories:
                        inv_right = created_inventories[w_right]
                    else:
                        inv_right = Inventory(w_right)
                        inventories_to_supply.append(inv_right)
                        created_inventories[w_right] = inv_right
                    form_edge(inv_right, m)

                    
def form_late_product_differentiation(sources: Dict[str, Node], sinks: Dict[str, Node], w_standard):
    inventories_for_standard_products = dict()
    
    def get_inventory_for_standard_product(w):
        assert w in w_standard, '{} not in set of standard words.'.format(w)
        if w not in inventories_for_standard_products:
            inv = Inventory(w)
            inventories_to_supply.append(inv)
            inventories_for_standard_products[w] = inv
        return inventories_for_standard_products[w]
    
    def get_longest_standard_product_in(w):
        best = None
        for c in w_standard:
            if c != w and c in w and (best is None or len(c) > len(best)):
                best = c
        return best

    inventories_to_supply = []

    for w_out, sink in sinks.items():
        if w_out in w_standard:
            inv = inventories_for_standard_products[w_out]
        else:
            inv = Inventory(w_out)
            inventories_to_supply.append(inv)
        form_edge(inv, sink)
    while len(inventories_to_supply) > 0:
        inv = inventories_to_supply.pop()
        w = inv.word
        if w in sources:
            form_edge(sources[w], inv)
        else:
            wst = get_longest_standard_product_in(w)
            if wst is None:
                w_left, w_right = split_word(w, 1)
                m = Machine(w_left, w_right)
                form_edge(m, inv)
                inv_left = Inventory(w_left)
                form_edge(inv_left, m)
                inv_right = Inventory(w_right)
                form_edge(inv_right, m)
                inventories_to_supply.append(inv_left)
                inventories_to_supply.append(inv_right)
            else:
                w_head = w[:w.index(wst)]
                w_tail = w[w.index(wst) + len(wst):]
                
                if len(w_head) > 0:
                    if w_head in w_standard:
                        inv_w_head = get_inventory_for_standard_product(w_head)
                    else:
                        inv_w_head = Inventory(w_head)
                        inventories_to_supply.append(inv_w_head)
                if len(w_tail) > 0:
                    if w_tail in w_standard:
                        inv_w_tail = get_inventory_for_standard_product(w_tail)
                    else:
                        inv_w_tail = Inventory(w_tail)
                        inventories_to_supply.append(inv_w_tail)
                
                if len(w_head) > 0 and len(w_tail) > 0:
                    inv_intermediate = Inventory(w_head + wst)
                    m1 = Machine(w_head, wst)
                    form_edge(m1, inv_intermediate)
                    form_edge(inv_w_head, m1)
                    form_edge(get_inventory_for_standard_product(wst), m1)
                    m2 = Machine(w_head + wst, w_tail)
                    form_edge(inv_intermediate, m2)
                    form_edge(inv_w_tail, m2)
                    form_edge(m2, inv)
                elif len(w_head) > 0:
                    m = Machine(w_head, wst)
                    form_edge(m, inv)
                    form_edge(get_inventory_for_standard_product(wst), m)
                    form_edge(inv_w_head, m)
                elif len(w_tail) > 0:
                    m = Machine(wst, w_tail)
                    form_edge(m, inv)
                    form_edge(get_inventory_for_standard_product(wst), m)
                    form_edge(inv_w_tail, m)
