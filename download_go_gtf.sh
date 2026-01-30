#!/usr/bin/env bash
set -euo pipefail

# download_and_convert_gtf_gene_only.sh
#
# Downloads:
#  - Full GTFs (GENCODE human GRCh38, mouse GRCm39)
#  - GO ontology + GAF annotations (human + mouse)
#
# Builds:
#  - go_bp_human.gmt, go_bp_mouse.gmt
#
# Converts (FULL -> MINIMAL gene-only):
#  - gencode.v49.primary_assembly.annotation.gtf.gz -> gencode.v49.gene_only.minimal.gtf
#  - gencode.vM38.primary_assembly.annotation.gtf.gz -> gencode.vM38.gene_only.minimal.gtf
#
# The minimal GTF format:
#  ##description: ...
#  ##provider: ...
#  ##format: gtf
#  chr...  pygreat  gene  ...  gene_id "..."; gene_name "...";

OUTDIR="${1:-refdata}"
mkdir -p "$OUTDIR"
cd "$OUTDIR"

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing dependency: $1" >&2; exit 1; }; }
need curl
need python3

download() {
  local url="$1"
  local out="$2"
  if [[ -s "$out" ]]; then
    echo "[skip] $out exists"
    return 0
  fi
  echo "[get ] $url"
  curl -L --fail --retry 3 --retry-delay 2 -o "$out" "$url"
}

echo "==> Downloading full GENCODE GTFs (primary assembly)"
HUMAN_GTF_GZ="gencode.v49.primary_assembly.annotation.gtf.gz"
MOUSE_GTF_GZ="gencode.vM38.primary_assembly.annotation.gtf.gz"

download "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_49/${HUMAN_GTF_GZ}" "${HUMAN_GTF_GZ}"
download "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M38/${MOUSE_GTF_GZ}" "${MOUSE_GTF_GZ}"

echo "==> Downloading GO ontology + annotations (GAF)"
download "https://purl.obolibrary.org/obo/go/go-basic.obo" "go-basic.obo"
download "https://current.geneontology.org/annotations/goa_human.gaf.gz" "goa_human.gaf.gz"
download "https://current.geneontology.org/annotations/mgi.gaf.gz" "mgi.gaf.gz"

echo "==> Building BP-only GMT files from GAF + OBO"
python3 - <<'PY'
import gzip
from collections import defaultdict

def parse_obo(path):
    go = {}
    cur = None
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if line == "[Term]":
                cur = {"id": None, "name": None, "namespace": None}
                continue
            if not cur:
                continue
            if line == "":
                if cur.get("id"):
                    go[cur["id"]] = (cur.get("name") or cur["id"], cur.get("namespace"))
                cur = None
                continue
            if line.startswith("id: "):
                cur["id"] = line.split("id: ", 1)[1].strip()
            elif line.startswith("name: "):
                cur["name"] = line.split("name: ", 1)[1].strip()
            elif line.startswith("namespace: "):
                cur["namespace"] = line.split("namespace: ", 1)[1].strip()
    if cur and cur.get("id"):
        go[cur["id"]] = (cur.get("name") or cur["id"], cur.get("namespace"))
    return go

def gaf_to_gmt_bp(gaf_gz, obo, out_gmt):
    go = parse_obo(obo)
    term_genes = defaultdict(set)

    with gzip.open(gaf_gz, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line or line.startswith("!"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 9:
                continue
            gene_symbol = cols[2].strip()   # DB Object Symbol
            go_id = cols[4].strip()        # GO ID
            aspect = cols[8].strip()       # P/F/C
            if aspect != "P":
                continue
            if gene_symbol and go_id:
                term_genes[go_id].add(gene_symbol)

    with open(out_gmt, "w", encoding="utf-8") as out:
        for go_id in sorted(term_genes.keys()):
            genes = sorted(term_genes[go_id])
            if len(genes) < 2:
                continue
            term_name, _ns = go.get(go_id, (go_id, None))
            name = f"{go_id}\t{term_name}"
            out.write(name + "\t".join(genes) + "\n")

gaf_to_gmt_bp("goa_human.gaf.gz", "go-basic.obo", "go_bp_human.gmt")
gaf_to_gmt_bp("mgi.gaf.gz", "go-basic.obo", "go_bp_mouse.gmt")

print("Wrote go_bp_human.gmt and go_bp_mouse.gmt")
PY

echo "==> Converting full GTFs -> gene-only minimal GTFs (gene_id + gene_name only)"

python3 - <<'PY'
import gzip
import re
from pathlib import Path

def get_attr(attrs: str, key: str):
    # GTF attributes are typically: key "value"; key2 "value2";
    m = re.search(rf'{re.escape(key)}\s+"([^"]+)"', attrs)
    return m.group(1) if m else None

def convert_gtf_gene_only_minimal(in_gz: str, out_path: str, description: str):
    in_gz = Path(in_gz)
    out_path = Path(out_path)

    with gzip.open(in_gz, "rt", encoding="utf-8", errors="replace") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        # Write minimal header block (your format)
        fout.write(f"##description: {description}\n")
        fout.write("##provider: pygreat\n")
        fout.write("##format: gtf\n")

        for line in fin:
            if not line or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) != 9:
                continue
            seqname, source, feature, start, end, score, strand, frame, attrs = cols

            # gene-level only
            if feature != "gene":
                continue

            gene_id = get_attr(attrs, "gene_id")
            gene_name = get_attr(attrs, "gene_name") or get_attr(attrs, "gene")  # occasional alt key fallback

            if not gene_id:
                continue
            if not gene_name:
                # keep it deterministic if gene_name missing
                gene_name = gene_id

            # output: use "pygreat" as source, keep coordinates/strand, drop other attrs
            minimal_attrs = f'gene_id "{gene_id}"; gene_name "{gene_name}";'
            fout.write("\t".join([
                seqname, "pygreat", "gene", start, end, score, strand, frame, minimal_attrs
            ]) + "\n")

def main():
    convert_gtf_gene_only_minimal(
        in_gz="gencode.v49.primary_assembly.annotation.gtf.gz",
        out_path="gencode.v49.gene_only.minimal.gtf",
        description="GENCODE GRCh38 gene-only minimal GTF for pygreat local analysis"
    )
    convert_gtf_gene_only_minimal(
        in_gz="gencode.vM38.primary_assembly.annotation.gtf.gz",
        out_path="gencode.vM38.gene_only.minimal.gtf",
        description="GENCODE GRCm39 gene-only minimal GTF for pygreat local analysis"
    )

if __name__ == "__main__":
    main()
PY

echo "==> Done."
echo "Outputs in: $(pwd)"
echo ""
echo "Gene-only minimal GTFs:"
echo " - gencode.v49.gene_only.minimal.gtf"
echo " - gencode.vM38.gene_only.minimal.gtf"
echo ""
echo "GO BP GMTs:"
echo " - go_bp_human.gmt"
echo " - go_bp_mouse.gmt"
