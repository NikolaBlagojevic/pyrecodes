"""Traffic-flow accuracy tests for the scipy-backed transportation module.

These tests pin down the numerical behaviour of the traffic-assignment
logic that was previously delivered by ``pandana.Network``. They operate
at the level of ``substep_assignment`` — the routine that routes agents
along shortest paths and accumulates edge volumes — rather than
re-checking shortest-path correctness, which is covered by
``test_scipy_network.py``.

Coverage:
1. Single agent: volume is deposited on every edge of the shortest path.
2. Multi-agent linearity on a shared path.
3. Disjoint-path non-interference.
4. Flow conservation: total ``vol_true`` equals the total hops taken by
   all agents combined.
5. BPR travel-time formula on loaded and unloaded edges.
6. Residual OD generated when an edge's travel time exceeds the
   remaining quarter time.
7. Agent-time-limit removal.
8. Two-way routing with explicit reverse edges.
9. Dijkstra-cache does not corrupt results across repeated queries.
10. Damaged network: closing links reroutes agents and travel times
    rise accordingly; closing all paths gives ``inf`` travel time.
11. OD-matrix changes: scaling demand inflates travel times via BPR
    congestion feedback.
"""
# ruff: noqa: INP001

import math

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString

from residual_demand_API.transportation import (
    ScipyNetwork,
    TransportationPerformance,
)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def _build_edges_df(edges, lanes=1):
    """Build an edges DataFrame matching the schema required by
    ``substep_assignment``.

    Each ``edges`` entry is ``(start_nid, end_nid, fft)`` where ``fft`` is
    the free-flow travel time in seconds.
    """
    rows = []
    for uid, (s, e, fft) in enumerate(edges):
        rows.append({
            'uniqueid': uid,
            'u': s,
            'v': e,
            'start_nid': s,
            'end_nid': e,
            'fft': float(fft),
            'normal_fft': float(fft),
            'capacity': float(lanes * 1800),
            'normal_capacity': float(lanes * 1800),
            'length': float(fft),  # placeholder; not used by substep_assignment
            'vol_true': 0.0,
            'vol_tot': 0.0,
            'veh_current': 0.0,
            't_avg': float(fft),
            'weight': float(fft),
            'geometry': LineString([(s, 0), (e, 0)]),
        })
    df = pd.DataFrame(rows)
    df['edge_str'] = (
        df['start_nid'].astype(str) + '-' + df['end_nid'].astype(str)
    )
    return df.set_index('edge_str')


def _build_nodes_df(node_ids):
    """Build a nodes DataFrame indexed by node_id with ``x`` / ``y`` cols."""
    df = pd.DataFrame({
        'node_id': list(node_ids),
        'x': [float(nid) for nid in node_ids],
        'y': [0.0 for _ in node_ids],
    }).set_index('node_id')
    return df


def _build_od_df(od_pairs):
    """Build an OD DataFrame. ``od_pairs`` items: (agent_id, origin, destin)."""
    rows = [{
        'agent_id': a,
        'origin_nid': o,
        'destin_nid': d,
        'current_nid': o,
        'current_link': None,
        'current_link_time': 0,
    } for (a, o, d) in od_pairs]
    return pd.DataFrame(rows)


def _empty_trip_info(od_pairs, hour=0, quarter=0):
    return {
        (a, o, d): [0, 0, o, 0, hour, quarter, 0, 0]
        for (a, o, d) in od_pairs
    }


def _run_substep(simulator, nodes, edges, od_pairs, **overrides):
    """Run ``substep_assignment`` with sensible defaults for these tests."""
    od = _build_od_df(od_pairs)
    trip_info = _empty_trip_info(od_pairs)
    kwargs = dict(
        nodes_df=nodes,
        weighted_edges_df=edges,
        od_ss=od,
        quarter_demand=len(od_pairs),
        assigned_demand=len(od_pairs),
        quarter_counts=4,
        trip_info=trip_info,
        agent_time_limit=None,
        sample_interval=1,
        agents_path=None,
        hour=0,
        quarter=0,
        ss_id=0,
    )
    kwargs.update(overrides)
    return simulator.substep_assignment(**kwargs)


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #

@pytest.fixture
def simulator():
    """Bare ``TransportationPerformance``; only ``substep_assignment`` is used."""
    return TransportationPerformance()


