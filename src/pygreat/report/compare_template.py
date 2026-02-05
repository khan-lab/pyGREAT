"""HTML template for GREAT comparison report.

Contains the complete HTML template with embedded CSS and JavaScript
for generating self-contained multi-run comparison reports.
"""

from __future__ import annotations

# Custom CSS for compare mode
COMPARE_CSS = """
:root {
    --primary-color: #2563eb;
    --primary-hover: #1d4ed8;
    --success-color: #16a34a;
    --warning-color: #d97706;
    --danger-color: #dc2626;
    --bg-light: #f8fafc;
    --bg-white: #ffffff;
    --border-color: #e2e8f0;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-muted: #94a3b8;
}

body {
    background: var(--bg-light);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Helvetica Neue", Arial, sans-serif;
}

/* Header */
.report-header {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    color: white;
    padding: 1.5rem 0;
    margin-bottom: 1.5rem;
}

.report-header h1 {
    margin: 0 0 0.25rem 0;
    font-size: 1.75rem;
    font-weight: 700;
}

.report-header .subtitle {
    opacity: 0.9;
    font-size: 0.95rem;
}

/* Main Tab Navigation */
.main-tabs {
    margin-bottom: 1.5rem;
    border-bottom: 2px solid var(--border-color);
}

.main-tabs .nav-link {
    font-weight: 600;
    padding: 0.75rem 1.5rem;
    color: var(--text-secondary);
    border: none;
    border-radius: 0.5rem 0.5rem 0 0;
    margin-right: 0.25rem;
    transition: all 0.2s;
}

.main-tabs .nav-link:hover {
    background: #f1f5f9;
    color: var(--text-primary);
}

.main-tabs .nav-link.active {
    background: var(--primary-color);
    color: white;
}

/* Tab Panes */
.main-tab-pane {
    display: none;
}

.main-tab-pane.show.active {
    display: block;
}

/* Comparison Controls */
.compare-controls {
    background: var(--bg-white);
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}

.compare-controls .filter-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.compare-controls label {
    font-weight: 500;
    font-size: 0.875rem;
    color: var(--text-secondary);
    white-space: nowrap;
}

.compare-controls .form-control,
.compare-controls .form-select {
    min-width: 120px;
    font-size: 0.875rem;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.summary-card {
    background: var(--bg-white);
    border-radius: 0.5rem;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
    border-left: 4px solid var(--primary-color);
}

.summary-card.shared { border-left-color: var(--success-color); }
.summary-card.any { border-left-color: var(--warning-color); }
.summary-card.unique { border-left-color: #8b5cf6; }

.summary-card .count {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}

.summary-card .label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

/* Cards */
.card {
    background: var(--bg-white);
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: none;
    margin-bottom: 1.5rem;
}

.card-header {
    background: #f8fafc;
    border-bottom: 1px solid var(--border-color);
    padding: 0.875rem 1.25rem;
    font-weight: 600;
}

.card-body {
    padding: 1.25rem;
}

/* Tabulator Overrides */
.tabulator {
    border: 1px solid var(--border-color);
    border-radius: 0.375rem;
    font-size: 0.875rem;
}

.tabulator-header {
    background: #f8fafc;
    border-bottom: 2px solid var(--border-color);
}

.tabulator-col {
    background: transparent;
    border-right: 1px solid var(--border-color);
}

.tabulator-col-title {
    font-weight: 600;
    color: var(--text-primary);
}

.tabulator-row {
    border-bottom: 1px solid #f1f5f9;
}

.tabulator-row:hover {
    background: #f8fafc;
}

.tabulator-row.tabulator-selected {
    background: #dbeafe;
}

.tabulator-cell {
    border-right: 1px solid #f1f5f9;
}

/* Presence Indicator */
.presence-indicator {
    display: inline-flex;
    gap: 3px;
    align-items: center;
}

.presence-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: 1px solid #d1d5db;
}

.presence-dot.present {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.presence-dot.absent {
    background-color: #f1f5f9;
}

/* Plot Containers */
.plot-container {
    min-height: 400px;
    border: 1px dashed var(--border-color);
    border-radius: 0.375rem;
    background: var(--bg-white);
}

/* Selection Info */
.selection-info {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: #dbeafe;
    border-radius: 0.375rem;
    margin-bottom: 1rem;
}

.selection-info .count {
    font-weight: 600;
    color: var(--primary-color);
}

/* Export Buttons */
.export-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.export-buttons .btn {
    font-size: 0.8rem;
    padding: 0.375rem 0.75rem;
}

/* Footer */
.report-footer {
    text-align: center;
    padding: 2rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.report-footer a {
    color: var(--primary-color);
    text-decoration: none;
}

/* Run tabs in individual run panes */
.run-pane-content {
    background: var(--bg-white);
    border-radius: 0.5rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Plot Settings Grid */
.plot-settings {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.75rem;
    margin-bottom: 1rem;
}

.plot-settings .form-group label {
    display: block;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-secondary);
    margin-bottom: 0.25rem;
}

/* Run Pane Accordion */
.run-accordion .accordion-item {
    border: 1px solid var(--border-color);
    margin-bottom: 0.5rem;
    border-radius: 0.375rem;
    overflow: hidden;
}

.run-accordion .accordion-button {
    font-weight: 600;
    padding: 0.75rem 1rem;
    background: #f8fafc;
}

.run-accordion .accordion-button:not(.collapsed) {
    background: #eff6ff;
    color: var(--primary-color);
}

.run-accordion .accordion-button:focus {
    box-shadow: none;
    border-color: var(--border-color);
}

.run-accordion .category-badge {
    background: var(--primary-color);
    color: white;
    font-size: 0.75rem;
    padding: 0.15rem 0.5rem;
    border-radius: 1rem;
}

/* Term link in tables */
.term-link {
    color: var(--primary-color);
    text-decoration: none;
    cursor: pointer;
}

.term-link:hover {
    text-decoration: underline;
}

/* Term Detail Modal */
.term-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}

.term-stat-item {
    background: #f8fafc;
    padding: 0.75rem;
    border-radius: 0.375rem;
}

.term-stat-item .stat-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.term-stat-item .stat-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
}

/* Genes section in modal */
.genes-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
    max-height: 200px;
    overflow-y: auto;
    padding: 0.5rem;
    background: #f8fafc;
    border-radius: 0.375rem;
}

.gene-badge {
    background: #e2e8f0;
    padding: 0.15rem 0.5rem;
    border-radius: 0.25rem;
    font-family: monospace;
    font-size: 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
    .compare-controls {
        flex-direction: column;
        align-items: stretch;
    }

    .summary-cards {
        grid-template-columns: repeat(2, 1fr);
    }

    .main-tabs .nav-link {
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
    }
}
"""

