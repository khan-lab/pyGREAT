"""Parser for GREAT server responses."""

from __future__ import annotations

import json
import re
from io import StringIO
from typing import Any

import pandas as pd

from pygreat.core.config import BATCH_COLUMN_MAP
from pygreat.core.exceptions import ParsingError


class BatchResponseParser:
    """Parse batch TSV responses from GREAT server.

    This parser handles the TSV format returned by the GREAT batch API
    when using outputType=batch.

    The batch format consists of:
    - Line 1: Script tag with metadata (version, species, association rule)
    - Lines 2-3: Comment lines
    - Line 4: Column headers (prefixed with #)
    - Data rows: Tab-separated values with ontology as first column
    - Footer: Ontology summary stats (lines starting with #)
    """

    # Regex patterns for extracting metadata from first line
    VERSION_PATTERN = re.compile(r"GREAT version\s+([\d.]+)")
    SPECIES_PATTERN = re.compile(r"Species assembly:\s+(\w+)")
    RULE_PATTERN = re.compile(r"Association rule:\s+([^,\n]+)")

    def parse(self, tsv_content: str) -> dict[str, pd.DataFrame]:
        """Parse batch TSV output into DataFrames grouped by ontology.

        Args:
            tsv_content: Raw TSV content from GREAT batch API.

        Returns:
            Dictionary mapping ontology names to enrichment DataFrames.

        Raises:
            ParsingError: If content cannot be parsed.
        """
        if not tsv_content or not tsv_content.strip():
            return {}

        lines = tsv_content.strip().split("\n")
        if len(lines) < 5:
            return {}

        # Parse header line (line 4, index 3) - strip leading "# "
        header_line = lines[3]
        if header_line.startswith("# "):
            header_line = header_line[2:]
        elif header_line.startswith("#"):
            header_line = header_line[1:]

        columns = header_line.split("\t")

        # Parse data rows (skip header rows and footer)
        data_rows = []
        for line in lines[4:]:
            # Skip empty lines and footer comments
            if not line.strip() or line.startswith("#"):
                continue
            data_rows.append(line.split("\t"))

        if not data_rows:
            return {}

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)

        # Rename columns using batch column map
        df = df.rename(columns=BATCH_COLUMN_MAP)

        # Convert numeric columns
        numeric_cols = [
            "binom_rank", "binom_p", "binom_bonferroni", "binom_fdr",
            "binom_fold_enrichment", "expected_regions", "observed_regions",
            "genome_fraction", "region_coverage",
            "hyper_rank", "hyper_p", "hyper_bonferroni", "hyper_fdr",
            "hyper_fold_enrichment", "expected_genes", "observed_genes",
            "total_genes", "gene_coverage", "term_coverage",
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert integer columns
        int_cols = [
            "binom_rank", "hyper_rank", "observed_regions", "observed_genes",
            "total_genes",
        ]
        for col in int_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0).astype(int)

        # Group by ontology
        results: dict[str, pd.DataFrame] = {}
        if "ontology" in df.columns:
            for ontology, group in df.groupby("ontology", sort=False):
                # Remove ontology column from individual DataFrames
                ont_df = group.drop(columns=["ontology"]).reset_index(drop=True)
                results[str(ontology)] = ont_df
        else:
            # Single ontology or no ontology column
            results["Unknown"] = df

        return results

    def parse_metadata(self, tsv_content: str) -> dict[str, str]:
        """Extract metadata from batch response.

        Args:
            tsv_content: Raw TSV content from GREAT batch API.

        Returns:
            Dictionary with version, species, and rule.
        """
        metadata = {
            "version": "",
            "species": "",
            "rule": "",
        }

        if not tsv_content:
            return metadata

        first_line = tsv_content.split("\n")[0] if tsv_content else ""

        version_match = self.VERSION_PATTERN.search(first_line)
        if version_match:
            metadata["version"] = version_match.group(1)

        species_match = self.SPECIES_PATTERN.search(first_line)
        if species_match:
            metadata["species"] = species_match.group(1)

        rule_match = self.RULE_PATTERN.search(first_line)
        if rule_match:
            metadata["rule"] = rule_match.group(1).strip()

        return metadata

    def parse_ontology_stats(self, tsv_content: str) -> dict[str, dict[str, Any]]:
        """Extract ontology summary statistics from footer.

        Args:
            tsv_content: Raw TSV content from GREAT batch API.

        Returns:
            Dictionary mapping ontology names to stats (terms tested, min/max count).
        """
        stats: dict[str, dict[str, Any]] = {}

        if not tsv_content:
            return stats

        # Find footer section (lines starting with # after data)
        in_footer = False
        for line in tsv_content.split("\n"):
            if line.startswith("# Ontology\tTermsTested"):
                in_footer = True
                continue
            if in_footer and line.startswith("# ") and "\t" in line:
                parts = line[2:].split("\t")
                if len(parts) >= 3:
                    ontology = parts[0].strip()
                    stats[ontology] = {
                        "terms_tested": int(parts[1]) if parts[1].isdigit() else 0,
                        "min_annot_count": parts[2] if len(parts) > 2 else "1",
                        "max_annot_count": parts[3] if len(parts) > 3 else "Inf",
                    }

        return stats


