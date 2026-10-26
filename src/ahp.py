"""
AHP hierarchy for 'The Thirsty Cloud'. Uses principal eigenvectors,
the Saaty RI table and the CR <= 0.1 rule. Quantitative leaves take
their local priorities from the model outputs; qualitative leaves come from
pairwise matrices with an evidence note for each judgement.

The module is imported by 06_ahp.py (base case, rainbow diagrams) and by
07_sensitivity.py (Monte Carlo on the quantitative leaves).
"""
import numpy as np
from scipy import stats

from model import STRATEGIES

RI = (0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49, 1.51, 1.54, 1.56, 1.57, 1.58)


def AHPmat(A, method="Algebra"):
    """Priority vector and consistency of a positive reciprocal matrix.

    The Algebra name is retained for callers; the principal eigenvector is
    selected directly rather than finding a determinant root near n.
    """
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1] or not len(A):
        raise ValueError("AHP matrix must be non-empty and square")
    if not np.isfinite(A).all() or (A <= 0).any():
        raise ValueError("AHP comparisons must be finite and positive")
    if not np.allclose(A * A.T, 1) or not np.allclose(np.diag(A), 1):
        raise ValueError("AHP matrix must be reciprocal with diagonal one")
    n = A.shape[0]
    if method == "Algebra":
        vals, vecs = np.linalg.eig(A)
        k = vals.real.argmax()
        lam = float(vals[k].real)
        w = vecs[:, k].real
        w = w / w.sum()
    elif method == "RGM":
        gm = stats.gmean(A, axis=1)
        w = gm / gm.sum()
        lam = (A @ w / w).mean()
    else:
        raise ValueError("Unknown AHP extraction method")
    CI = max(0., (lam - n) / (n - 1)) if n > 1 else 0.0
    CR = 0.0 if n <= 2 else CI / RI[n - 3]
    return w, lam, CI, CR


def pairwise(upper):
    """Build a reciprocal matrix from the upper-triangle entries, row by row."""
    n = int((1 + np.sqrt(1 + 8 * len(upper))) / 2)
    A = np.eye(n)
    k = 0
    for i in range(n):
        for j in range(i + 1, n):
            A[i, j] = upper[k]
            A[j, i] = 1 / upper[k]
            k += 1
    return A


def less_is_better(x, floor=0.10):
    """Local priorities for a quantitative 'less is better' leaf.
    Linear distance from the worst alternative plus a floor of 10 % of the
    range, so the worst option keeps a small but non-zero priority and the
    scale works for positive or signed values. This is a utility transformation,
    not an elicited comparison matrix, so a consistency ratio is inapplicable."""
    x = np.asarray(x, dtype=float)
    if not np.isfinite(x).all() or floor <= 0:
        raise ValueError("Scores require finite values and a positive floor")
    rng = x.max() - x.min()
    if rng == 0:
        return np.ones(len(x)) / len(x)
    s = (x.max() - x) + floor * rng
    return s / s.sum()


# ---------------------------------------------------------------- hierarchy
GOAL = "Best strategy to meet the cooling-water needs of new Singapore DCs, 2027-2035"
CRITERIA = ["C1 Economic", "C2 Environmental", "C3 Water security", "C4 Implementation"]
SUB = {
    "C1 Economic": ["C1a Societal life-cycle cost", "C1b Cost to DC operators"],
    "C2 Environmental": ["C2a GHG per MWh_IT", "C2b Electricity use", "C2c Marine discharge (brine, blowdown)"],
    "C3 Water security": ["C3a Water drawn from national supply", "C3b Weather resilience", "C3c Dependence on used-water feedstock"],
    "C4 Implementation": ["C4a Technical maturity in the tropics", "C4b Policy alignment & enforceability", "C4c Effect on other water users"],
}
QUANT = {  # leaf -> (table, column) read from model outputs; all less-is-better
    "C1a Societal life-cycle cost": ("lcc", "social_cost"),
    "C1b Cost to DC operators": ("lcc", "operator_cost"),
    "C2a GHG per MWh_IT": ("lca", "gwp_total"),
    "C2b Electricity use": ("lca", "kwh_total"),
    "C2c Marine discharge (brine, blowdown)": ("lca", "marine_m3"),
    "C3a Water drawn from national supply": ("lca", "water_from_national_supply_m3"),
}