# Custom JavaScript for compare mode
COMPARE_JS = """
// === State Management ===
const state = {
    runs: {},              // Per-run data
    merged: {},            // Merged comparison data
    runLabels: [],         // Ordered labels
    categories: [],        // All categories
    selectedTerms: new Set(),
    currentTab: 'compare',
    filters: {
        fdr: 0.05,
        metric: 'fdr',
        category: 'all',
        search: '',
    },
    tables: {},            // Tabulator instances
    plots: {},             // Plotly references
};

// === Initialization ===
document.addEventListener('DOMContentLoaded', function() {
    // Load data from embedded JSON
    state.runs = DATA.runs;
    state.merged = DATA.merged;
    state.runLabels = DATA.runLabels;
    state.categories = DATA.categories;

    initMainTabs();
    initCompareView();
    initRunTabs();
});

// === Main Tab Navigation ===
function initMainTabs() {
    document.querySelectorAll('#mainTabs .nav-link').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            const tabId = this.dataset.tab;
            switchMainTab(tabId);
        });
    });
}

function switchMainTab(tabId) {
    state.currentTab = tabId;

    // Update tab active states
    document.querySelectorAll('#mainTabs .nav-link').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tabId);
    });

    // Show/hide content panes
    document.querySelectorAll('.main-tab-pane').forEach(pane => {
        const isActive = pane.id === 'pane-' + tabId;
        pane.classList.toggle('show', isActive);
        pane.classList.toggle('active', isActive);
    });

    // Refresh/init content when switching
    if (tabId === 'compare') {
        refreshComparePlots();
    } else if (tabId.startsWith('run-')) {
        // Lazy init run pane
        const safeId = tabId.substring(4);
        const label = state.runLabels.find(l => makeSafeId(l) === safeId);
        if (label) initRunPane(label);
    }
}

// === Compare View ===
function initCompareView() {
    initCompareControls();
    initCompareTable();
    initSummaryCards();
    initComparePlots();
}

function initCompareControls() {
    const fdrSelect = document.getElementById('compareFdr');
    const metricSelect = document.getElementById('compareMetric');
    const categorySelect = document.getElementById('compareCategory');
    const searchInput = document.getElementById('compareSearch');

    if (fdrSelect) {
        fdrSelect.addEventListener('change', (e) => {
            state.filters.fdr = parseFloat(e.target.value);
            applyCompareFilters();
        });
    }

    if (metricSelect) {
        metricSelect.addEventListener('change', (e) => {
            state.filters.metric = e.target.value;
            refreshCompareTable();
            refreshComparePlots();
        });
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', (e) => {
            state.filters.category = e.target.value;
            applyCompareFilters();
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            state.filters.search = e.target.value.toLowerCase();
            applyCompareFilters();
        }, 300));
    }
}

function initCompareTable() {
    const tableEl = document.getElementById('compareTable');
    if (!tableEl || !state.merged.terms) return;

    // Build columns dynamically
    const columns = [
        {
            formatter: "rowSelection",
            titleFormatter: "rowSelection",
            hozAlign: "center",
            headerSort: false,
            width: 40,
            cellClick: function(e, cell) {
                cell.getRow().toggleSelect();
            }
        },
        {
            title: "Term Name",
            field: "termName",
            sorter: "string",
            minWidth: 200,
            formatter: function(cell) {
                const data = cell.getRow().getData();
                const termId = data.termId;
                if (termId && termId.startsWith('GO:')) {
                    return `<a href="https://amigo.geneontology.org/amigo/term/${termId}"
                              target="_blank" class="term-link">${cell.getValue()}</a>`;
                }
                return cell.getValue();
            }
        },
        {
            title: "GO ID",
            field: "termId",
            sorter: "string",
            width: 100,
        },
        {
            title: "Category",
            field: "category",
            sorter: "string",
            width: 140,
        },
    ];

    // Add per-run columns
    state.runLabels.forEach(label => {
        columns.push({
            title: label + " FDR",
            field: "stats." + label + ".fdr",
            sorter: "number",
            width: 100,
            formatter: formatScientific,
            sorterParams: { alignEmptyValues: "bottom" },
        });
        columns.push({
            title: label + " Fold",
            field: "stats." + label + ".fold",
            sorter: "number",
            width: 80,
            formatter: formatDecimal,
            sorterParams: { alignEmptyValues: "bottom" },
        });
    });

    // Add derived columns
    columns.push({
        title: "Present In",
        field: "presence",
        sorter: function(a, b) {
            return (a?.length || 0) - (b?.length || 0);
        },
        width: 100,
        formatter: presenceFormatter,
    });
    columns.push({
        title: "Max -log₁₀",
        field: "maxNegLog",
        sorter: "number",
        width: 100,
        formatter: formatDecimal,
    });
    columns.push({
        title: "Range",
        field: "range",
        sorter: "number",
        width: 80,
        formatter: formatDecimal,
    });

    // Initialize Tabulator
    state.tables.compare = new Tabulator(tableEl, {
        data: state.merged.terms,
        columns: columns,
        layout: "fitDataFill",
        height: "500px",
        pagination: "local",
        paginationSize: 50,
        paginationSizeSelector: [25, 50, 100, 200],
        initialSort: [{ column: "maxNegLog", dir: "desc" }],
        selectable: true,
        selectableRangeMode: "click",
        rowSelected: function(row) {
            const termId = row.getData().termId;
            state.selectedTerms.add(termId);
            updateSelectionInfo();
        },
        rowDeselected: function(row) {
            const termId = row.getData().termId;
            state.selectedTerms.delete(termId);
            updateSelectionInfo();
        },
    });
}

function applyCompareFilters() {
    if (!state.tables.compare) return;

    state.tables.compare.setFilter(function(data) {
        // Category filter
        if (state.filters.category !== 'all' && data.category !== state.filters.category) {
            return false;
        }

        // Search filter
        if (state.filters.search) {
            const searchLower = state.filters.search;
            const nameMatch = data.termName?.toLowerCase().includes(searchLower);
            const idMatch = data.termId?.toLowerCase().includes(searchLower);
            if (!nameMatch && !idMatch) return false;
        }

        // FDR filter - keep if ANY run passes threshold
        const fdrThreshold = state.filters.fdr;
        let passesFdr = false;
        for (const label of state.runLabels) {
            const stats = data.stats?.[label];
            if (stats && stats.fdr <= fdrThreshold) {
                passesFdr = true;
                break;
            }
        }
        if (!passesFdr && fdrThreshold < 1) return false;

        return true;
    });

    updateSummaryCardCounts();
    refreshComparePlots();
    if (state.runLabels.length >= 3) {
        createUpsetPlot();
    }
}

function refreshCompareTable() {
    if (!state.tables.compare) return;
    state.tables.compare.redraw(true);
}

// === Summary Cards ===
function initSummaryCards() {
    updateSummaryCardCounts();
}

function updateSummaryCardCounts() {
    const sharedEl = document.getElementById('sharedCount');
    const anyEl = document.getElementById('anyCount');
    const totalEl = document.getElementById('totalCount');

    // Count based on current filter
    const fdrThreshold = state.filters.fdr;
    let shared = 0, any = 0, total = 0;

    state.merged.terms.forEach(term => {
        // Apply category filter
        if (state.filters.category !== 'all' && term.category !== state.filters.category) {
            return;
        }

        total++;

        const sigRuns = state.runLabels.filter(label => {
            const stats = term.stats?.[label];
            return stats && stats.fdr < fdrThreshold;
        });

        if (sigRuns.length === state.runLabels.length) shared++;
        if (sigRuns.length > 0) any++;
    });

    if (sharedEl) sharedEl.textContent = shared;
    if (anyEl) anyEl.textContent = any;
    if (totalEl) totalEl.textContent = total;

    // Update per-run unique counts
    state.runLabels.forEach(label => {
        const el = document.getElementById('unique-' + makeSafeId(label));
        if (el) {
            const uniqueCount = state.merged.terms.filter(term => {
                if (state.filters.category !== 'all' && term.category !== state.filters.category) {
                    return false;
                }
                const sigRuns = state.runLabels.filter(l => {
                    const stats = term.stats?.[l];
                    return stats && stats.fdr < fdrThreshold;
                });
                return sigRuns.length === 1 && sigRuns[0] === label;
            }).length;
            el.textContent = uniqueCount;
        }
    });
}

// === Compare Plots ===
function initComparePlots() {
    createMultiRunDotPlot();
    createTrendPlot();
    createHeatmap();
    if (state.runLabels.length >= 3) {
        createUpsetPlot();
    }
}

function refreshComparePlots() {
    createMultiRunDotPlot();
    createTrendPlot();
    createHeatmap();
}

function createMultiRunDotPlot() {
    const container = document.getElementById('multiRunDotPlot');
    if (!container) return;

    // Get top N terms by max -log10 value
    const topTerms = getTopTermsForPlot(20);

    // Create traces - one per run
    const traces = state.runLabels.map((label, i) => {
        const y = [];
        const x = [];
        const sizes = [];
        const text = [];

        topTerms.forEach(term => {
            const stats = term.stats[label];
            if (stats && stats.fdr < 1) {
                y.push(truncate(term.termName, 40));
                x.push(-Math.log10(Math.max(stats.fdr, 1e-300)));
                sizes.push(Math.sqrt(stats.observed_genes || 10) * 4 + 5);
                text.push(`${label}<br>FDR: ${formatSci(stats.fdr)}<br>Fold: ${stats.fold?.toFixed(2)}`);
            }
        });

        return {
            type: 'scatter',
            mode: 'markers',
            name: label,
            y: y,
            x: x,
            marker: { size: sizes, opacity: 0.7 },
            text: text,
            hovertemplate: '%{text}<extra></extra>',
        };
    });

    const layout = {
        title: { text: 'Multi-Run Dot Plot', font: { size: 14 } },
        xaxis: { title: '-log₁₀(FDR)', zeroline: false },
        yaxis: { automargin: true, tickfont: { size: 10 } },
        hovermode: 'closest',
        legend: { orientation: 'h', y: -0.15 },
        margin: { l: 200, r: 20, t: 40, b: 60 },
        height: 400,
    };

    Plotly.newPlot(container, traces, layout, { responsive: true });
    state.plots.dotPlot = container;
}

function createTrendPlot() {
    const container = document.getElementById('trendPlot');
    if (!container) return;

    // Spaghetti plot: x = run, y = -log10(FDR), one line per term
    const topTerms = getTopTermsForPlot(15);

    const traces = topTerms.map(term => ({
        type: 'scatter',
        mode: 'lines+markers',
        name: truncate(term.termName, 25),
        x: state.runLabels,
        y: state.runLabels.map(label => {
            const stats = term.stats[label];
            if (!stats || stats.fdr >= 1) return null;
            return -Math.log10(Math.max(stats.fdr, 1e-300));
        }),
        connectgaps: false,
        hovertemplate: '%{x}: %{y:.2f}<extra>%{fullData.name}</extra>',
    }));

    const layout = {
        title: { text: 'Term Trends Across Runs', font: { size: 14 } },
        xaxis: { title: 'Run' },
        yaxis: { title: '-log₁₀(FDR)' },
        hovermode: 'closest',
        legend: { font: { size: 9 } },
        margin: { l: 60, r: 20, t: 40, b: 60 },
        height: 400,
    };

    Plotly.newPlot(container, traces, layout, { responsive: true });
    state.plots.trendPlot = container;
}

function createHeatmap() {
    const container = document.getElementById('heatmap');
    if (!container) return;

    const topTerms = getTopTermsForPlot(30);

    const z = topTerms.map(term =>
        state.runLabels.map(label => {
            const stats = term.stats[label];
            if (!stats || stats.fdr >= 1) return null;
            return -Math.log10(Math.max(stats.fdr, 1e-300));
        })
    );

    const trace = {
        type: 'heatmap',
        z: z,
        x: state.runLabels,
        y: topTerms.map(t => truncate(t.termName, 35)),
        colorscale: 'Viridis',
        hoverongaps: false,
        colorbar: { title: '-log₁₀(FDR)', titleside: 'right' },
        hovertemplate: '%{y}<br>%{x}: %{z:.2f}<extra></extra>',
    };

    const layout = {
        title: { text: 'Significance Heatmap', font: { size: 14 } },
        xaxis: { side: 'bottom', tickangle: -30 },
        yaxis: { automargin: true, tickfont: { size: 9 } },
        margin: { l: 200, r: 80, t: 40, b: 80 },
        height: 500,
    };

    Plotly.newPlot(container, [trace], layout, { responsive: true });
    state.plots.heatmap = container;
}

function createUpsetPlot() {
    const container = document.getElementById('upsetPlot');
    if (!container) return;

    // Compute intersection sizes
    const intersections = computeIntersections();
    intersections.sort((a, b) => b.size - a.size);
    const top = intersections.slice(0, 15);
    if (top.length === 0) {
        Plotly.purge(container);
        container.innerHTML = '<div style="text-align:center;padding:2rem;color:#94a3b8;">No intersections found with current filters</div>';
        return;
    }

    const nSets = state.runLabels.length;
    const nInter = top.length;

    // --- Bar chart trace (top portion) ---
    const barTrace = {
        type: 'bar',
        x: top.map((_, i) => i),
        y: top.map(i => i.size),
        marker: { color: '#3b82f6', line: { width: 0 } },
        hovertext: top.map(i => i.label + ': ' + i.size + ' terms'),
        hoverinfo: 'text',
        xaxis: 'x',
        yaxis: 'y',
        showlegend: false,
        width: 0.6,
    };

    // --- Dot matrix traces (bottom portion) ---
    const dotTraces = [];

    // Background grid dots (grey)
    const bgX = [], bgY = [];
    for (let i = 0; i < nInter; i++) {
        for (let j = 0; j < nSets; j++) {
            bgX.push(i);
            bgY.push(j);
        }
    }
    dotTraces.push({
        type: 'scatter',
        mode: 'markers',
        x: bgX,
        y: bgY,
        marker: { size: 10, color: '#e2e8f0', symbol: 'circle' },
        xaxis: 'x2',
        yaxis: 'y2',
        showlegend: false,
        hoverinfo: 'skip',
    });

    // Active dots and connecting lines for each intersection
    for (let i = 0; i < nInter; i++) {
        const inter = top[i];
        const activeIndices = inter.runs.map(r => state.runLabels.indexOf(r)).filter(idx => idx >= 0);

        // Active dots (blue)
        dotTraces.push({
            type: 'scatter',
            mode: 'markers',
            x: activeIndices.map(() => i),
            y: activeIndices,
            marker: { size: 12, color: '#3b82f6', symbol: 'circle' },
            xaxis: 'x2',
            yaxis: 'y2',
            showlegend: false,
            hovertext: inter.label + ': ' + inter.size + ' terms',
            hoverinfo: 'text',
        });

        // Connecting line between active dots (if >1)
        if (activeIndices.length > 1) {
            const minY = Math.min(...activeIndices);
            const maxY = Math.max(...activeIndices);
            dotTraces.push({
                type: 'scatter',
                mode: 'lines',
                x: [i, i],
                y: [minY, maxY],
                line: { color: '#3b82f6', width: 2.5 },
                xaxis: 'x2',
                yaxis: 'y2',
                showlegend: false,
                hoverinfo: 'skip',
            });
        }
    }

    const layout = {
        grid: { rows: 2, columns: 1, subplots: [['xy'], ['x2y2']], roworder: 'top to bottom' },
        // Top bar chart
        xaxis: {
            showticklabels: false,
            showgrid: false,
            zeroline: false,
            range: [-0.5, nInter - 0.5],
        },
        yaxis: {
            title: { text: 'Count', font: { size: 11 } },
            domain: [0.45, 1],
            gridcolor: '#f1f5f9',
        },
        // Bottom dot matrix
        xaxis2: {
            showticklabels: false,
            showgrid: false,
            zeroline: false,
            range: [-0.5, nInter - 0.5],
        },
        yaxis2: {
            tickmode: 'array',
            tickvals: state.runLabels.map((_, i) => i),
            ticktext: state.runLabels,
            tickfont: { size: 10 },
            domain: [0, 0.4],
            showgrid: false,
            zeroline: false,
            fixedrange: true,
        },
        margin: { l: 80, r: 10, t: 10, b: 10 },
        height: 350,
        hovermode: 'closest',
        plot_bgcolor: 'white',
        paper_bgcolor: 'white',
    };

    Plotly.newPlot(container, [barTrace, ...dotTraces], layout, { responsive: true, displayModeBar: false });
}

function computeIntersections() {
    const fdrThreshold = state.filters.fdr;
    const n = state.runLabels.length;
    const intersections = [];

    // For each possible combination
    for (let mask = 1; mask < (1 << n); mask++) {
        const included = [];
        for (let i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                included.push(state.runLabels[i]);
            }
        }

        // Count terms significant in exactly these runs
        const count = state.merged.terms.filter(term => {
            if (state.filters.category !== 'all' && term.category !== state.filters.category) {
                return false;
            }
            const sigRuns = state.runLabels.filter(l => {
                const stats = term.stats?.[l];
                return stats && stats.fdr < fdrThreshold;
            });
            return sigRuns.length === included.length &&
                   included.every(l => sigRuns.includes(l)) &&
                   sigRuns.every(l => included.includes(l));
        }).length;

        if (count > 0) {
            intersections.push({
                runs: included,
                label: included.length === 1 ? included[0] + ' only' : included.join(' ∩ '),
                size: count,
            });
        }
    }

    return intersections;
}

// === Individual Run Panes (Full Single-Run Report UI) ===
const runPaneState = {};  // { safeId: { initialized, label, filters, selectedTerms, tables, allRows } }

function initRunTabs() {
    // Lazy init - done on tab switch
}

function initRunPane(label) {
    const safeId = makeSafeId(label);
    if (runPaneState[safeId]?.initialized) return;

    const runData = state.runs[label];
    if (!runData) return;

    // Initialize state for this run
    runPaneState[safeId] = {
        initialized: true,
        label: label,
        filters: { search: '', category: 'all', fdr: 0.05, topN: null },
        selectedTerms: new Set(),
        tables: {},
        allRows: [],
    };

    // Flatten all rows
    for (const [category, rows] of Object.entries(runData.tables)) {
        rows.forEach(row => {
            runPaneState[safeId].allRows.push({...row, _category: category});
        });
    }

    buildRunSummary(safeId, runData.summary);
    buildRunCategoryOptions(safeId, runData.summary.categories);
    buildRunAccordion(safeId, runData);
    initRunFilterListeners(safeId);
}

function buildRunSummary(safeId, summary) {
    const el = document.getElementById('runSummary-' + safeId);
    if (!el) return;

    const total = summary.total_terms || 0;
    const significant = summary.significant_terms || 0;
    const numCats = Object.keys(summary.categories || {}).length;

    el.innerHTML = `
        <div class="summary-card">
            <div class="count">${total}</div>
            <div class="label">Total Terms</div>
        </div>
        <div class="summary-card" style="border-left-color: var(--success-color);">
            <div class="count">${significant}</div>
            <div class="label">Significant (FDR &lt; 0.05)</div>
        </div>
        <div class="summary-card">
            <div class="count">${numCats}</div>
            <div class="label">Categories</div>
        </div>
    `;
}

function buildRunCategoryOptions(safeId, categories) {
    const select = document.querySelector(`.run-category[data-run="${safeId}"]`);
    if (!select || !categories) return;

    for (const catName of Object.keys(categories).sort()) {
        const option = document.createElement('option');
        option.value = catName;
        option.textContent = catName;
        select.appendChild(option);
    }
}

function buildRunAccordion(safeId, runData) {
    const accordion = document.getElementById('runAccordion-' + safeId);
    if (!accordion) return;

    const categories = Object.keys(runData.tables).sort();
    const rs = runPaneState[safeId];

    // Build accordion HTML
    let html = '';
    categories.forEach((category, i) => {
        const rows = runData.tables[category];
        const catId = `runCat-${safeId}-${i}`;
        const isFirst = i === 0;

        html += `
            <div class="accordion-item" data-category="${category}">
                <h2 class="accordion-header">
                    <button class="accordion-button ${isFirst ? '' : 'collapsed'}" type="button"
                            data-bs-toggle="collapse" data-bs-target="#${catId}">
                        ${category}
                        <span class="badge category-badge ms-2">${rows.length}</span>
                    </button>
                </h2>
                <div id="${catId}" class="accordion-collapse collapse ${isFirst ? 'show' : ''}"
                     data-bs-parent="#runAccordion-${safeId}">
                    <div class="accordion-body p-0">
                        <div id="runTable-${safeId}-${i}"></div>
                    </div>
                </div>
            </div>
        `;
    });
    accordion.innerHTML = html;

    // Initialize Tabulator tables for each category
    categories.forEach((category, i) => {
        const tableEl = document.getElementById(`runTable-${safeId}-${i}`);
        if (!tableEl) return;

        const rows = runData.tables[category];
        const columns = [
            {
                formatter: "rowSelection",
                titleFormatter: "rowSelection",
                hozAlign: "center",
                headerSort: false,
                width: 40,
                cellClick: function(e, cell) { cell.getRow().toggleSelect(); }
            },
            {
                title: "Term Name", field: "term_name", sorter: "string", minWidth: 200,
                formatter: function(cell) {
                    const data = cell.getRow().getData();
                    const termId = data.term_id || '';
                    return `<a href="#" class="term-link" data-term-id="${termId}"
                              onclick="showTermDetail('${safeId}', this); return false;">${cell.getValue()}</a>`;
                }
            },
            { title: "Term ID", field: "term_id", sorter: "string", width: 100 },
        ];

        // Add stat columns
        const sample = rows[0] || {};
        if ('binom_fdr' in sample) columns.push({ title: "FDR", field: "binom_fdr", sorter: "number", width: 100, formatter: formatScientific });
        if ('binom_p' in sample) columns.push({ title: "P-value", field: "binom_p", sorter: "number", width: 100, formatter: formatScientific });
        if ('binom_fold_enrichment' in sample) columns.push({ title: "Fold", field: "binom_fold_enrichment", sorter: "number", width: 80, formatter: formatDecimal });
        if ('observed_genes' in sample) columns.push({ title: "Genes", field: "observed_genes", sorter: "number", width: 70 });

        rs.tables[i] = new Tabulator(tableEl, {
            data: rows,
            columns: columns,
            layout: "fitDataFill",
            height: "400px",
            pagination: "local",
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100],
            initialSort: [{ column: "binom_fdr", dir: "asc" }],
            selectable: true,
            selectableRangeMode: "click",
            rowSelected: function(row) {
                rs.selectedTerms.add(row.getData().term_id);
                updateRunSelectionCount(safeId);
            },
            rowDeselected: function(row) {
                rs.selectedTerms.delete(row.getData().term_id);
                updateRunSelectionCount(safeId);
            },
        });
        rs.tables[i]._category = category;
    });
}

function initRunFilterListeners(safeId) {
    const searchEl = document.querySelector(`.run-search[data-run="${safeId}"]`);
    const categoryEl = document.querySelector(`.run-category[data-run="${safeId}"]`);
    const fdrEl = document.querySelector(`.run-fdr[data-run="${safeId}"]`);
    const topNEl = document.querySelector(`.run-topn[data-run="${safeId}"]`);

    if (searchEl) {
        searchEl.addEventListener('input', debounce(() => {
            runPaneState[safeId].filters.search = searchEl.value.toLowerCase();
            applyRunFilters(safeId);
        }, 300));
    }
    if (categoryEl) {
        categoryEl.addEventListener('change', () => {
            runPaneState[safeId].filters.category = categoryEl.value;
            applyRunFilters(safeId);
        });
    }
    if (fdrEl) {
        fdrEl.addEventListener('change', () => {
            runPaneState[safeId].filters.fdr = parseFloat(fdrEl.value);
            applyRunFilters(safeId);
        });
    }
    if (topNEl) {
        topNEl.addEventListener('change', () => {
            const val = topNEl.value;
            runPaneState[safeId].filters.topN = val ? parseInt(val) : null;
            applyRunFilters(safeId);
        });
    }
}

function applyRunFilters(safeId) {
    const rs = runPaneState[safeId];
    if (!rs) return;

    const { search, category, fdr, topN } = rs.filters;

    // Apply filters to each table
    Object.values(rs.tables).forEach(table => {
        const tableCat = table._category;

        // Hide entire accordion item if category doesn't match
        const accordionItem = document.querySelector(`#runAccordion-${safeId} .accordion-item[data-category="${tableCat}"]`);
        if (accordionItem) {
            accordionItem.style.display = (category === 'all' || category === tableCat) ? '' : 'none';
        }

        // Apply row filters
        table.setFilter(function(data) {
            if (search && !data.term_name?.toLowerCase().includes(search) &&
                !data.term_id?.toLowerCase().includes(search)) {
                return false;
            }
            if (fdr < 1 && data.binom_fdr > fdr) {
                return false;
            }
            return true;
        });

        // Apply top N
        if (topN) {
            table.setPageSize(topN);
        } else {
            table.setPageSize(50);
        }
    });
}

function updateRunSelectionCount(safeId) {
    const rs = runPaneState[safeId];
    if (!rs) return;

    const count = rs.selectedTerms.size;
    const countEl = document.getElementById('runSelectedCount-' + safeId);
    const btnEl = document.getElementById('runPlotBtn-' + safeId);

    if (countEl) countEl.textContent = count;
    if (btnEl) btnEl.disabled = count === 0;
}

function runSelectAllVisible(safeId) {
    const rs = runPaneState[safeId];
    if (!rs) return;

    Object.values(rs.tables).forEach(table => {
        table.getRows("active").forEach(row => {
            row.select();
            rs.selectedTerms.add(row.getData().term_id);
        });
    });
    updateRunSelectionCount(safeId);
}

function runDeselectAll(safeId) {
    const rs = runPaneState[safeId];
    if (!rs) return;

    Object.values(rs.tables).forEach(table => {
        table.deselectRow();
    });
    rs.selectedTerms.clear();
    updateRunSelectionCount(safeId);
}

function generateRunPlot(safeId) {
    const rs = runPaneState[safeId];
    if (!rs || rs.selectedTerms.size === 0) return;

    const plotType = document.getElementById('runPlotType-' + safeId)?.value || 'bar';
    const metric = document.getElementById('runPlotMetric-' + safeId)?.value || 'neglog_fdr';
    const container = document.getElementById('runPlotContainer-' + safeId);
    if (!container) return;

    // Get selected term data
    const selectedData = rs.allRows.filter(r => rs.selectedTerms.has(r.term_id));

    // Calculate metric values
    const getMetricValue = (row) => {
        if (metric === 'neglog_fdr') return -Math.log10(Math.max(row.binom_fdr || 1, 1e-300));
        if (metric === 'neglog_p') return -Math.log10(Math.max(row.binom_p || 1, 1e-300));
        if (metric === 'fold') return row.binom_fold_enrichment || 0;
        return 0;
    };

    const sortedData = [...selectedData].sort((a, b) => getMetricValue(b) - getMetricValue(a));
    const labels = sortedData.map(r => truncate(r.term_name, 40));
    const values = sortedData.map(getMetricValue);
    const metricLabel = metric === 'neglog_fdr' ? '-log₁₀(FDR)' :
                        metric === 'neglog_p' ? '-log₁₀(P-value)' : 'Fold Enrichment';

    let trace, layout;
    if (plotType === 'bar') {
        trace = {
            type: 'bar',
            y: labels,
            x: values,
            orientation: 'h',
            marker: { color: '#3b82f6' },
        };
        layout = {
            title: { text: `${rs.label} - Selected Terms`, font: { size: 14 } },
            xaxis: { title: metricLabel },
            yaxis: { automargin: true, tickfont: { size: 10 } },
            margin: { l: 200, r: 20, t: 40, b: 60 },
            height: Math.max(300, sortedData.length * 25 + 100),
        };
    } else {
        const sizes = sortedData.map(r => Math.sqrt(r.observed_genes || 10) * 4 + 5);
        trace = {
            type: 'scatter',
            mode: 'markers',
            y: labels,
            x: values,
            marker: { size: sizes, color: values, colorscale: 'Viridis', showscale: true,
                      colorbar: { title: metricLabel } },
        };
        layout = {
            title: { text: `${rs.label} - Selected Terms`, font: { size: 14 } },
            xaxis: { title: metricLabel },
            yaxis: { automargin: true, tickfont: { size: 10 } },
            margin: { l: 200, r: 80, t: 40, b: 60 },
            height: Math.max(300, sortedData.length * 25 + 100),
        };
    }

    Plotly.newPlot(container, [trace], layout, { responsive: true });
}

function exportRunPlotSVG(safeId) {
    const container = document.getElementById('runPlotContainer-' + safeId);
    if (container) Plotly.downloadImage(container, { format: 'svg', filename: 'plot_' + safeId });
}

function exportRunPlotPNG(safeId) {
    const container = document.getElementById('runPlotContainer-' + safeId);
    if (container) Plotly.downloadImage(container, { format: 'png', scale: 2, filename: 'plot_' + safeId });
}

function exportRunTSV(safeId) {
    const rs = runPaneState[safeId];
    if (!rs) return;

    const rows = rs.allRows;
    const header = ['term_name', 'term_id', 'category', 'binom_fdr', 'binom_p', 'binom_fold_enrichment', 'observed_genes'];
    const tsv = [header.join('\\t')];
    rows.forEach(r => {
        tsv.push([r.term_name, r.term_id, r._category, r.binom_fdr, r.binom_p, r.binom_fold_enrichment, r.observed_genes].join('\\t'));
    });
    downloadFile(tsv.join('\\n'), `${rs.label}_results.tsv`, 'text/tab-separated-values');
}

function showTermDetail(safeId, linkEl) {
    const termId = linkEl.dataset.termId;
    const rs = runPaneState[safeId];
    if (!rs || !termId) return;

    const term = rs.allRows.find(r => r.term_id === termId);
    if (!term) return;

    // Populate modal
    document.getElementById('modalTermName').textContent = term.term_name || '';
    document.getElementById('modalTermId').textContent = term.term_id || '';

    // Stats grid
    const statsHtml = `
        <div class="term-stats-grid">
            <div class="term-stat-item"><div class="stat-label">FDR</div><div class="stat-value">${formatSci(term.binom_fdr)}</div></div>
            <div class="term-stat-item"><div class="stat-label">P-value</div><div class="stat-value">${formatSci(term.binom_p)}</div></div>
            <div class="term-stat-item"><div class="stat-label">Fold Enrichment</div><div class="stat-value">${term.binom_fold_enrichment?.toFixed(2) || 'N/A'}</div></div>
            <div class="term-stat-item"><div class="stat-label">Observed Genes</div><div class="stat-value">${term.observed_genes || 'N/A'}</div></div>
        </div>
    `;
    document.getElementById('modalStats').innerHTML = statsHtml;

    // Genes
    const genesSection = document.getElementById('genesSection');
    const genesList = document.getElementById('modalGenes');
    if (term.genes) {
        const genes = term.genes.split(',').map(g => g.trim()).filter(g => g);
        genesList.innerHTML = genes.map(g => `<span class="gene-badge">${g}</span>`).join('');
        genesSection.style.display = 'block';
    } else {
        genesSection.style.display = 'none';
    }

    // External links
    const termIdClean = term.term_id || '';
    document.getElementById('amigoLink').href = termIdClean.startsWith('GO:') ?
        `https://amigo.geneontology.org/amigo/term/${termIdClean}` : '#';
    document.getElementById('quickgoLink').href = termIdClean.startsWith('GO:') ?
        `https://www.ebi.ac.uk/QuickGO/term/${termIdClean}` : '#';

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('termModal'));
    modal.show();
}

function copyGenes() {
    const genesList = document.getElementById('modalGenes');
    if (!genesList) return;
    const genes = Array.from(genesList.querySelectorAll('.gene-badge')).map(el => el.textContent).join(', ');
    navigator.clipboard.writeText(genes).then(() => {
        const btn = document.getElementById('copyGenesBtn');
        if (btn) {
            const orig = btn.textContent;
            btn.textContent = 'Copied!';
            setTimeout(() => btn.textContent = orig, 1500);
        }
    });
}

// === Selection Management ===
function updateSelectionInfo() {
    const count = state.selectedTerms.size;
    const infoEl = document.getElementById('selectionInfo');
    const countEl = document.getElementById('selectedCount');

    if (infoEl) {
        infoEl.style.display = count > 0 ? 'flex' : 'none';
    }
    if (countEl) {
        countEl.textContent = count;
    }
}

function selectAllVisible() {
    if (!state.tables.compare) return;
    state.tables.compare.selectRow();
    state.tables.compare.getSelectedRows().forEach(row => {
        state.selectedTerms.add(row.getData().termId);
    });
    updateSelectionInfo();
}

function deselectAll() {
    if (!state.tables.compare) return;
    state.tables.compare.deselectRow();
    state.selectedTerms.clear();
    updateSelectionInfo();
}

// === Export Functions ===
function exportMergedTSV() {
    const data = state.tables.compare?.getData() || state.merged.terms;

    // Build header
    let header = ['term_name', 'term_id', 'category'];
    state.runLabels.forEach(label => {
        header.push(label + '_fdr', label + '_fold', label + '_genes');
    });
    header.push('presence', 'max_neglog', 'range');

    // Build rows
    const rows = data.map(term => {
        let row = [term.termName, term.termId, term.category];
        state.runLabels.forEach(label => {
            const stats = term.stats?.[label];
            row.push(stats?.fdr ?? '', stats?.fold ?? '', stats?.observed_genes ?? '');
        });
        row.push(term.presence?.join(';') || '', term.maxNegLog || '', term.range || '');
        return row.join('\\t');
    });

    downloadFile(header.join('\\t') + '\\n' + rows.join('\\n'), 'comparison_results.tsv', 'text/tab-separated-values');
}

function exportSelectedTSV() {
    if (state.selectedTerms.size === 0) {
        alert('No terms selected. Select rows from the table first.');
        return;
    }

    const selectedData = state.merged.terms.filter(t => state.selectedTerms.has(t.termId));

    let header = ['term_name', 'term_id', 'category'];
    state.runLabels.forEach(label => {
        header.push(label + '_fdr');
    });

    const rows = selectedData.map(term => {
        let row = [term.termName, term.termId, term.category];
        state.runLabels.forEach(label => {
            const stats = term.stats?.[label];
            row.push(stats?.fdr ?? '');
        });
        return row.join('\\t');
    });

    downloadFile(header.join('\\t') + '\\n' + rows.join('\\n'), 'selected_terms.tsv', 'text/tab-separated-values');
}

function exportPlotSVG(plotId) {
    const container = document.getElementById(plotId);
    if (!container) return;
    Plotly.downloadImage(container, { format: 'svg', filename: plotId });
}

function exportPlotPNG(plotId) {
    const container = document.getElementById(plotId);
    if (!container) return;
    Plotly.downloadImage(container, { format: 'png', scale: 2, filename: plotId });
}

// === Utility Functions ===
function getTopTermsForPlot(n) {
    const fdrThreshold = state.filters.fdr;
    return state.merged.terms
        .filter(term => {
            // Category filter
            if (state.filters.category !== 'all' && term.category !== state.filters.category) {
                return false;
            }
            // FDR filter - must be significant in at least one run
            if (fdrThreshold < 1) {
                let passesFdr = false;
                for (const label of state.runLabels) {
                    const stats = term.stats?.[label];
                    if (stats && stats.fdr <= fdrThreshold) {
                        passesFdr = true;
                        break;
                    }
                }
                if (!passesFdr) return false;
            }
            return term.maxNegLog > 0;
        })
        .sort((a, b) => b.maxNegLog - a.maxNegLog)
        .slice(0, n);
}

function formatScientific(cell) {
    const val = cell.getValue();
    if (val == null || val === '') return '-';
    const num = parseFloat(val);
    if (isNaN(num)) return '-';
    if (num >= 0.01 && num < 1000) return num.toFixed(4);
    return num.toExponential(2);
}

function formatDecimal(cell) {
    const val = cell.getValue();
    if (val == null || val === '') return '-';
    const num = parseFloat(val);
    if (isNaN(num)) return '-';
    return num.toFixed(2);
}

function formatSci(num) {
    if (num == null) return 'N/A';
    return num.toExponential(2);
}

function presenceFormatter(cell) {
    const presence = cell.getValue();
    if (!presence || !Array.isArray(presence)) return '';
    return state.runLabels.map(label => {
        const present = presence.includes(label);
        return `<span class="presence-dot ${present ? 'present' : 'absent'}"
                      title="${label}"></span>`;
    }).join('');
}

function truncate(str, len) {
    if (!str) return '';
    return str.length > len ? str.slice(0, len - 3) + '...' : str;
}

function makeSafeId(str) {
    return str.replace(/[^a-zA-Z0-9]/g, '_');
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
"""

