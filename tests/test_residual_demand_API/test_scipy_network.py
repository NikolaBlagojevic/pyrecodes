"""Tests for ScipyNetwork — drop-in replacement for pandana.Network."""

import numpy as np
import pandas as pd
import pytest

from residual_demand_API.transportation import ScipyNetwork


def _make_network(nodes, edges, twoway=False):
    """Helper to build a ScipyNetwork from simple dicts.

    Args:
        nodes: dict {node_id: (x, y)}
        edges: list of (from_id, to_id, weight)
        twoway: whether edges are bidirectional
    """
    node_ids = list(nodes.keys())
    xs = pd.Series([nodes[n][0] for n in node_ids], index=node_ids, name='x')
    ys = pd.Series([nodes[n][1] for n in node_ids], index=node_ids, name='y')
    edge_from = [e[0] for e in edges]
    edge_to = [e[1] for e in edges]
    weights = [e[2] for e in edges]
    edge_df = pd.DataFrame({'weight': weights})
    return ScipyNetwork(xs, ys, edge_from, edge_to, edge_df[['weight']],
                        twoway=twoway)


class TestScipyNetworkConstruction:

    def test_node_ids_contains_all_nodes(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (1, 1)}
        edges = [(1, 2, 1.0), (2, 3, 2.0)]
        net = _make_network(nodes, edges)
        assert set(net.node_ids) == {1, 2, 3}

    def test_set_is_noop(self):
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges)
        net.set(pd.Series(net.node_ids))  # should not raise


class TestShortestPaths:

    def test_simple_chain(self):
        """1 -> 2 -> 3, weights 1 and 2."""
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0)}
        edges = [(1, 2, 1.0), (2, 3, 2.0)]
        net = _make_network(nodes, edges)
        paths = net.shortest_paths(np.array([1]), np.array([3]))
        assert len(paths) == 1
        assert paths[0] == [1, 2, 3]

    def test_shortest_path_chooses_lower_weight(self):
        """Diamond: 1->2->4 (cost 3) vs 1->3->4 (cost 5). Should pick 1->2->4."""
        nodes = {1: (0, 0), 2: (1, 1), 3: (1, -1), 4: (2, 0)}
        edges = [(1, 2, 1.0), (2, 4, 2.0), (1, 3, 2.0), (3, 4, 3.0)]
        net = _make_network(nodes, edges)
        paths = net.shortest_paths(np.array([1]), np.array([4]))
        assert paths[0] == [1, 2, 4]

    def test_no_path_returns_empty_list(self):
        """Disconnected graph: no path from 1 to 3."""
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0)}
        edges = [(1, 2, 1.0)]  # no edge to 3
        net = _make_network(nodes, edges)
        paths = net.shortest_paths(np.array([1]), np.array([3]))
        assert paths[0] == []

    def test_directed_no_reverse_path(self):
        """Edge 1->2 but not 2->1 when twoway=False."""
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges, twoway=False)
        paths = net.shortest_paths(np.array([2]), np.array([1]))
        assert paths[0] == []

    def test_twoway_allows_reverse(self):
        """Edge 1->2 with twoway=True allows 2->1."""
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges, twoway=True)
        paths = net.shortest_paths(np.array([2]), np.array([1]))
        assert paths[0] == [2, 1]

    def test_multiple_od_pairs(self):
        """Multiple OD pairs in single call."""
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0)}
        edges = [(1, 2, 1.0), (2, 3, 1.0)]
        net = _make_network(nodes, edges)
        origins = np.array([1, 1, 2])
        dests = np.array([2, 3, 3])
        paths = net.shortest_paths(origins, dests)
        assert paths[0] == [1, 2]
        assert paths[1] == [1, 2, 3]
        assert paths[2] == [2, 3]

    def test_origin_equals_destination(self):
        """Path from a node to itself."""
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges)
        paths = net.shortest_paths(np.array([1]), np.array([1]))
        assert paths[0] == [1]


class TestShortestPathLengths:

    def test_simple_chain_length(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0)}
        edges = [(1, 2, 1.0), (2, 3, 2.0)]
        net = _make_network(nodes, edges)
        lengths = net.shortest_path_lengths(np.array([1]), np.array([3]))
        assert lengths[0] == pytest.approx(3.0)

    def test_no_path_returns_inf(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges)
        lengths = net.shortest_path_lengths(np.array([1]), np.array([3]))
        assert np.isinf(lengths[0])

    def test_multiple_lengths(self):
        nodes = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (3, 0)}
        edges = [(1, 2, 1.0), (2, 3, 2.0), (3, 4, 3.0)]
        net = _make_network(nodes, edges)
        origins = np.array([1, 1, 2])
        dests = np.array([2, 4, 4])
        lengths = net.shortest_path_lengths(origins, dests)
        assert lengths[0] == pytest.approx(1.0)
        assert lengths[1] == pytest.approx(6.0)
        assert lengths[2] == pytest.approx(5.0)

    def test_twoway_length(self):
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 3.5)]
        net = _make_network(nodes, edges, twoway=True)
        lengths = net.shortest_path_lengths(np.array([2]), np.array([1]))
        assert lengths[0] == pytest.approx(3.5)

    def test_origin_equals_destination_length(self):
        nodes = {1: (0, 0), 2: (1, 0)}
        edges = [(1, 2, 1.0)]
        net = _make_network(nodes, edges)
        lengths = net.shortest_path_lengths(np.array([1]), np.array([1]))
        assert lengths[0] == pytest.approx(0.0)


class TestConsistencyPathsAndLengths:
    """Verify that shortest_paths and shortest_path_lengths give consistent results."""

    def test_path_length_matches_sum_of_edge_weights(self):
        """On a grid-like network, verify path length equals sum of edge weights along the path."""
        nodes = {0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (0, 1), 4: (1, 1), 5: (2, 1)}
        edges = [
            (0, 1, 1.0), (1, 2, 1.5), (0, 3, 2.0), (3, 4, 1.0),
            (4, 5, 1.0), (1, 4, 0.5), (2, 5, 3.0), (4, 2, 0.5),
        ]
        edge_weight = {(e[0], e[1]): e[2] for e in edges}
        net = _make_network(nodes, edges)

        origins = np.array([0, 0, 3])
        dests = np.array([5, 2, 2])
        paths = net.shortest_paths(origins, dests)
        lengths = net.shortest_path_lengths(origins, dests)

        for i, path in enumerate(paths):
            expected_length = sum(
                edge_weight[(path[j], path[j + 1])] for j in range(len(path) - 1)
            )
            assert lengths[i] == pytest.approx(expected_length), \
                f"OD pair {i}: path {path}, expected {expected_length}, got {lengths[i]}"