@pytest.fixture
def diamond():
    """Two parallel paths from 1 to 4:
    upper: 1->2->4 with fft 5+5 = 10
    lower: 1->3->4 with fft 30+30 = 60
    """
    nodes = _build_nodes_df([1, 2, 3, 4])
    edges = _build_edges_df([(1, 2, 5), (2, 4, 5), (1, 3, 30), (3, 4, 30)])
    return nodes, edges


# --------------------------------------------------------------------------- #
# Single agent                                                                #
# --------------------------------------------------------------------------- #

class TestSubstepAssignmentSingleAgent:

    def test_volumes_placed_on_shortest_path(self, simulator, diamond):
        """A single 1->4 agent should put vol_true=1 on the upper-path edges
        and leave lower-path edges at zero."""
        nodes, edges = diamond
        new_edges, residual, trip_info_out, _ = _run_substep(
            simulator, nodes, edges, [(0, 1, 4)],
        )
        assert new_edges.loc['1-2', 'vol_true'] == 1
        assert new_edges.loc['2-4', 'vol_true'] == 1
        assert new_edges.loc['1-3', 'vol_true'] == 0
        assert new_edges.loc['3-4', 'vol_true'] == 0
        assert residual == []
        # Trip-info slots: [travel_time, used_time, stop_nid, ...]
        assert trip_info_out[(0, 1, 4)][0] == 3600 / 4
        assert trip_info_out[(0, 1, 4)][1] == 10
        assert trip_info_out[(0, 1, 4)][2] == 4

# --------------------------------------------------------------------------- #
# Multi-agent linearity and flow conservation                                 #
# --------------------------------------------------------------------------- #

class TestSubstepAssignmentMultiAgent:

    def test_shared_path_volumes_scale_linearly(self, simulator, diamond):
        """Five agents on the same 1->4 path ⇒ vol_true=5 on each
        traversed edge."""
        nodes, edges = diamond
        num_agents = 5
        pairs = [(i, 1, 4) for i in range(num_agents)]
        new_edges, _, _, _ = _run_substep(simulator, nodes, edges, pairs)
        assert new_edges.loc['1-2', 'vol_true'] == num_agents
        assert new_edges.loc['2-4', 'vol_true'] == num_agents
        assert new_edges.loc['1-3', 'vol_true'] == 0
        assert new_edges.loc['3-4', 'vol_true'] == 0

    def test_disjoint_paths_dont_interfere(self, simulator):
        """Two agents on disjoint subnetworks deposit volume only on their
        own edges."""
        nodes = _build_nodes_df([1, 2, 3, 4, 5, 6])
        edges = _build_edges_df([
            (1, 2, 5), (2, 3, 5), (4, 5, 5), (5, 6, 5),
        ])
        new_edges, _, _, _ = _run_substep(
            simulator, nodes, edges, [(0, 1, 3), (1, 4, 6)],
        )
        assert new_edges.loc['1-2', 'vol_true'] == 1
        assert new_edges.loc['2-3', 'vol_true'] == 1
        assert new_edges.loc['4-5', 'vol_true'] == 1
        assert new_edges.loc['5-6', 'vol_true'] == 1

    def test_flow_conservation_matches_hop_count(self, simulator):
        """Total ``vol_true`` across edges equals the total number of
        edges traversed by all agents combined — the substep-level
        flow-conservation identity."""
        nodes = _build_nodes_df([1, 2, 3, 4, 5])
        edges = _build_edges_df([
            (1, 2, 10), (2, 3, 10), (3, 4, 10), (4, 5, 10),
        ])
        # Three agents with hop counts 4 + 3 + 2 = 9
        pairs = [(0, 1, 5), (1, 2, 5), (2, 1, 3)]
        expected_hops = 4 + 3 + 2
        new_edges, residual, _, _ = _run_substep(
            simulator, nodes, edges, pairs,
        )
        assert residual == []
        assert new_edges['vol_true'].sum() == expected_hops


# --------------------------------------------------------------------------- #
# BPR travel-time formula                                                     #
# --------------------------------------------------------------------------- #