class ResponseParser:
    """Parse HTML and JavaScript responses from GREAT server.

    This parser handles the specific response formats returned by GREAT,
    including HTML pages with embedded JavaScript data and TSV files.
    """

    # Regex patterns based on rGREAT implementation
    SESSION_PATTERN = re.compile(r'var\s+_sessionName\s*=\s*["\']([^"\']+)["\']')
    SPECIES_PATTERN = re.compile(r'var\s+_species\s*=\s*["\']([^"\']+)["\']')
    ERROR_PATTERN = re.compile(
        r"encountered a user error|"
        r"<strong>Warning:</strong>|"
        r"Error:|"
        r"Invalid input"
    )

    # Ontology extraction patterns
    ONTOLOGY_CATEGORY_PATTERN = re.compile(
        r'<div[^>]*class="[^"]*ontologyCategoryHeader[^"]*"[^>]*>([^<]+)</div>',
        re.IGNORECASE,
    )
    ONTOLOGY_NAME_PATTERN = re.compile(
        r'<a[^>]*class="[^"]*ontologyName[^"]*"[^>]*>([^<]+)</a>', re.IGNORECASE
    )
    ONTOLOGY_DATA_PATTERN = re.compile(
        r'data-ontology=["\']([^"\']+)["\']', re.IGNORECASE
    )

    def parse_submit_response(self, html: str) -> dict[str, Any]:
        """Parse job submission response.

        Args:
            html: HTML response from greatWeb.php.

        Returns:
            Dictionary with:
            - session_id: GREAT session identifier
            - ontologies: Dict mapping category to list of ontology names
            - species: Genome assembly

        Raises:
            ParsingError: If response cannot be parsed or contains errors.
        """
        # Check for errors
        if self.ERROR_PATTERN.search(html):
            error_msg = self._extract_error_message(html)
            raise ParsingError(f"GREAT server error: {error_msg}")

        # Extract session ID
        session_match = self.SESSION_PATTERN.search(html)
        if not session_match:
            # Try alternative patterns
            alt_patterns = [
                r'sessionName["\']?\s*:\s*["\']([^"\']+)["\']',
                r'session["\']?\s*=\s*["\']([^"\']+)["\']',
                r'/tmp/results/([^/]+)\.d/',
            ]
            for pattern in alt_patterns:
                match = re.search(pattern, html)
                if match:
                    session_match = match
                    break

        if not session_match:
            raise ParsingError("Could not extract session ID from response")

        session_id = session_match.group(1)

        # Extract species
        species = ""
        species_match = self.SPECIES_PATTERN.search(html)
        if species_match:
            species = species_match.group(1)

        # Extract available ontologies
        ontologies = self._parse_ontologies(html)

        return {
            "session_id": session_id,
            "ontologies": ontologies,
            "species": species,
        }

    def parse_enrichment_js(self, js_content: str) -> pd.DataFrame:
        """Parse JavaScript enrichment results.

        GREAT returns enrichment data as JavaScript arrays/objects.
        This method extracts and converts to DataFrame.

        Args:
            js_content: JavaScript data from readJsFromFile.php.

        Returns:
            DataFrame with enrichment results.

        Raises:
            ParsingError: If data cannot be parsed.
        """
        # GREAT returns JS like: var enrichmentData = [...];
        # Try multiple patterns to extract JSON array
        patterns = [
            r"var\s+\w+\s*=\s*(\[[\s\S]*?\]);",
            r"=\s*(\[[\s\S]*?\]);",
            r"(\[[\s\S]*\])",
        ]

        data = None
        for pattern in patterns:
            match = re.search(pattern, js_content)
            if match:
                try:
                    data = json.loads(match.group(1))
                    break
                except json.JSONDecodeError:
                    continue

        # Try direct JSON parsing if patterns fail
        if data is None:
            try:
                data = json.loads(js_content)
            except json.JSONDecodeError as e:
                raise ParsingError(f"Could not parse enrichment data: {e}") from e

        if not data:
            return pd.DataFrame()

        # Convert to DataFrame with standardized column names
        df = pd.DataFrame(data)

        # Rename columns to standard names
        column_map = {
            "ID": "term_id",
            "id": "term_id",
            "name": "term_name",
            "Name": "term_name",
            "Desc": "term_name",
            "description": "term_name",
            "Binom_Raw_PValue": "binom_p",
            "Binom_Bonferroni_PValue": "binom_bonferroni",
            "Binom_FDR_Q_Val": "binom_fdr",
            "Binom_Fold_Enrichment": "binom_fold_enrichment",
            "Hyper_Raw_PValue": "hyper_p",
            "Hyper_Bonferroni_PValue": "hyper_bonferroni",
            "Hyper_FDR_Q_Val": "hyper_fdr",
            "Hyper_Fold_Enrichment": "hyper_fold_enrichment",
            "Binom_Observed_Region_Hits": "observed_regions",
            "Binom_Region_Set_Coverage": "region_coverage",
            "Hyper_Observed_Gene_Hits": "observed_genes",
            "Hyper_Total_Genes": "total_genes",
            "Hyper_Gene_Set_Coverage": "gene_coverage",
            # Alternative column names
            "BinomP": "binom_p",
            "BinomBonfP": "binom_bonferroni",
            "BinomFdrQ": "binom_fdr",
            "BinomFold": "binom_fold_enrichment",
            "HyperP": "hyper_p",
            "HyperBonfP": "hyper_bonferroni",
            "HyperFdrQ": "hyper_fdr",
            "HyperFold": "hyper_fold_enrichment",
            "ObsRegions": "observed_regions",
            "RegionCov": "region_coverage",
            "ObsGenes": "observed_genes",
            "TotalGenes": "total_genes",
            "GeneCov": "gene_coverage",
        }

        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

        # Ensure required columns exist with defaults
        required_columns = {
            "term_id": "",
            "term_name": "",
            "binom_p": 1.0,
            "binom_fdr": 1.0,
            "binom_fold_enrichment": 0.0,
            "hyper_p": 1.0,
            "hyper_fdr": 1.0,
            "hyper_fold_enrichment": 0.0,
            "observed_genes": 0,
            "total_genes": 0,
            "observed_regions": 0,
        }

        for col, default in required_columns.items():
            if col not in df.columns:
                df[col] = default  # type: ignore[call-overload]

        return df

    def parse_associations(self, tsv_content: str) -> pd.DataFrame:
        """Parse region-gene association TSV.

        Args:
            tsv_content: TSV content from downloadAssociations.php.

        Returns:
            DataFrame with region-gene associations.
        """
        # Skip comment lines
        lines = []
        for line in tsv_content.split("\n"):
            if not line.startswith("#") and line.strip():
                lines.append(line)

        if not lines:
            return pd.DataFrame()

        content = "\n".join(lines)
        return pd.read_csv(StringIO(content), sep="\t")

    def _parse_ontologies(self, html: str) -> dict[str, list[str]]:
        """Extract ontology categories and names from HTML.

        Args:
            html: HTML response content.

        Returns:
            Dictionary mapping category names to ontology lists.
        """
        ontologies: dict[str, list[str]] = {}
        current_category = "Gene Ontology"

        # Try to extract from structured data
        # Look for ontology select options or links
        ontology_patterns = [
            r'<option[^>]*value="([^"]+)"[^>]*>([^<]+)</option>',
            r'data-ontology="([^"]+)"[^>]*>([^<]+)<',
            r'ontology["\']?\s*:\s*["\']([^"\']+)["\']',
        ]

        found_any = False
        for pattern in ontology_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                found_any = True
                if isinstance(match, tuple) and len(match) >= 2:
                    ontology_id, ontology_name = match[0], match[1]
                else:
                    ontology_name = match
                    ontology_id = match

                # Categorize ontologies
                if "GO" in ontology_name or "Gene Ontology" in ontology_name:
                    category = "Gene Ontology"
                elif "Pathway" in ontology_name or "KEGG" in ontology_name:
                    category = "Pathway Data"
                elif "Disease" in ontology_name or "Phenotype" in ontology_name:
                    category = "Disease Ontology"
                else:
                    category = "Other"

                if category not in ontologies:
                    ontologies[category] = []
                if ontology_name not in ontologies[category]:
                    ontologies[category].append(ontology_name)

        # If no ontologies found, return defaults
        if not found_any:
            ontologies = {
                "Gene Ontology": [
                    "GO Molecular Function",
                    "GO Biological Process",
                    "GO Cellular Component",
                ],
            }

        return ontologies

    def _extract_error_message(self, html: str) -> str:
        """Extract error message from HTML.

        Args:
            html: HTML content with error.

        Returns:
            Extracted error message or generic message.
        """
        # Look for error text in common patterns
        patterns = [
            r'<div[^>]*class="[^"]*error[^"]*"[^>]*>(.*?)</div>',
            r"<strong>Warning:</strong>\s*(.*?)<",
            r"Error:\s*(.*?)<",
            r"encountered a user error:\s*(.*?)<",
            r'class="errorMsg"[^>]*>(.*?)<',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                # Clean up HTML tags from message
                msg = re.sub(r"<[^>]+>", "", match.group(1))
                return msg.strip()
        return "Unknown error"
