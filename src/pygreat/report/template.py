"""HTML template for GREAT enrichment report.

Contains the complete HTML template with embedded CSS and JavaScript
for generating self-contained interactive reports.
"""

# Custom CSS styles
CUSTOM_CSS = """
:root {
    --primary-color: #2563eb;
    --success-color: #16a34a;
    --warning-color: #d97706;
    --danger-color: #dc2626;
    --bg-light: #f8fafc;
    --border-color: #e2e8f0;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: var(--bg-light);
}

.report-header {
    background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    color: white;
    padding: 1.5rem 0;
    margin-bottom: 1.5rem;
}

.report-header h1 {
    margin: 0;
    font-weight: 600;
}

.report-header .subtitle {
    opacity: 0.9;
    font-size: 0.9rem;
}

/* Summary Cards */
.summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.summary-card {
    background: white;
    border-radius: 0.5rem;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border-left: 4px solid var(--primary-color);
}

.summary-card.significant {
    border-left-color: var(--success-color);
}

.summary-card .card-value {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
}

.summary-card .card-label {
    color: #64748b;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Top Terms */
.top-terms-section {
    background: white;
    border-radius: 0.5rem;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
}

.top-terms-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.top-terms-category {
    border: 1px solid var(--border-color);
    border-radius: 0.375rem;
    padding: 0.75rem;
}

.top-terms-category h6 {
    margin: 0 0 0.5rem 0;
    color: var(--primary-color);
    font-weight: 600;
}

.top-terms-category ul {
    margin: 0;
    padding-left: 1.25rem;
    font-size: 0.875rem;
}

.top-terms-category li {
    margin-bottom: 0.25rem;
    color: #475569;
}

.top-terms-category .fdr-badge {
    font-size: 0.75rem;
    color: #64748b;
}

/* Filters Bar */
.filters-bar {
    background: white;
    border-radius: 0.5rem;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}

.filters-bar .filter-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.filters-bar label {
    font-size: 0.875rem;
    color: #64748b;
    white-space: nowrap;
}

.filters-bar input[type="text"] {
    min-width: 250px;
}

/* Accordion */
.accordion-button:not(.collapsed) {
    background-color: #eff6ff;
    color: var(--primary-color);
}

.accordion-button .badge {
    margin-left: 0.5rem;
}

.category-badge {
    background-color: var(--primary-color);
}

/* Tables */
.table-container {
    background: white;
    padding: 1rem;
}

table.dataTable {
    font-size: 0.875rem;
}

table.dataTable thead th {
    background-color: #f8fafc;
    border-bottom: 2px solid var(--border-color);
    font-weight: 600;
    white-space: nowrap;
}

table.dataTable tbody tr:hover {
    background-color: #f1f5f9 !important;
}

table.dataTable tbody tr.selected {
    background-color: #dbeafe !important;
}

table.dataTable tbody td {
    vertical-align: middle;
}

.term-link {
    color: var(--primary-color);
    text-decoration: none;
    cursor: pointer;
}

.term-link:hover {
    text-decoration: underline;
}

/* Selection checkbox column */
table.dataTable td.select-checkbox,
table.dataTable th.select-checkbox {
    width: 40px;
    min-width: 40px;
    max-width: 40px;
    text-align: center;
    vertical-align: middle;
    padding: 0.5rem !important;
}

/* Checkbox styling for better clickability */
.term-select {
    width: 18px;
    height: 18px;
    cursor: pointer;
    margin: 0;
    padding: 0;
    vertical-align: middle;
    accent-color: var(--primary-color);
}

.term-select:hover {
    transform: scale(1.1);
}

/* Ensure checkbox cell has clickable area */
table.dataTable td.select-checkbox {
    cursor: pointer;
}

/* Plot Builder */
.plot-builder {
    background: white;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-top: 1.5rem;
}

.plot-builder .card-header {
    background-color: #f8fafc;
    border-bottom: 1px solid var(--border-color);
    font-weight: 600;
}

.plot-settings {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    margin-bottom: 1rem;
}

.plot-settings .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.plot-settings label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
}

#plotContainer {
    min-height: 400px;
    border: 1px dashed var(--border-color);
    border-radius: 0.375rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #94a3b8;
}

#plotContainer.has-plot {
    border: none;
}

.export-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border-color);
}

/* Modal */
.modal-header {
    background-color: #f8fafc;
    border-bottom: 1px solid var(--border-color);
}

.term-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
}

.stat-item {
    padding: 0.5rem;
    background-color: #f8fafc;
    border-radius: 0.375rem;
}

.stat-item .stat-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
}

.stat-item .stat-value {
    font-weight: 600;
    color: #1e293b;
}

.genes-section {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f8fafc;
    border-radius: 0.375rem;
}

.genes-list {
    max-height: 150px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.875rem;
    padding: 0.5rem;
    background: white;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
}

.external-links {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
}

/* Footer */
.report-footer {
    text-align: center;
    padding: 1.5rem;
    color: #64748b;
    font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 768px) {
    .filters-bar {
        flex-direction: column;
        align-items: stretch;
    }

    .filters-bar input[type="text"] {
        min-width: 100%;
    }

    .plot-settings {
        grid-template-columns: 1fr 1fr;
    }
}
"""