class TestBPRTravelTimeFormula:
    """``t_avg = fft * (1 + alpha * (flow/capacity)**beta)`` with a hard
    cap at 36000 s (see ``substep_assignment``)."""

    def test_bpr_applied_to_loaded_edges(self, simulator):
        nodes = _build_nodes_df([1, 2, 3])
        edges = _build_edges_df([(1, 2, 100), (2, 3, 100)])
        pairs = [(i, 1, 3) for i in range(10)]
        alpha, beta, quarter_counts = 0.3, 4, 4

        new_edges, _, _, _ = _run_substep(
            simulator, nodes, edges, pairs,
            alpha_f=alpha, beta_f=beta, quarter_counts=quarter_counts,
        )
        # vol_true=10, quarter_demand=assigned_demand=10, quarter_counts=4
        # => flow = 10 * (10/10) * 4 = 40
        # capacity = 1 * 1800 = 1800
        expected_t_avg = round(100 * (1 + alpha * (40 / 1800) ** beta), 2)
        assert new_edges.loc['1-2', 't_avg'] == pytest.approx(expected_t_avg)
        assert new_edges.loc['2-3', 't_avg'] == pytest.approx(expected_t_avg)

    def test_unloaded_edges_keep_fft(self, simulator, diamond):
        """Edges not traversed by any agent have flow=0 ⇒ t_avg == fft."""
        nodes, edges = diamond
        new_edges, _, _, _ = _run_substep(
            simulator, nodes, edges, [(0, 1, 4)],
        )
        assert new_edges.loc['1-3', 't_avg'] == pytest.approx(
            new_edges.loc['1-3', 'fft'],
        )
        assert new_edges.loc['3-4', 't_avg'] == pytest.approx(
            new_edges.loc['3-4', 'fft'],
        )

    def test_bpr_capped_at_36000(self, simulator):
        """Severely overloaded edges have ``t_avg`` clamped to 36000 s.

        Uses ``fft=100`` — smaller than the per-substep budget
        (``3600/4 = 900 s``) so every agent actually traverses the edge
        and vol_true climbs into the capped BPR regime. With 3000 agents
        and capacity 1800, ``flow = 3000 * 1 * 4 = 12000`` and
        ``t_avg_raw = 100 * (1 + 0.3 * (12000/1800)**4) ≈ 59408 s``,
        well above the 36000 cap.
        """
        nodes = _build_nodes_df([1, 2])
        edges = _build_edges_df([(1, 2, 100)])
        pairs = [(i, 1, 2) for i in range(3000)]
        new_edges, _, _, _ = _run_substep(
            simulator, nodes, edges, pairs, alpha_f=0.3, beta_f=4,
        )
        assert new_edges.loc['1-2', 't_avg'] == 36000


# --------------------------------------------------------------------------- #
# Residual OD generation                                                      #
# --------------------------------------------------------------------------- #

class TestResidualODGeneration:

    def test_residual_created_when_edge_takes_too_long(self, simulator):
        """If the next edge's travel time exceeds remaining_time, an entry
        is appended to ``od_residual_ss_list`` with the current edge and
        residual time."""
        nodes = _build_nodes_df([1, 2, 3])
        # remaining_time = 3600/4 = 900 s.
        # Edge 1-2 fft=10 (consumed). Edge 2-3 fft=10000 (too long).
        edges = _build_edges_df([(1, 2, 10), (2, 3, 10000)])
        new_edges, residual, trip_info_out, _ = _run_substep(
            simulator, nodes, edges, [(7, 1, 3)],
        )
        assert len(residual) == 1
        entry = residual[0]
        # Layout: [agent_id, origin, destin, trip_stop, current_link,
        #          current_link_time]
        assert entry[0] == 7
        assert entry[1] == 1
        assert entry[2] == 3
        assert entry[3] == 2       # stopped at node 2
        assert entry[4] == '2-3'   # unfinished edge
        assert entry[5] == pytest.approx(3600 / 4 - 10)
        assert new_edges.loc['1-2', 'vol_true'] == 1
        assert new_edges.loc['2-3', 'vol_true'] == 0
        assert trip_info_out[(7, 1, 3)][1] == 10

    def test_agent_time_limit_removes_agent(self, simulator):
        """If the shortest-path length exceeds ``agent_time_limit`` the
        agent is dropped: no volume, no residual, trip_info untouched."""
        nodes = _build_nodes_df([1, 2, 3])
        edges = _build_edges_df([(1, 2, 100), (2, 3, 100)])
        new_edges, residual, trip_info_out, _ = _run_substep(
            simulator, nodes, edges, [(0, 1, 3)],
            agent_time_limit=50,  # full trip is 200 s, exceeds limit
        )
        assert new_edges['vol_true'].sum() == 0
        assert residual == []
        assert trip_info_out[(0, 1, 3)][0] == 0


# --------------------------------------------------------------------------- #
# Two-way routing                                                             #
# --------------------------------------------------------------------------- #