# Sub-criteria pairwise matrices (upper triangle, row-wise) with notes
SUB_PAIRWISE = {
    "C1 Economic": ([1], "Society and operator costs weighted equally: the price-signal gap is itself a finding."),
    "C2 Environmental": ([3, 2, 1/2], "Team scenario: GHG has the greatest weight. Electricity and discharge volume are overlapping/incomplete proxies, removed in separate sensitivity cases; discharge volume is not ecological damage."),
    "C3 Water security": ([2, 2, 1], "Volume drawn is PUB's planning variable; resilience and feedstock dependence are second-order."),
    "C4 Implementation": ([1, 2, 2], "Maturity and policy fit matter equally for a 2027 start; distributional effects slightly less."),
}

# Qualitative leaves: alternatives pairwise (A1 Desal, A2 NEWater, A3 High-CoC+reuse, A4 Liquid+dry)
# Entries: A1:A2, A1:A3, A1:A4, A2:A3, A2:A4, A3:A4
QUAL_PAIRWISE = {
    "C3b Weather resilience": ([1, 1, 1, 1, 1, 1],
        "Neutral team judgment: all options must meet the same cooling reliability requirement. Both supply taps are weather-resilient. "
        "Weather effects enter WUE and the energy assumptions; there are no site reliability data to justify a further advantage."),
    "C3c Dependence on used-water feedstock": ([5, 3, 2, 1/3, 1/5, 1/2],
        "Team judgment for the NEWater-residual base case: desal needs no used-water feedstock; A2 uses most NEWater; A3/A4 use less. "
        "These ratios are illustrative, not measured scarcity or stakeholder preferences. They overlap with withdrawal and are stress-tested."),
    "C4a Technical maturity in the tropics": ([1, 2, 4, 2, 4, 2],
        "Team judgment on heat rejection: conventional towers have the longest local operating record; recovery adds treatment complexity; "
        "warm-water dry/adiabatic rejection has less public Singapore operating evidence. Liquid cooling is common to all alternatives, "
        "so its adoption and the SS 726 publication date do not distinguish the options."),
    "C4b Policy alignment & enforceability": ([1/2, 1/3, 1/3, 1/2, 1/2, 1],
        "Illustrative team ratios: NEWater and water reduction align with published efficiency objectives. A3 and A4 receive equal "
        "preference; neither receives an extra credit for liquid cooling because it is common to all. No regulator supplied these weights."),
    "C4c Effect on other water users": ([1/2, 1/4, 1/5, 1/3, 1/4, 1/2],
        "Illustrative team judgment: reducing withdrawals leaves more supply available. A tariff increase caused by this tranche has not "
        "been estimated. This leaf overlaps with withdrawal/cost and is removed with other proxies in a sensitivity case."),
}

# Weighting scenarios: main criteria pairwise (C1:C2, C1:C3, C1:C4, C2:C3, C2:C4, C3:C4)
WEIGHT_SCENARIOS = {
    "W1 Balanced": [1, 1, 1, 1, 1, 1],
    "W2 PUB / water security": [1, 1/4, 1/2, 1/4, 1/2, 3],
    "W3 Operator / economic": [4, 3, 2, 1, 1/2, 1/2],
    "W4 Climate (EMA, NGOs)": [1/4, 1/2, 1, 3, 4, 1],
    "W5 Growth (IMDA, EDB)": [2, 2, 1, 1, 1/3, 1/3],
}


_QUAL_CACHE = {}


def quantitative_values(L, C):
    """Pull the quantitative leaf values (one per strategy) from lca/lcc tables."""
    L = L.copy()
    L["marine_m3"] = L["brine_m3"] + L["blowdown_discharge_m3"]
    vals = {}
    for leaf, (tab, col) in QUANT.items():
        src = L if tab == "lca" else C
        vals[leaf] = np.array([src.loc[a, col] for a in STRATEGIES])
    return vals


def local_priorities(L, C, floor=0.10, qualitative=None):
    """Local priority matrix W[criterion] of shape (alternatives x sub-criteria), plus CRs."""
    q = quantitative_values(L, C)
    W, CR = {}, {}
    for cr, leaves in SUB.items():
        cols = []
        for leaf in leaves:
            if leaf in q:
                cols.append(less_is_better(q[leaf], floor))
                CR[leaf] = np.nan
            else:
                if qualitative is not None:
                    w, lam, ci, cr_ = AHPmat(qualitative[leaf])
                elif leaf not in _QUAL_CACHE:
                    _QUAL_CACHE[leaf] = AHPmat(pairwise(QUAL_PAIRWISE[leaf][0]))
                    w, lam, ci, cr_ = _QUAL_CACHE[leaf]
                else:
                    w, lam, ci, cr_ = _QUAL_CACHE[leaf]
                cols.append(w)
                CR[leaf] = cr_
        W[cr] = np.array(cols).T
    return W, CR, q