# Custom JavaScript
CUSTOM_JS = """
// State management
let tables = {};
let allData = {};
let selectedTerms = new Set();

// Initialize on document ready
$(document).ready(function() {
    // Store all data for easy access
    DATA.categories.forEach(cat => {
        allData[cat] = DATA.tables[cat];
    });

    initTables();
    setupFilterListeners();
    updateSelectionCount();
});

// Initialize DataTables for each category
function initTables() {
    document.querySelectorAll('.enrichment-table').forEach(el => {
        const category = el.dataset.category;
        const tableData = DATA.tables[category] || [];

        // Build columns with checkbox first
        const columns = [
            {
                data: null,
                defaultContent: '',
                className: 'select-checkbox',
                orderable: false,
                render: function(data, type, row) {
                    const termId = row.term_id;
                    const checked = selectedTerms.has(termId) ? 'checked' : '';
                    return `<input type="checkbox" class="term-select" data-term-id="${termId}" ${checked}>`;
                }
            }
        ];

        // Add data columns
        DATA.columns.forEach(col => {
            const colDef = {
                data: col.data,
                title: col.title,
                render: function(data, type, row) {
                    if (data === null || data === undefined) return '-';

                    // For display
                    if (type === 'display') {
                        if (col.data === 'term_name') {
                            return `<a class="term-link" onclick="showTermDetail('${row.term_id}')">${escapeHtml(data)}</a>`;
                        }
                        if (col.data === 'term_id' && data.startsWith('GO:')) {
                            return `<a href="https://amigo.geneontology.org/amigo/term/${data}" target="_blank">${data}</a>`;
                        }
                        if (col.render_type === 'scientific') {
                            return formatScientific(data);
                        }
                        if (col.render_type === 'decimal') {
                            return typeof data === 'number' ? data.toFixed(3) : data;
                        }
                        if (col.render_type === 'integer') {
                            return typeof data === 'number' ? Math.round(data) : data;
                        }
                    }
                    return data;
                }
            };
            columns.push(colDef);
        });

        // Find FDR column index for default sorting
        let fdrColIdx = columns.findIndex(c => c.data === 'binom_fdr');
        if (fdrColIdx === -1) fdrColIdx = columns.findIndex(c => c.data === 'hyper_fdr');
        if (fdrColIdx === -1) fdrColIdx = columns.findIndex(c => c.data === 'binom_p');
        if (fdrColIdx === -1) fdrColIdx = 2; // Default to first data column after checkbox and term_id

        tables[category] = $(el).DataTable({
            data: tableData,
            columns: columns,
            order: [[fdrColIdx, 'asc']],
            pageLength: 10,
            scrollX: true,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, 'All']],
            dom: '<"row"<"col-sm-6"l><"col-sm-6"f>>rtip',
            language: {
                search: 'Search:',
                lengthMenu: 'Show _MENU_ entries'
            },
            columnDefs: [
                { targets: 0, orderable: false }
            ]
        });
    });

    // Handle checkbox changes using document-level delegation (works with DataTables pagination)
    $(document).on('change', '.term-select', function() {
        const termId = $(this).data('term-id');
        if (this.checked) {
            selectedTerms.add(termId);
        } else {
            selectedTerms.delete(termId);
        }
        updateSelectionCount();
    });

    // Also allow clicking the cell itself to toggle the checkbox (larger click target)
    $(document).on('click', 'td.select-checkbox', function(e) {
        // Don't double-trigger if clicking directly on checkbox
        if ($(e.target).hasClass('term-select')) return;

        const checkbox = $(this).find('.term-select');
        if (checkbox.length) {
            checkbox.prop('checked', !checkbox.prop('checked')).trigger('change');
        }
    });
}

// Setup filter listeners
function setupFilterListeners() {
    $('#globalSearch').on('keyup', applyFilters);
    $('#categoryFilter').on('change', applyFilters);
    $('#fdrFilter').on('change', applyFilters);
    $('#pvalFilter').on('change', applyFilters);
    $('#topNFilter').on('change', applyFilters);
}

// Apply filters to all tables
function applyFilters() {
    const search = $('#globalSearch').val().toLowerCase();
    const categoryFilter = $('#categoryFilter').val();
    const fdrThreshold = parseFloat($('#fdrFilter').val()) || 1;
    const pvalThreshold = parseFloat($('#pvalFilter').val()) || 1;
    const topN = parseInt($('#topNFilter').val()) || Infinity;

    // Show/hide accordion sections based on category filter
    document.querySelectorAll('.accordion-item').forEach(item => {
        const cat = item.dataset.category;
        if (categoryFilter === 'all' || cat === categoryFilter) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });

    // Apply filters to each table
    Object.entries(tables).forEach(([category, table]) => {
        // Clear previous search
        table.search('');

        // Apply global search
        if (search) {
            table.search(search);
        }

        // First, compute which term_ids pass FDR/P-value filters and are in top N
        const categoryData = allData[category] || [];

        // Filter by FDR and P-value thresholds
        let filteredData = categoryData.filter(row => {
            const fdr = parseFloat(row.binom_fdr || row.hyper_fdr || 1);
            const pval = parseFloat(row.binom_p || row.hyper_p || 1);
            return fdr <= fdrThreshold && pval <= pvalThreshold;
        });

        // Sort by FDR to get top N most significant
        filteredData.sort((a, b) => {
            const fdrA = parseFloat(a.binom_fdr || a.hyper_fdr || 1);
            const fdrB = parseFloat(b.binom_fdr || b.hyper_fdr || 1);
            return fdrA - fdrB;
        });

        // Take top N
        const topNData = filteredData.slice(0, topN);
        const allowedTermIds = new Set(topNData.map(row => row.term_id));

        // Custom filtering using the precomputed set
        $.fn.dataTable.ext.search.push(function(settings, data, dataIndex, rowData) {
            // Only apply to this specific table
            if (settings.nTable.dataset.category !== category) return true;
            return allowedTermIds.has(rowData.term_id);
        });

        table.draw();

        // Remove custom filter after drawing
        $.fn.dataTable.ext.search.pop();
    });

    updateCategoryCounts();
}

// Update category counts in accordion headers
function updateCategoryCounts() {
    Object.entries(tables).forEach(([category, table]) => {
        const count = table.rows({ filter: 'applied' }).count();
        const badge = document.querySelector(`.accordion-button[data-category="${category}"] .badge`);
        if (badge) {
            badge.textContent = count;
        }
    });
}

// Update selection count
function updateSelectionCount() {
    const count = selectedTerms.size;
    $('#selectedCount').text(count);
    $('#generatePlotBtn').prop('disabled', count === 0);
}

// Show term detail modal
function showTermDetail(termId) {
    // Find the term in all data
    let term = null;
    for (const category in allData) {
        term = allData[category].find(t => t.term_id === termId);
        if (term) break;
    }

    if (!term) return;

    // Populate modal
    $('#modalTermName').text(term.term_name);
    $('#modalTermId').text(term.term_id);

    // Build stats HTML
    let statsHtml = '';
    const statFields = [
        { key: 'binom_p', label: 'Binom P-value' },
        { key: 'binom_fdr', label: 'Binom FDR' },
        { key: 'binom_fold_enrichment', label: 'Binom Fold' },
        { key: 'hyper_p', label: 'Hyper P-value' },
        { key: 'hyper_fdr', label: 'Hyper FDR' },
        { key: 'hyper_fold_enrichment', label: 'Hyper Fold' },
        { key: 'observed_regions', label: 'Obs Regions' },
        { key: 'expected_regions', label: 'Exp Regions' },
        { key: 'observed_genes', label: 'Obs Genes' },
        { key: 'total_genes', label: 'Total Genes' },
    ];

    statFields.forEach(field => {
        if (term[field.key] !== undefined && term[field.key] !== null) {
            let value = term[field.key];
            if (field.key.includes('_p') || field.key.includes('_fdr')) {
                value = formatScientific(value);
            } else if (typeof value === 'number' && !Number.isInteger(value)) {
                value = value.toFixed(3);
            }
            statsHtml += `
                <div class="stat-item">
                    <div class="stat-label">${field.label}</div>
                    <div class="stat-value">${value}</div>
                </div>
            `;
        }
    });

    $('#modalStats').html(statsHtml);

    // Handle genes
    const genes = term.genes;
    if (genes) {
        $('#genesSection').show();
        $('#modalGenes').text(genes);
    } else {
        $('#genesSection').hide();
    }

    // Set external links
    if (term.term_id.startsWith('GO:')) {
        $('#amigoLink').attr('href', `https://amigo.geneontology.org/amigo/term/${term.term_id}`).show();
        $('#quickgoLink').attr('href', `https://www.ebi.ac.uk/QuickGO/term/${term.term_id}`).show();
    } else {
        $('#amigoLink').hide();
        $('#quickgoLink').hide();
    }

    // Show modal
    new bootstrap.Modal(document.getElementById('termModal')).show();
}

// Copy genes to clipboard
function copyGenes() {
    const genes = $('#modalGenes').text();
    navigator.clipboard.writeText(genes).then(() => {
        // Show feedback
        const btn = $('#copyGenesBtn');
        const originalText = btn.text();
        btn.text('Copied!');
        setTimeout(() => btn.text(originalText), 1500);
    });
}

// Get selected terms data
function getSelectedTerms() {
    const selected = [];
    for (const category in allData) {
        allData[category].forEach(term => {
            if (selectedTerms.has(term.term_id)) {
                selected.push(term);
            }
        });
    }
    return selected;
}

// Get filtered terms (visible in tables)
function getFilteredTerms() {
    const filtered = [];
    Object.entries(tables).forEach(([category, table]) => {
        table.rows({ filter: 'applied' }).data().each(function(row) {
            filtered.push(row);
        });
    });
    return filtered;
}

// Generate plot
function generatePlot() {
    const selected = getSelectedTerms();
    if (selected.length === 0) {
        alert('Please select at least one term from the tables.');
        return;
    }

    const plotType = $('#plotType').val();
    const metric = $('#plotMetric').val();
    const width = parseInt($('#plotWidth').val()) || 800;
    const height = parseInt($('#plotHeight').val()) || 600;
    const fontSize = parseInt($('#fontSize').val()) || 12;
    const colorPalette = $('#colorPalette').val();
    const orientation = $('#orientation').val();
    const showValues = $('#showValues').is(':checked');

    // Sort by value
    const sortedData = [...selected].sort((a, b) => {
        const valA = getMetricValue(a, metric);
        const valB = getMetricValue(b, metric);
        return valB - valA;
    });

    const values = sortedData.map(t => getMetricValue(t, metric));
    const labels = sortedData.map(t => truncateLabel(t.term_name, 50));
    const geneCounts = sortedData.map(t => t.observed_genes || t.total_genes || 10);

    let trace, layout;

    if (plotType === 'bar') {
        if (orientation === 'horizontal') {
            trace = {
                type: 'bar',
                orientation: 'h',
                y: labels,
                x: values,
                marker: {
                    color: values,
                    colorscale: colorPalette
                },
                text: showValues ? values.map(v => v.toFixed(2)) : null,
                textposition: 'outside',
                hovertemplate: '%{y}<br>Value: %{x:.3f}<extra></extra>'
            };
            layout = {
                xaxis: { title: getMetricLabel(metric) },
                yaxis: { automargin: true },
                margin: { l: 250, r: 50, t: 50, b: 50 }
            };
        } else {
            trace = {
                type: 'bar',
                x: labels,
                y: values,
                marker: {
                    color: values,
                    colorscale: colorPalette
                },
                text: showValues ? values.map(v => v.toFixed(2)) : null,
                textposition: 'outside',
                hovertemplate: '%{x}<br>Value: %{y:.3f}<extra></extra>'
            };
            layout = {
                yaxis: { title: getMetricLabel(metric) },
                xaxis: { tickangle: -45, automargin: true },
                margin: { l: 50, r: 50, t: 50, b: 150 }
            };
        }
    } else {
        // Dot plot
        const sizeRef = Math.max(...geneCounts) / 40;
        if (orientation === 'horizontal') {
            trace = {
                type: 'scatter',
                mode: 'markers',
                y: labels,
                x: values,
                marker: {
                    size: geneCounts,
                    sizeref: sizeRef,
                    sizemin: 5,
                    color: values,
                    colorscale: colorPalette,
                    colorbar: { title: getMetricLabel(metric) }
                },
                text: sortedData.map(t => `${t.term_name}<br>Genes: ${t.observed_genes || 'N/A'}`),
                hovertemplate: '%{text}<br>Value: %{x:.3f}<extra></extra>'
            };
            layout = {
                xaxis: { title: getMetricLabel(metric) },
                yaxis: { automargin: true },
                margin: { l: 250, r: 100, t: 50, b: 50 }
            };
        } else {
            trace = {
                type: 'scatter',
                mode: 'markers',
                x: labels,
                y: values,
                marker: {
                    size: geneCounts,
                    sizeref: sizeRef,
                    sizemin: 5,
                    color: values,
                    colorscale: colorPalette,
                    colorbar: { title: getMetricLabel(metric) }
                },
                text: sortedData.map(t => `${t.term_name}<br>Genes: ${t.observed_genes || 'N/A'}`),
                hovertemplate: '%{text}<br>Value: %{y:.3f}<extra></extra>'
            };
            layout = {
                yaxis: { title: getMetricLabel(metric) },
                xaxis: { tickangle: -45, automargin: true },
                margin: { l: 50, r: 100, t: 50, b: 150 }
            };
        }
    }

    layout.width = width;
    layout.height = height;
    layout.font = { size: fontSize };
    layout.showlegend = false;

    Plotly.newPlot('plotContainer', [trace], layout, { responsive: true });
    document.getElementById('plotContainer').classList.add('has-plot');

    // Enable export buttons
    $('.export-btn').prop('disabled', false);
}

// Get metric value for a term
function getMetricValue(term, metric) {
    switch (metric) {
        case 'neglog_fdr':
            return -Math.log10(Math.max(term.binom_fdr || term.hyper_fdr || 1e-300, 1e-300));
        case 'neglog_p':
            return -Math.log10(Math.max(term.binom_p || term.hyper_p || 1e-300, 1e-300));
        case 'fold':
            return term.binom_fold_enrichment || term.hyper_fold_enrichment || 0;
        default:
            return 0;
    }
}

// Get metric label
function getMetricLabel(metric) {
    switch (metric) {
        case 'neglog_fdr': return '-log₁₀(FDR)';
        case 'neglog_p': return '-log₁₀(P-value)';
        case 'fold': return 'Fold Enrichment';
        default: return metric;
    }
}

// Export functions
function exportSVG() {
    Plotly.downloadImage('plotContainer', { format: 'svg', filename: 'enrichment_plot' });
}

function exportPNG() {
    Plotly.downloadImage('plotContainer', { format: 'png', scale: 2, filename: 'enrichment_plot' });
}

function exportSelectedTSV() {
    const data = getSelectedTerms();
    downloadData(data, 'selected_terms.tsv', '\\t');
}

function exportFilteredCSV() {
    const data = getFilteredTerms();
    downloadData(data, 'filtered_results.csv', ',');
}

function downloadData(data, filename, separator) {
    if (data.length === 0) {
        alert('No data to export.');
        return;
    }

    // Get all keys from first item
    const keys = Object.keys(data[0]).filter(k => k !== 'category');
    const header = keys.join(separator);
    const rows = data.map(d => keys.map(k => {
        const val = d[k];
        if (val === null || val === undefined) return '';
        if (typeof val === 'string' && (val.includes(separator) || val.includes('"') || val.includes('\\n'))) {
            return '"' + val.replace(/"/g, '""') + '"';
        }
        return val;
    }).join(separator));

    const content = header + '\\n' + rows.join('\\n');
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Select/deselect all visible
function selectAllVisible() {
    // Only select from visible accordion sections
    document.querySelectorAll('.accordion-item').forEach(item => {
        // Skip hidden accordion sections
        if (item.style.display === 'none') return;

        const category = item.dataset.category;
        const table = tables[category];
        if (!table) return;

        // Only get rows that pass current filters
        table.rows({ filter: 'applied' }).data().each(function(row) {
            selectedTerms.add(row.term_id);
        });
    });

    // Update checkboxes - only check visible ones
    $('.term-select:visible').each(function() {
        const termId = $(this).data('term-id');
        this.checked = selectedTerms.has(termId);
    });

    // Also update checkboxes that might be on other pages
    $('.term-select').each(function() {
        const termId = $(this).data('term-id');
        this.checked = selectedTerms.has(termId);
    });

    updateSelectionCount();
}

function deselectAll() {
    selectedTerms.clear();
    $('.term-select').prop('checked', false);
    updateSelectionCount();
}

// Utility functions
function formatScientific(num) {
    if (num === null || num === undefined) return '-';
    if (typeof num !== 'number') num = parseFloat(num);
    if (isNaN(num)) return '-';
    if (num === 0) return '0';
    if (num >= 0.01 && num < 1000) return num.toFixed(4);
    return num.toExponential(2);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateLabel(text, maxLen) {
    if (text.length <= maxLen) return text;
    return text.substring(0, maxLen - 3) + '...';
}
"""

# Main HTML template
REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- DataTables CSS -->
    <link href="https://cdn.datatables.net/1.13.8/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/select/1.7.0/css/select.bootstrap5.min.css" rel="stylesheet">

    <style>
{custom_css}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="report-header">
        <div class="container-fluid">
            <h1>{title}</h1>
            <div class="subtitle">Generated by pyGREAT</div>
        </div>
    </div>

    <div class="container-fluid">
        <!-- Summary Cards -->
{summary_html}

        <!-- Top Terms -->
{top_terms_html}

        <!-- Filters Bar -->
{filters_html}

        <!-- Ontology Sections (Accordion) -->
{accordion_html}

        <!-- Plot Builder -->
{plot_builder_html}
    </div>

    <!-- Term Detail Modal -->
{modal_html}

    <!-- Footer -->
    <div class="report-footer">
        This report is generated by <a href="https://github.com/khan-lab/pyGREAT" target="_blank">pyGREAT (version xxx)</a> on DATE.
    </div>

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.8/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.8/js/dataTables.bootstrap5.min.js"></script>
    <script src="https://cdn.datatables.net/select/1.7.0/js/dataTables.select.min.js"></script>
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>

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