class TestTwoWayRouting:
    """The caller-side convention (``pyrecodes_residual_demand.__init__``)
    is to duplicate edges with flipped endpoints before handing them to
    ``substep_assignment``. We pin down both this working pattern and the
    failure mode when the convention isn't followed."""

    def test_twoway_with_explicit_reverse_edges(self, simulator):
        """With an explicit reverse edge, a 2->1 agent registers volume
        on the '2-1' edge entry."""
        nodes = _build_nodes_df([1, 2])
        edges = _build_edges_df([(1, 2, 10), (2, 1, 10)])
        new_edges, residual, _, _ = _run_substep(
            simulator, nodes, edges, [(0, 2, 1)], two_way_edges=True,
        )
        assert new_edges.loc['2-1', 'vol_true'] == 1
        assert new_edges.loc['1-2', 'vol_true'] == 0
        assert residual == []

    def test_twoway_without_reverse_edges_raises(self, simulator):
        """Without an explicit reverse edge, the reverse traversal's
        lookup on '2-1' in the edge dict fails with ``KeyError``. Pinning
        this down so future refactors notice the caller-side contract."""
        nodes = _build_nodes_df([1, 2])
        edges = _build_edges_df([(1, 2, 10)])
        with pytest.raises(KeyError):
            _run_substep(
                simulator, nodes, edges, [(0, 2, 1)], two_way_edges=True,
            )


# --------------------------------------------------------------------------- #
# Caching regression guards                                                   #
# --------------------------------------------------------------------------- #