def sub_weights():
    v, CR = {}, {}
    for cr, (upper, _) in SUB_PAIRWISE.items():
        w, lam, ci, cr_ = AHPmat(pairwise(upper))
        v[cr], CR[cr] = w, cr_
    return v, CR


def main_weights(scenario="W1 Balanced"):
    w, lam, ci, cr_ = AHPmat(pairwise(WEIGHT_SCENARIOS[scenario]))
    return w, cr_


def global_scores(W, v, u):
    """Alternatives' global priorities for main weights u and sub weights v."""
    return sum(np.dot(W[cr], u[i] * v[cr]) for i, cr in enumerate(CRITERIA))


def ahp_scores(L, C, scenario="W1 Balanced"):
    W, _, _ = local_priorities(L, C)
    v, _ = sub_weights()
    u, _ = main_weights(scenario)
    return global_scores(W, v, u)


def renorm_wt(p, k, base_wt):
    """Lecture helper: set weight k to p and rescale the others proportionally."""
    new = base_wt.copy()
    bal = base_wt.sum() - base_wt[k]
    for i in range(len(base_wt)):
        if i != k:
            new[i] = (1 - p) * base_wt[i] / bal
    new[k] = p
    return new


def omit_leaves(v, omitted=()):
    """Remove proxy leaves and renormalise within each retained criterion."""
    result = {}
    for cr, leaves in SUB.items():
        weights = np.array(v[cr], dtype=float, copy=True)
        for j, leaf in enumerate(leaves):
            if leaf in omitted:
                weights[j] = 0.
        if weights.sum() <= 0:
            raise ValueError("Cannot remove every leaf of a criterion")
        result[cr] = weights / weights.sum()
    return result


PROXY_CASES = {
    "Full hierarchy": (),
    "No electricity overlap": ("C2b Electricity use",),
    "No discharge-volume proxy": ("C2c Marine discharge (brine, blowdown)",),
    "Reduced overlap": ("C2b Electricity use", "C2c Marine discharge (brine, blowdown)",
                        "C3b Weather resilience", "C3c Dependence on used-water feedstock",
                        "C4c Effect on other water users"),
}


def perturb_matrix(A, rng, sigma=0.35):
    """Lognormal perturbation of upper comparisons; reciprocals stay exact.

    Ratios are bounded by the usual 1/9 to 9 comparison range. This is a
    specified stress-test distribution, not an estimate of stakeholder belief.
    Callers reject matrices with CR above 0.10 and report rejection counts.
    """
    A = np.asarray(A, dtype=float)
    B = np.eye(len(A))
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            x = np.clip(A[i, j] * np.exp(rng.normal(0., sigma)), 1 / 9, 9)
            B[i, j], B[j, i] = x, 1 / x
    return B


def sample_preferences(rng, sigma=0.35, max_attempts=100):
    """Sample main/sub weights and qualitative judgments, keeping CR <= .10.

    Main weights span the simplex through Dirichlet(1,1,1,1), represented by
    a consistent ratio matrix. Other comparisons perturb the team's base
    matrices. Every attempted matrix and rejection is counted.
    """
    u = rng.dirichlet(np.ones(len(CRITERIA)))
    v, qualitative = {}, {}
    attempts = rejected = 0
    maximum_cr = 0.
    matrices = [("sub", cr, pairwise(spec[0])) for cr, spec in SUB_PAIRWISE.items()]
    matrices += [("qual", leaf, pairwise(spec[0])) for leaf, spec in QUAL_PAIRWISE.items()]
    for kind, name, A in matrices:
        for _ in range(max_attempts):
            attempts += 1
            B = perturb_matrix(A, rng, sigma)
            w, _, _, cr = AHPmat(B)
            if cr <= .10:
                maximum_cr = max(maximum_cr, cr)
                if kind == "sub":
                    v[name] = w
                else:
                    qualitative[name] = B
                break
            rejected += 1
        else:
            raise RuntimeError("Could not sample a consistent preference matrix")
    return u, v, qualitative, dict(matrix_attempts=attempts, matrices_rejected=rejected,
                                   maximum_accepted_cr=maximum_cr)