# Main HTML template for compare mode
COMPARE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    {libraries_css}

    <style>
{custom_css}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="report-header">
        <div class="container-fluid">
            <h1>{title}</h1>
            <div class="subtitle">Comparing {num_runs} runs | Generated by pyGREAT</div>
        </div>
    </div>

    <div class="container-fluid">
        <!-- Main Tab Navigation -->
        <ul class="nav nav-tabs main-tabs" id="mainTabs" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" data-tab="compare" href="#">Compare</a>
            </li>
            {run_tabs_html}
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="mainTabContent">
            <!-- Compare Pane -->
            <div class="main-tab-pane show active" id="pane-compare">
                <!-- Comparison Controls -->
                <div class="compare-controls">
                    <div class="filter-group">
                        <label for="compareSearch">Search:</label>
                        <input type="text" id="compareSearch" class="form-control form-control-sm"
                               placeholder="Search terms...">
                    </div>
                    <div class="filter-group">
                        <label for="compareCategory">Category:</label>
                        <select id="compareCategory" class="form-select form-select-sm">
                            <option value="all">All Categories</option>
                            {category_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="compareFdr">FDR:</label>
                        <select id="compareFdr" class="form-select form-select-sm">
                            <option value="1">All</option>
                            <option value="0.05" selected>&le; 0.05</option>
                            <option value="0.01">&le; 0.01</option>
                            <option value="0.001">&le; 0.001</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="compareMetric">Metric:</label>
                        <select id="compareMetric" class="form-select form-select-sm">
                            <option value="fdr">FDR</option>
                            <option value="p">P-value</option>
                            <option value="fold">Fold Enrichment</option>
                        </select>
                    </div>
                    <div class="export-buttons ms-auto">
                        <button class="btn btn-sm btn-secondary" onclick="exportMergedTSV()">
                            Export TSV
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="exportSelectedTSV()">
                            Export Selected
                        </button>
                    </div>
                </div>

                <!-- Summary Cards -->
                <div class="summary-cards">
                    <div class="summary-card shared">
                        <div class="count" id="sharedCount">0</div>
                        <div class="label">Shared (All Runs)</div>
                    </div>
                    <div class="summary-card any">
                        <div class="count" id="anyCount">0</div>
                        <div class="label">Significant (Any)</div>
                    </div>
                    <div class="summary-card">
                        <div class="count" id="totalCount">0</div>
                        <div class="label">Total Terms</div>
                    </div>
                    {unique_cards_html}
                </div>

                <!-- Selection Info -->
                <div class="selection-info" id="selectionInfo" style="display: none;">
                    <span><span class="count" id="selectedCount">0</span> terms selected</span>
                    <button class="btn btn-sm btn-outline-primary" onclick="selectAllVisible()">
                        Select All Visible
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="deselectAll()">
                        Clear Selection
                    </button>
                </div>

                <!-- Comparison Table -->
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <span><strong>Merged Comparison Table</strong>
                        <span class="text-muted ms-2">Terms matched by {match_by}</span></span>
                    </div>
                    <div class="card-body p-0">
                        <div id="compareTable"></div>
                    </div>
                </div>

                <!-- Compare Plots -->
                <div class="row">
                    <div class="col-lg-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header d-flex justify-content-between">
                                <span>Multi-Run Dot Plot</span>
                                <div>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotSVG('multiRunDotPlot')">SVG</button>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotPNG('multiRunDotPlot')">PNG</button>
                                </div>
                            </div>
                            <div class="card-body p-2">
                                <div id="multiRunDotPlot" class="plot-container"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header d-flex justify-content-between">
                                <span>Term Trends</span>
                                <div>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotSVG('trendPlot')">SVG</button>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotPNG('trendPlot')">PNG</button>
                                </div>
                            </div>
                            <div class="card-body p-2">
                                <div id="trendPlot" class="plot-container"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-lg-{heatmap_col_size} mb-4">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between">
                                <span>Significance Heatmap</span>
                                <div>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotSVG('heatmap')">SVG</button>
                                    <button class="btn btn-sm btn-outline-secondary"
                                            onclick="exportPlotPNG('heatmap')">PNG</button>
                                </div>
                            </div>
                            <div class="card-body p-2">
                                <div id="heatmap" class="plot-container"></div>
                            </div>
                        </div>
                    </div>
                    {upset_section}
                </div>
            </div>

            <!-- Individual Run Panes -->
            {run_panes_html}
        </div>
    </div>

    <!-- Footer -->
    <div class="report-footer">
        Generated by <a href="https://github.com/khan-lab/pyGREAT" target="_blank">pyGREAT</a>
    </div>

    <!-- Term Detail Modal -->
    <div class="modal fade" id="termModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="modalTermName">Term Name</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p><strong>Term ID:</strong> <span id="modalTermId"></span></p>

                    <h6 class="mt-3">Statistics</h6>
                    <div id="modalStats"></div>

                    <div id="genesSection" class="mt-3" style="display:none;">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h6 class="mb-0">Associated Genes</h6>
                            <button id="copyGenesBtn" class="btn btn-sm btn-outline-secondary" onclick="copyGenes()">
                                Copy Genes
                            </button>
                        </div>
                        <div class="genes-list" id="modalGenes"></div>
                    </div>

                    <div class="external-links mt-3">
                        <a id="amigoLink" href="#" target="_blank" class="btn btn-sm btn-outline-primary">
                            View in AmiGO
                        </a>
                        <a id="quickgoLink" href="#" target="_blank" class="btn btn-sm btn-outline-primary">
                            View in QuickGO
                        </a>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>

    {libraries_js}

    <!-- Data -->
    <script>
        const DATA = {data_json};
        const CONFIG = {config_json};
    </script>

    <!-- Custom JavaScript -->
    <script>
{custom_js}
    </script>
</body>
</html>
"""


def get_upset_section_html() -> str:
    """Return HTML for UpSet plot section (used when >= 3 runs)."""
    return """
                    <div class="col-lg-4 mb-4">
                        <div class="card h-100">
                            <div class="card-header">Set Intersections</div>
                            <div class="card-body p-2">
                                <div id="upsetPlot" class="plot-container" style="min-height: 350px;"></div>
                            </div>
                        </div>
                    </div>
    """