class TestCachingCorrectness:
    """Regression guards for the per-source dijkstra cache in
    ``ScipyNetwork``."""

    def test_repeated_queries_give_identical_results(self):
        node_ids = [1, 2, 3]
        xs = pd.Series([0.0, 1.0, 2.0], index=node_ids)
        ys = pd.Series([0.0, 0.0, 0.0], index=node_ids)
        edge_df = pd.DataFrame({'w': [1.0, 2.0]})
        net = ScipyNetwork(
            xs, ys, [1, 2], [2, 3], edge_df[['w']], twoway=False,
        )
        origins = np.array([1, 1, 1])
        dests = np.array([3, 3, 3])

        first = net.shortest_paths(origins, dests)
        second = net.shortest_paths(origins, dests)
        third = net.shortest_path_lengths(origins, dests)
        fourth = net.shortest_path_lengths(origins, dests)

        assert first == second == [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
        assert third == fourth == [pytest.approx(3.0)] * 3

    def test_query_order_does_not_affect_results(self):
        node_ids = [0, 1, 2, 3]
        xs = pd.Series([0.0, 1.0, 2.0, 3.0], index=node_ids)
        ys = pd.Series([0.0, 0.0, 0.0, 0.0], index=node_ids)
        # 0->1 (w=1), 1->2 (w=2), 2->3 (w=3), 0->2 (w=4)
        edge_df = pd.DataFrame({'w': [1.0, 2.0, 3.0, 4.0]})
        build = lambda: ScipyNetwork(  # noqa: E731
            xs, ys, [0, 1, 2, 0], [1, 2, 3, 2], edge_df[['w']], twoway=False,
        )
        net_a = build()
        net_b = build()

        pairs_a = [(0, 3), (1, 3), (0, 2), (0, 3)]
        pairs_b = [(0, 2), (0, 3), (0, 3), (1, 3)]

        out_a = {
            p: net_a.shortest_path_lengths(np.array([p[0]]), np.array([p[1]]))[0]
            for p in pairs_a
        }
        out_b = {
            p: net_b.shortest_path_lengths(np.array([p[0]]), np.array([p[1]]))[0]
            for p in pairs_b
        }
        for key in out_a:
            assert out_a[key] == pytest.approx(out_b[key])


# --------------------------------------------------------------------------- #
# Assignment-level helpers                                                    #
# --------------------------------------------------------------------------- #

def _build_od_all(od_triples, hour=0, quarter=0):
    """Build an ``od_all`` DataFrame for ``assignment``.

    Uses explicit ``quarter`` values so the quarter assignment is
    deterministic (``assignment`` bypasses its ``np.random.choice`` branch
    when the column is already present).
    """
    rows = [{
        'agent_id': a,
        'origin_nid': o,
        'destin_nid': d,
        'hour': hour,
        'quarter': quarter,
    } for (a, o, d) in od_triples]
    return pd.DataFrame(rows)


def _run_assignment(simulator, nodes, edges, od_triples, closed_uniqueids=(),
                    quarter_counts=4, alpha_f=0.3, beta_f=4,
                    substep_size=30000, seed=42):
    """Run ``assignment`` with save_edge_vol=False (no file I/O) and return
    the per-agent ``trip_info_df``.

    ``closed_uniqueids`` is a sequence of edge ``uniqueid`` values to mark
    as closed. A fixed ``seed`` is set so that ``np.random.choice``
    substep distribution is deterministic.
    """
    closed_links = pd.DataFrame({'uniqueid': list(closed_uniqueids)})
    od_all = _build_od_all(od_triples)
    np.random.seed(seed)
    return simulator.assignment(
        edges_df=edges.copy(),
        nodes_df=nodes,
        od_all=od_all,
        simulation_outputs=None,
        scen_nm='test',
        hour_list=[0],
        quarter_list=[0],
        closure_hours=[0],
        closed_links=closed_links,
        quarter_counts=quarter_counts,
        substep_size=substep_size,
        alpha_f=alpha_f,
        beta_f=beta_f,
        save_edge_vol=False,
    )


# --------------------------------------------------------------------------- #
# Damaged-network travel-time response                                        #
# --------------------------------------------------------------------------- #

class TestDamagedNetworkTravelTimes:
    """Closing links in a simple network should reroute agents onto the
    next-best path and inflate travel time; closing all paths should
    mark the trip as unreachable (travel_time_used == inf)."""

    @pytest.fixture
    def damage_diamond(self):
        """Diamond with two parallel 1->4 paths:
        upper: 1-(100)-2-(100)-4  (total fft 200)
        lower: 1-(300)-3-(300)-4  (total fft 600)
        uniqueids: 0=1-2, 1=2-4, 2=1-3, 3=3-4
        """
        nodes = _build_nodes_df([1, 2, 3, 4])
        edges = _build_edges_df([
            (1, 2, 100), (2, 4, 100), (1, 3, 300), (3, 4, 300),
        ])
        return nodes, edges

    def test_undamaged_uses_shortest_path_travel_time(
        self, simulator, damage_diamond,
    ):
        """With no damage, a single 1->4 agent has
        travel_time_used == fft(1-2) + fft(2-4) == 200."""
        nodes, edges = damage_diamond
        trip_info_df = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
        )
        assert trip_info_df.loc[0, 'travel_time_used'] == pytest.approx(200)

    def test_closing_short_path_forces_longer_route(
        self, simulator, damage_diamond,
    ):
        """Closing the upper (short) path forces the agent to the lower
        route. travel_time_used rises from 200 s to 600 s."""
        nodes, edges = damage_diamond
        baseline = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
        )
        damaged = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
            closed_uniqueids=[0, 1],  # close 1-2 and 2-4
        )
        assert baseline.loc[0, 'travel_time_used'] == pytest.approx(200)
        assert damaged.loc[0, 'travel_time_used'] == pytest.approx(600)
        assert (
            damaged.loc[0, 'travel_time_used']
            > baseline.loc[0, 'travel_time_used']
        )

    def test_closing_one_link_on_short_path_is_enough_to_reroute(
        self, simulator, damage_diamond,
    ):
        """Closing a single critical link on the shortest path still
        forces the longer route."""
        nodes, edges = damage_diamond
        damaged = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
            closed_uniqueids=[1],  # close only 2-4
        )
        assert damaged.loc[0, 'travel_time_used'] == pytest.approx(600)

    def test_closing_all_paths_yields_inf_travel_time(
        self, simulator, damage_diamond,
    ):
        """With every 1->4 path severed, the agent is marked unreachable
        and travel_time_used is inf (see ``assignment``'s no-path branch)."""
        nodes, edges = damage_diamond
        damaged = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
            closed_uniqueids=[0, 1, 2, 3],  # every edge closed
        )
        assert math.isinf(damaged.loc[0, 'travel_time_used'])

    def test_travel_times_monotonic_in_damage(
        self, simulator, damage_diamond,
    ):
        """Travel time should be monotonically non-decreasing as more
        damage is applied: undamaged <= partial damage <= full closure."""
        nodes, edges = damage_diamond
        undamaged = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
        ).loc[0, 'travel_time_used']
        partial = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
            closed_uniqueids=[0],  # close one edge on short path
        ).loc[0, 'travel_time_used']
        full = _run_assignment(
            simulator, nodes, edges, [(0, 1, 4)],
            closed_uniqueids=[0, 1, 2, 3],
        ).loc[0, 'travel_time_used']
        assert undamaged <= partial <= full


