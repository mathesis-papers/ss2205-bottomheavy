import hashlib
import itertools
import json
import math
from pathlib import Path


def trim(coefficients):
    while coefficients and coefficients[-1] == 0:
        coefficients.pop()
    return tuple(coefficients)


def add(left, right):
    coefficients = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        coefficients[index] += value
    for index, value in enumerate(right):
        coefficients[index] += value
    return trim(coefficients)


def scale(polynomial, weight):
    return trim([weight * value for value in polynomial])


def multiply_interval(polynomial, length):
    if length == 0 or not polynomial:
        return ()
    coefficients = []
    window = 0
    for index in range(len(polynomial) + length - 1):
        if index < len(polynomial):
            window += polynomial[index]
        if 0 <= index - length < len(polynomial):
            window -= polynomial[index - length]
        coefficients.append(window)
    return trim(coefficients)


def convolve(left, right):
    if not left or not right:
        return ()
    coefficients = [0] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            coefficients[left_index + right_index] += left_value * right_value
    return trim(coefficients)


def product(lengths):
    polynomial = (1,)
    for length in lengths:
        polynomial = convolve(polynomial, (1,) * length)
    return polynomial


def check_bottom(polynomial, ambient=None):
    degree = max(0, len(polynomial) - 1) if ambient is None else ambient
    comparisons = 0
    for index in range((degree + 1) // 2):
        lower = polynomial[index] if index < len(polynomial) else 0
        reflected = degree - index
        upper = polynomial[reflected] if reflected < len(polynomial) else 0
        assert upper <= lower, (polynomial, degree, index)
        comparisons += 1
    return comparisons


def check_tail(polynomial):
    degree = max(0, len(polynomial) - 1)
    comparisons = 0
    for index in range((degree + 1) // 2, degree):
        assert polynomial[index] >= polynomial[index + 1]
        comparisons += 1
    return comparisons


def symmetric_value(lengths, order, complete):
    if order < 0:
        return ()
    values = [(1,)] + [()] * order
    for length in lengths:
        indices = range(1, order + 1) if complete else range(order, 0, -1)
        for index in indices:
            values[index] = add(values[index], convolve(values[index - 1], (1,) * length))
    return values[order]


def main():
    maximum = 50
    families = ['S', 'c', 'SB', 'cB']
    previous = {family: {0: (1,)} for family in families}
    count = 0
    comparisons = 0
    tail_comparisons = 0
    identities = 0
    symmetry_checks = 0
    positivity_checks = 0
    ordered_checks = 0
    alternating_checks = 0
    examples = {}
    for row in range(maximum + 1):
        if row:
            current = {family: {} for family in families}
            for column in range(row + 1):
                lengths = [column, row - 1, 2 * column + 1, 2 * row - 1]
                for family, length in zip(families, lengths):
                    current[family][column] = add(
                        previous[family].get(column - 1, ()),
                        multiply_interval(previous[family].get(column, ()), length),
                    )
            previous = current
        for family in families:
            for column in range(-3, 54):
                polynomial = previous[family].get(column, ())
                assert all(value > 0 for value in polynomial)
                positivity_checks += bool(polynomial)
                if row and polynomial:
                    symmetric_case = column in ([1, row] if family in ['S', 'c'] else [0, row])
                    assert (polynomial == polynomial[::-1]) == symmetric_case
                    if not symmetric_case:
                        assert polynomial[0] > polynomial[-1]
                    symmetry_checks += 1
                comparisons += check_bottom(polynomial)
                tail_comparisons += check_tail(polynomial)
                count += 1
            if row <= 8:
                for column in range(row + 2):
                    if family == 'S':
                        lengths = range(1, column + 1)
                    elif family == 'c':
                        lengths = range(row)
                    elif family == 'SB':
                        lengths = range(1, 2 * column + 2, 2)
                    else:
                        lengths = range(1, 2 * row, 2)
                    expanded = symmetric_value(lengths, row - column, family in ['S', 'SB'])
                    assert expanded == previous[family].get(column, ()), (family, row, column)
                    identities += 1
            if row <= 12 and family in ['S', 'SB']:
                for column in range(row + 1):
                    lengths = range(1, column + 1) if family == 'S' else range(2, 2 * column + 1, 2)
                    ordered = convolve(previous[family].get(column, ()), product(lengths))
                    check_bottom(ordered)
                    check_tail(ordered)
                    ordered_checks += 1
        if row <= 30:
            alternating = ()
            for column in range(row + 1):
                ordered = convolve(previous['S'].get(column, ()), product(range(1, column + 1)))
                shifted = (0,) * (2 * (row - column)) + scale(ordered, (-1) ** (row - column))
                alternating = add(alternating, shifted)
            alternating = add(alternating, (-1,))
            expected = trim([0] + [math.comb(row, index) - math.comb(row, index - 1) for index in range(1, row + 1)])
            assert alternating == expected, (row, alternating, expected)
            if row >= 2:
                assert alternating[0] == 0
                assert alternating[1:] == tuple(-value for value in alternating[:0:-1])
                absolute_normalized = tuple(abs(value) for value in alternating[1:])
                assert absolute_normalized == absolute_normalized[::-1]
            if row == 2:
                assert alternating == (0, 1, -1)
                assert tuple(abs(value) for value in alternating) != tuple(abs(value) for value in alternating[::-1])
            alternating_checks += 1
        for family, target_row, column in [('S', 4, 3), ('SB', 6, 4), ('cB', 7, 5)]:
            if row == target_row:
                examples[f'{family}[{row},{column}]'] = list(previous[family][column])
    assert examples['S[4,3]'] == [3, 2, 1]
    assert examples['SB[6,4]'] == [15, 24, 34, 38, 43, 42, 43, 38, 35, 26, 20, 14, 10, 6, 4, 2, 1]
    assert examples['cB[7,5]'] == [21, 36, 51, 60, 70, 74, 79, 78, 79, 74, 71, 62, 56, 44, 35, 26, 20, 14, 10, 6, 4, 2, 1]
    assert examples['SB[6,4]'][4] > examples['SB[6,4]'][5] < examples['SB[6,4]'][6]
    assert examples['cB[7,5]'][6] > examples['cB[7,5]'][7] < examples['cB[7,5]'][8]
    product_count = 0
    ambient_comparisons = 0
    for size in range(5):
        for lengths in itertools.product(range(1, 7), repeat=size):
            polynomial = product(lengths)
            assert polynomial == polynomial[::-1]
            degree = len(polynomial) - 1
            assert all(polynomial[index] <= polynomial[index + 1] for index in range(degree // 2))
            for ambient in range(degree, degree + 13):
                ambient_comparisons += check_bottom(polynomial, ambient)
            product_count += 1
    short_products = [product(lengths) for size in range(3) for lengths in itertools.product(range(1, 5), repeat=size)]
    mixtures = 0
    defect_comparisons = 0
    for left, right in itertools.product(short_products, repeat=2):
        for left_weight, right_weight in itertools.product(range(4), repeat=2):
            polynomial = add(scale(left, left_weight), scale(right, right_weight))
            check_bottom(polynomial)
            check_tail(polynomial)
            if polynomial:
                degree = len(polynomial) - 1
                for index in range((degree + 1) // 2):
                    defect = 0
                    for summand, weight in [(left, left_weight), (right, right_weight)]:
                        summand_degree = len(summand) - 1
                        for layer in range(summand_degree // 2 + 1):
                            difference = summand[layer] - (summand[layer - 1] if layer else 0)
                            if layer <= index <= summand_degree - layer < degree - index:
                                defect += weight * difference
                    assert polynomial[index] - polynomial[degree - index] == defect
                    defect_comparisons += 1
            mixtures += 1
    for left_length in range(1, 13):
        for right_length in range(1, 13):
            layered = ()
            for offset in range(min(left_length, right_length)):
                layer = (0,) * offset + (1,) * (left_length + right_length - 1 - 2 * offset)
                layered = add(layered, layer)
            assert layered == convolve((1,) * left_length, (1,) * right_length)
    assert product([2, 2]) == (1, 2, 1)
    assert product([2, 2])[1] > product([2, 2])[0]
    assert (0, 1)[1] > (0, 1)[0]
    chain_products = 0
    chain_objects = 0
    chain_injections = 0
    for size in range(5):
        for lengths in itertools.product(range(1, 5), repeat=size):
            chains = symmetric_chains(lengths)
            objects = [element for chain in chains for element in chain]
            assert len(objects) == math.prod(lengths)
            assert len(set(objects)) == len(objects)
            assert set(objects) == set(itertools.product(*(range(length) for length in lengths)))
            degree = sum(length - 1 for length in lengths)
            for chain in chains:
                assert sum(chain[0]) + sum(chain[-1]) == degree
                assert all(sum(right) == sum(left) + 1 for left, right in zip(chain, chain[1:]))
            for ambient in range(degree, degree + 5):
                for index in range((ambient + 1) // 2):
                    images = []
                    domain = []
                    for chain in chains:
                        first = sum(chain[0])
                        last = sum(chain[-1])
                        if first <= ambient - index <= last:
                            image = chain[index - first]
                            assert sum(image) == index
                            domain.append(chain[ambient - index - first])
                            images.append(image)
                    assert len(images) == len(set(images))
                    assert len(domain) == sum(sum(element) == ambient - index for element in objects)
                    chain_injections += len(images)
            chain_products += 1
            chain_objects += len(objects)
    complex_checks, complex_identities, reverse_checks = check_complex_families()
    report = {
        'schema_version': 1,
        'arithmetic': 'exact integers',
        'recurrence_range': {'n': [0, maximum], 'k': [-3, 53]},
        'polynomials': count,
        'bottom_heavy_comparisons': comparisons,
        'upper_half_comparisons': tail_comparisons,
        'symmetric_function_identities': identities,
        'symmetric_function_n_max': 8,
        'products': product_count,
        'product_range': {'factors': [0, 4], 'lengths': [1, 6]},
        'ambient_extra_degree': [0, 12],
        'ambient_comparisons': ambient_comparisons,
        'weighted_mixtures': mixtures,
        'positive_support_checks': positivity_checks,
        'symmetric_entry_classifications': symmetry_checks,
        'ordered_family_checks': ordered_checks,
        'reflection_defect_identities': defect_comparisons,
        'symmetric_chain_products': chain_products,
        'symmetric_chain_objects': chain_objects,
        'injected_objects': chain_injections,
        'chain_range': {'factors': [0, 4], 'lengths': [1, 4], 'extra_ambient_degree': [0, 4]},
        'complex_group_polynomials_including_ordered': complex_checks,
        'complex_group_symmetric_identities': complex_identities,
        'complex_group_range': {'m': [2, 5], 'n': [0, 10], 'k': '0 through n'},
        'reversed_hilbert_checks': reverse_checks,
        'alternating_sum_identities': alternating_checks,
        'alternating_sum_n_range': [0, 30],
        'mixture_range': {'factors_each': [0, 2], 'lengths': [1, 4], 'weights': [0, 3]},
        'interval_layer_identities': 144,
        'boundary_examples': {'false_ambient_bound': [1, 2, 1], 'shifted_S_2_2': [0, 1],
                              'alternating_n_2': [0, 1, -1]},
        'examples': examples,
        'status': 'all assertions satisfied',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


def rectangle_chains(width, height):
    if width > height:
        return [[(second, first) for first, second in chain] for chain in rectangle_chains(height, width)]
    return [[(offset, second) for second in range(height - offset)] +
            [(first, height - 1 - offset) for first in range(offset + 1, width)]
            for offset in range(width)]


def symmetric_chains(lengths):
    chains = [[()]]
    for length in lengths:
        expanded = []
        for chain in chains:
            for rectangle in rectangle_chains(len(chain), length):
                expanded.append([chain[first] + (second,) for first, second in rectangle])
        chains = expanded
    return chains


def check_complex_families():
    comparisons = 0
    identities = 0
    reversed_checks = 0
    for parameter in range(2, 6):
        previous = {family: {0: (1,)} for family in ['S', 'c', 'super']}
        for row in range(11):
            if row:
                current = {family: {} for family in previous}
                for column in range(row + 1):
                    lengths = [parameter * column + 1, parameter * (row - 1) + 1, parameter * (column + 1) - 1]
                    for family, length in zip(previous, lengths):
                        current[family][column] = add(previous[family].get(column - 1, ()),
                                                       multiply_interval(previous[family].get(column, ()), length))
                previous = current
            for family in previous:
                for column in range(row + 1):
                    polynomial = previous[family][column]
                    if family == 'c':
                        lengths = [parameter * index + 1 for index in range(row)]
                    elif family == 'S':
                        lengths = [parameter * index + 1 for index in range(column + 1)]
                    else:
                        lengths = [parameter * (index + 1) - 1 for index in range(column + 1)]
                    expanded = symmetric_value(lengths, row - column, family != 'c')
                    assert polynomial == expanded
                    identities += 1
                    for candidate in [polynomial, convolve(polynomial, product(range(parameter, parameter * column + 1, parameter)))]:
                        check_bottom(candidate)
                        check_tail(candidate)
                        assert all(value > 0 for value in candidate)
                        comparisons += 1
                    if family == 'S':
                        reversed_hilbert = convolve(polynomial, product(range(parameter, parameter * column + 1, parameter)))[::-1]
                        degree = len(reversed_hilbert) - 1
                        assert all(reversed_hilbert[index] <= reversed_hilbert[degree - index]
                                   for index in range((degree + 1) // 2))
                        reversed_checks += 1
    return comparisons, identities, reversed_checks


if __name__ == '__main__':
    main()
