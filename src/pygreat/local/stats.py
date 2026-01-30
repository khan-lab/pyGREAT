"""Statistical tests for GREAT analysis.

Implements the binomial and hypergeometric tests used by GREAT
for enrichment analysis.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import stats


def binomial_test(
    observed_regions: int,
    total_regions: int,
    genome_fraction: float,
) -> tuple[float, float]:
    """Perform binomial test for region enrichment.

    Tests whether the observed number of regions associated with a gene set
    is significantly higher than expected by chance.

    Args:
        observed_regions: Number of input regions associated with gene set.
        total_regions: Total number of input regions.
        genome_fraction: Fraction of genome covered by regulatory domains
            of genes in the gene set.

    Returns:
        Tuple of (p-value, fold_enrichment).
    """
    if total_regions == 0 or genome_fraction == 0:
        return 1.0, 0.0

    # Expected regions under null
    expected = total_regions * genome_fraction

    # Fold enrichment
    fold_enrichment = observed_regions / expected if expected > 0 else 0.0

    # One-sided binomial test (greater)
    # P(X >= observed) where X ~ Binom(n, p)
    p_value = stats.binom.sf(observed_regions - 1, total_regions, genome_fraction)

    return float(p_value), float(fold_enrichment)


def hypergeometric_test(
    observed_genes: int,
    total_genes_in_regions: int,
    genes_in_term: int,
    total_genes_in_genome: int,
) -> tuple[float, float]:
    """Perform hypergeometric test for gene enrichment.

    Tests whether genes associated with input regions are enriched
    for a particular gene set.

    Args:
        observed_genes: Number of genes in both input regions AND gene set.
        total_genes_in_regions: Total genes associated with input regions.
        genes_in_term: Total genes in the gene set/term.
        total_genes_in_genome: Total genes in the genome.

    Returns:
        Tuple of (p-value, fold_enrichment).
    """
    if (
        total_genes_in_regions == 0
        or genes_in_term == 0
        or total_genes_in_genome == 0
    ):
        return 1.0, 0.0

    # Expected genes under null
    expected = (total_genes_in_regions * genes_in_term) / total_genes_in_genome

    # Fold enrichment
    fold_enrichment = observed_genes / expected if expected > 0 else 0.0

    # Hypergeometric test (Fisher's exact test one-sided)
    # hypergeom.sf(k-1, M, n, N) = P(X >= k)
    # M = total population (total genes in genome)
    # n = success states in population (genes in term)
    # N = number of draws (genes in regions)
    # k = observed successes (genes in both)
    p_value = stats.hypergeom.sf(
        observed_genes - 1,
        total_genes_in_genome,
        genes_in_term,
        total_genes_in_regions,
    )

    return float(p_value), float(fold_enrichment)


def correct_pvalues(
    pvalues: NDArray[Any],
    method: str = "fdr_bh",
) -> NDArray[Any]:
    """Apply multiple testing correction to p-values.

    Args:
        pvalues: Array of p-values.
        method: Correction method:
            - 'fdr_bh': Benjamini-Hochberg FDR (default)
            - 'bonferroni': Bonferroni correction
            - 'fdr_by': Benjamini-Yekutieli FDR

    Returns:
        Array of corrected p-values (same shape as input).
    """
    from scipy.stats import false_discovery_control

    pvalues = np.asarray(pvalues)

    if len(pvalues) == 0:
        return pvalues

    # Handle NaN values
    valid_mask = ~np.isnan(pvalues)
    if not valid_mask.any():
        return pvalues

    if method == "bonferroni":
        corrected = np.minimum(pvalues * len(pvalues), 1.0)
    elif method in ("fdr_bh", "fdr_by"):
        # Use scipy's false_discovery_control for BH/BY
        corrected = np.ones_like(pvalues)
        if valid_mask.any():
            try:
                corrected[valid_mask] = false_discovery_control(
                    pvalues[valid_mask], method=method.replace("fdr_", "")
                )
            except Exception:
                # Fallback to manual BH if scipy version doesn't support
                corrected = _benjamini_hochberg(pvalues)
    else:
        raise ValueError(f"Unknown correction method: {method}")

    return np.asarray(corrected)


def _benjamini_hochberg(pvalues: NDArray[Any]) -> NDArray[Any]:
    """Manual Benjamini-Hochberg FDR correction.

    Args:
        pvalues: Array of p-values.

    Returns:
        Array of FDR-corrected q-values.
    """
    pvalues = np.asarray(pvalues)
    n = len(pvalues)

    if n == 0:
        return pvalues

    # Sort p-values
    sorted_idx = np.argsort(pvalues)
    sorted_pvals = pvalues[sorted_idx]

    # Calculate adjusted p-values
    adjusted = np.zeros(n)
    adjusted[sorted_idx] = np.minimum(
        sorted_pvals * n / (np.arange(n) + 1), 1.0
    )

    # Ensure monotonicity (cumulative minimum from end)
    for i in range(n - 2, -1, -1):
        adjusted[sorted_idx[i]] = min(
            adjusted[sorted_idx[i]], adjusted[sorted_idx[i + 1]]
        )

    return adjusted