# --------------------------------------------------------------------------- #
# OD-matrix sensitivity                                                       #
# --------------------------------------------------------------------------- #

class TestODMatrixTravelTimes:
    """Changes to the OD matrix should propagate to travel times via the
    BPR congestion feedback loop. Each substep within a quarter updates
    ``t_avg`` from the cumulative flow, so agents routed in *later*
    substeps of the same quarter traverse each edge at the
    congestion-inflated travel time while agents in the first substep
    experience fft.

    These tests force multiple substeps via ``substep_size=50``.
    Parameters are chosen so that the BPR-inflated ``t_avg`` never
    exceeds the per-substep remaining time (``3600 / quarter_counts``),
    which would otherwise bounce agents into the residual-OD queue and
    confound the comparison."""

    @pytest.fixture
    def chain_network(self):
        """Single-path 1->2->3 with ``fft=200`` per edge (trip = 400 s)."""
        nodes = _build_nodes_df([1, 2, 3])
        edges = _build_edges_df([(1, 2, 200), (2, 3, 200)], lanes=1)
        return nodes, edges

    def test_baseline_od_uses_fft(self, simulator, chain_network):
        """Sanity baseline: a small OD on the chain gives mean travel
        time == fft_sum. Without this anchor, a drift in the chain
        fixture would silently invalidate the comparison tests below."""
        nodes, edges = chain_network
        trips = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(5)],
        )
        assert trips['travel_time_used'].mean() == pytest.approx(400)

    def test_more_trips_raise_mean_travel_time_via_bpr(
        self, simulator, chain_network,
    ):
        """Scaling OD from 5 agents up to 450 agents on a 1-lane chain
        triggers BPR feedback.

        At 450 agents with ``quarter_counts=4``, ``flow = 450*4 = 1800 ==
        capacity`` so BPR factor = ``1 + 0.3 * 1**4 = 1.3`` ⇒ per-edge
        ``t_avg`` rises from 200 s to 260 s, which is still well below
        the per-substep budget of 900 s. With ``substep_size=50``,
        substeps 1..N see the congested ``t_avg`` while substep 0 still
        uses fft — so the mean is strictly between fft_sum (400) and
        the fully-congested trip time (520)."""
        nodes, edges = chain_network

        light = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(5)],
            quarter_counts=4, substep_size=50,
        )
        heavy = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(450)],
            quarter_counts=4, substep_size=50,
        )

        light_mean = light['travel_time_used'].mean()
        heavy_mean = heavy['travel_time_used'].mean()

        # Low demand: one substep, all agents at fft.
        assert light_mean == pytest.approx(400)
        # Heavy demand: BPR-inflated t_avg applies from substep 1 onward.
        assert heavy_mean > light_mean
        # Upper bound: fully-congested trip time = 2 edges * 260 s.
        assert heavy_mean <= 520

    def test_double_demand_increases_travel_time_more_than_baseline(
        self, simulator, chain_network,
    ):
        """Monotonicity check: doubling the OD demand should not reduce
        the mean travel time — this pins down the sign of the
        BPR-feedback response."""
        nodes, edges = chain_network
        base = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(225)],
            quarter_counts=4, substep_size=50,
        )
        doubled = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(450)],
            quarter_counts=4, substep_size=50,
        )
        assert (
            doubled['travel_time_used'].mean()
            >= base['travel_time_used'].mean()
        )

    def test_different_od_pairs_yield_different_travel_times(
        self, simulator,
    ):
        """Changing *which* pairs travel (not just how many) should
        change the resulting travel times, because OD pairs with
        different origins/destinations consume different edge
        combinations."""
        nodes = _build_nodes_df([1, 2, 3])
        edges = _build_edges_df([(1, 2, 100), (2, 3, 400)], lanes=1)
        # OD set A: short trip 1 -> 2 (fft = 100)
        short_trips = _run_assignment(
            simulator, nodes, edges, [(i, 1, 2) for i in range(3)],
        )
        # OD set B: full trip 1 -> 3 (fft = 500)
        long_trips = _run_assignment(
            simulator, nodes, edges, [(i, 1, 3) for i in range(3)],
        )
        assert short_trips['travel_time_used'].mean() == pytest.approx(100)
        assert long_trips['travel_time_used'].mean() == pytest.approx(500)
        assert (
            long_trips['travel_time_used'].mean()
            > short_trips['travel_time_used'].mean()
        )
