// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const compareBtn = document.getElementById('compareBtn');

// Tab functionality
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

// Global variables
let currentResults = null;
let isComparisonMode = false;

// File upload handling
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validate file type
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv') && !file.name.toLowerCase().endsWith('.xlsx')) {
        alert('Vui lòng chọn file CSV hoặc XLSX');
        return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
        alert('File quá lớn. Vui lòng chọn file nhỏ hơn 50MB');
        return;
    }

    // Update file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;

    // Show file info
    fileName.textContent = file.name;
    fileSize.textContent = `(${formatFileSize(file.size)})`;
    fileInfo.classList.remove('hidden');

    // Enable submit button
    submitBtn.disabled = false;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Tab switching
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Update buttons
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });

    // Update content
    tabContents.forEach(content => {
        content.classList.remove('active');
        if (content.id === tabName + 'Tab') {
            content.classList.add('active');
        }
    });
}

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!fileInput.files[0]) {
        alert('Vui lòng chọn file để tải lên');
        return;
    }

    // Validate thresholds
    const supportThreshold = parseFloat(document.querySelector('input[name="support_threshold"]').value);
    const confidenceThreshold = parseFloat(document.querySelector('input[name="confidence_threshold"]').value);

    if (isNaN(supportThreshold) || supportThreshold <= 0 || supportThreshold > 1) {
        alert('Support Threshold phải là số từ 0.01 đến 1.0');
        return;
    }

    if (isNaN(confidenceThreshold) || confidenceThreshold <= 0 || confidenceThreshold > 1) {
        alert('Confidence Threshold phải là số từ 0.01 đến 1.0');
        return;
    }

    // Check file size before upload
    const fileInput = document.getElementById('file');
    const file = fileInput.files[0];
    if (file) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        console.log(`File size: ${fileSizeMB} MB`);

        if (file.size > 100 * 1024 * 1024) { // 100MB
            alert(`File quá lớn (${fileSizeMB} MB). Vui lòng chọn file nhỏ hơn 100MB.`);
            return;
        }
    }

    // Show progress
    showProgress();

    // Prepare form data
    const formData = new FormData(uploadForm);

    try {
        // Simulate progress updates
        updateProgress(20, 'Đang tải file lên server...');

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        updateProgress(60, 'Đang xử lý dữ liệu...');

        // Check if response is ok first
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Server error response:', errorText);

            if (response.status === 413) {
                throw new Error('File quá lớn! Vui lòng chọn file nhỏ hơn 50MB.');
            }

            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        // Try to parse JSON with better error handling
        let result;
        try {
            const responseText = await response.text();
            console.log('Raw response:', responseText.substring(0, 500) + '...');
            result = JSON.parse(responseText);
        } catch (jsonError) {
            console.error('JSON parsing error:', jsonError);
            console.error('Response was not valid JSON');
            throw new Error('Server trả về dữ liệu không hợp lệ (không phải JSON)');
        }

        console.log("data tra ra " ,result)

        if (!response.ok) {
            throw new Error(result.error || 'Có lỗi xảy ra');
        }

        updateProgress(100, 'Hoàn thành!');

        // Show results after a short delay
        setTimeout(() => {
            hideProgress();
            showResults(result);
        }, 1000);

    } catch (error) {
        hideProgress();
        alert('Lỗi: ' + error.message);
    }
});

function showProgress() {
    progressSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    submitBtn.disabled = true;
}

function updateProgress(percent, text) {
    progressBar.style.width = percent + '%';
    progressText.textContent = text;
}

function hideProgress() {
    progressSection.classList.add('hidden');
    submitBtn.disabled = false;
}

function showResults(data) {
    // Store current results
    currentResults = data;
    isComparisonMode = false;

    // Show results section and compare button
    resultsSection.classList.remove('hidden');
    compareBtn.classList.remove('hidden');

    // Populate summary cards
    populateSummaryCards(data);

    // Populate algorithm steps
    document.getElementById('algorithmSteps').textContent = data.results.steps;

    // Populate itemsets
    populateItemsets(data.results.frequent_itemsets);

    // Populate rules
    populateRules(data.results.association_rules);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function populateSummaryCards(data) {
    const summaryCards = document.getElementById('summaryCards');
    summaryCards.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-center">
                <i class="fas fa-database text-blue-600 text-2xl mr-3"></i>
                <div>
                    <div class="text-2xl font-bold text-blue-800">${data.data_info.total_transactions}</div>
                    <div class="text-sm text-blue-600">Giao dịch</div>
                </div>
            </div>
        </div>
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-center">
                <i class="fas fa-cubes text-green-600 text-2xl mr-3"></i>
                <div>
                    <div class="text-2xl font-bold text-green-800">${data.results.frequent_itemsets.length}</div>
                    <div class="text-sm text-green-600">Tập phổ biến</div>
                </div>
            </div>
        </div>
        <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div class="flex items-center">
                <i class="fas fa-arrow-right text-purple-600 text-2xl mr-3"></i>
                <div>
                    <div class="text-2xl font-bold text-purple-800">${data.results.association_rules.length}</div>
                    <div class="text-sm text-purple-600">Luật kết hợp</div>
                </div>
            </div>
        </div>
        <div class="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <div class="flex items-center">
                <i class="fas fa-clock text-orange-600 text-2xl mr-3"></i>
                <div>
                    <div class="text-2xl font-bold text-orange-800">${data.results.execution_time}s</div>
                    <div class="text-sm text-orange-600">Thời gian chạy</div>
                </div>
            </div>
        </div>
    `;
}

function populateItemsets(itemsets) {
    const itemsetsList = document.getElementById('itemsetsList');

    if (itemsets.length === 0) {
        itemsetsList.innerHTML = '<p class="text-gray-500 text-center py-8">Không tìm thấy tập phổ biến nào với ngưỡng đã cho.</p>';
        return;
    }

    itemsetsList.innerHTML = itemsets.map((item, index) => `
        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
            <div class="flex items-center justify-between">
                <div class="flex items-center">
                    <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full mr-3">
                        ${index + 1}
                    </span>
                    <div>
                        <div class="font-medium text-gray-800">
                            {${item.itemset.join(', ')}}
                        </div>
                        ${item.support !== 'N/A' ? `<div class="text-sm text-gray-600">Support: ${item.support}</div>` : ''}
                    </div>
                </div>
                <div class="text-sm text-gray-500">
                    ${item.itemset.length} item${item.itemset.length > 1 ? 's' : ''}
                </div>
            </div>
        </div>
    `).join('');
}

function populateRules(rules) {
    const rulesList = document.getElementById('rulesList');

    if (rules.length === 0) {
        rulesList.innerHTML = '<p class="text-gray-500 text-center py-8">Không tìm thấy luật kết hợp nào với ngưỡng đã cho.</p>';
        return;
    }

    // Sắp xếp theo confidence từ cao xuống thấp (đề phòng)
    const sortedRules = [...rules].sort((a, b) => b.confidence - a.confidence);

    rulesList.innerHTML = `
        <div class="mb-4 text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
            <i class="fas fa-sort-amount-down mr-2"></i>
            <strong>Đã sắp xếp theo độ tin cậy từ cao xuống thấp</strong> (${sortedRules.length} luật kết hợp)
        </div>
        ${sortedRules.map((rule, index) => `
            <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div class="flex items-start justify-between">
                    <div class="flex items-start">
                        <span class="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded-full mr-3 mt-1">
                            #${index + 1}
                        </span>
                        <div class="flex-1">
                            <div class="font-medium text-gray-800 mb-2">
                                ${rule.description}
                            </div>
                            <div class="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                                <strong>Mã sản phẩm:</strong> {${rule.antecedent.join(', ')}} → {${rule.consequent.join(', ')}}
                            </div>
                        </div>
                    </div>
                    <div class="text-right ml-4">
                        <div class="text-lg font-bold text-purple-600">${(rule.confidence * 100).toFixed(1)}%</div>
                        <div class="text-xs text-gray-500">Độ tin cậy</div>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
}

// Compare button functionality
compareBtn.addEventListener('click', async () => {
    if (isComparisonMode) {
        // Return to original results
        showOriginalResults();
        return;
    }

    try {
        compareBtn.disabled = true;
        compareBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Đang so sánh...';

        const response = await fetch('/compare');
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Có lỗi xảy ra khi so sánh');
        }

        // Switch to comparison mode
        isComparisonMode = true;
        showComparison(currentResults, result.library_results);

        compareBtn.innerHTML = '<i class="fas fa-arrow-left mr-2"></i>Quay lại kết quả gốc';
        compareBtn.disabled = false;

    } catch (error) {
        alert('Lỗi: ' + error.message);
        compareBtn.innerHTML = '<i class="fas fa-balance-scale mr-2"></i>So sánh với thư viện';
        compareBtn.disabled = false;
    }
});

function showOriginalResults() {
    isComparisonMode = false;

    // Restore original header
    const header = document.querySelector('#resultsSection h2');
    header.innerHTML = '<i class="fas fa-chart-bar mr-2 text-green-600"></i>Kết quả phân tích';

    // Restore original summary
    populateSummaryCards(currentResults);

    // Show steps tab again
    const stepsTab = document.querySelector('[data-tab="steps"]');
    stepsTab.style.display = 'block';

    // Restore original data
    populateItemsets(currentResults.results.frequent_itemsets);
    populateRules(currentResults.results.association_rules);

    // Update button
    compareBtn.innerHTML = '<i class="fas fa-balance-scale mr-2"></i>So sánh với thư viện';
}

function showComparison(customResults, libraryResults) {
    // Update header
    const header = document.querySelector('#resultsSection h2');
    header.innerHTML = '<i class="fas fa-balance-scale mr-2 text-blue-600"></i>So sánh kết quả: Thuật toán tự viết vs Thư viện';

    // Update summary cards for comparison
    populateComparisonSummary(customResults, libraryResults);

    // Update tabs for comparison
    updateTabsForComparison();

    // Populate comparison data
    populateItemsetsComparison(customResults.results.frequent_itemsets, libraryResults.frequent_itemsets);
    populateRulesComparison(customResults.results.association_rules, libraryResults.association_rules);
}

function populateComparisonSummary(customResults, libraryResults) {
    const summaryCards = document.getElementById('summaryCards');
    summaryCards.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="text-center">
                <div class="text-lg font-bold text-blue-800">Thuật toán tự viết</div>
                <div class="text-sm text-blue-600 mt-2">
                    <div>Itemsets: ${customResults.results.frequent_itemsets.length}</div>
                    <div>Rules: ${customResults.results.association_rules.length}</div>
                    <div>Thời gian: ${customResults.results.execution_time}s</div>
                </div>
            </div>
        </div>
        <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="text-center">
                <div class="text-lg font-bold text-green-800">Thư viện (mlxtend)</div>
                <div class="text-sm text-green-600 mt-2">
                    <div>Itemsets: ${libraryResults.frequent_itemsets.length}</div>
                    <div>Rules: ${libraryResults.association_rules.length}</div>
                    <div>Thời gian: ${libraryResults.execution_time.toFixed(4)}s</div>
                </div>
            </div>
        </div>
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="text-center">
                <div class="text-lg font-bold text-yellow-800">Chênh lệch</div>
                <div class="text-sm text-yellow-600 mt-2">
                    <div>Itemsets: ${Math.abs(customResults.results.frequent_itemsets.length - libraryResults.frequent_itemsets.length)}</div>
                    <div>Rules: ${Math.abs(customResults.results.association_rules.length - libraryResults.association_rules.length)}</div>
                    <div>Thời gian: ${Math.abs(customResults.results.execution_time - libraryResults.execution_time).toFixed(4)}s</div>
                </div>
            </div>
        </div>
        <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div class="text-center">
                <div class="text-lg font-bold text-purple-800">Hiệu suất</div>
                <div class="text-sm text-purple-600 mt-2">
                    <div>${customResults.results.execution_time < libraryResults.execution_time ? 'Tự viết nhanh hơn' : 'Thư viện nhanh hơn'}</div>
                    <div>Tỷ lệ: ${(Math.max(customResults.results.execution_time, libraryResults.execution_time) / Math.min(customResults.results.execution_time, libraryResults.execution_time)).toFixed(2)}x</div>
                </div>
            </div>
        </div>
    `;
}

function updateTabsForComparison() {
    // Hide steps tab in comparison mode
    const stepsTab = document.querySelector('[data-tab="steps"]');
    stepsTab.style.display = 'none';

    // Switch to itemsets tab
    switchTab('itemsets');
}

function populateItemsetsComparison(customItemsets, libraryItemsets) {
    const itemsetsList = document.getElementById('itemsetsList');

    itemsetsList.innerHTML = `
        <div class="grid md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-lg font-semibold mb-4 text-blue-600">Thuật toán tự viết (${customItemsets.length})</h3>
                <div class="space-y-2 max-h-96 overflow-y-auto">
                    ${customItemsets.map((item, index) => `
                        <div class="border border-blue-200 rounded p-3 text-sm">
                            <div class="font-medium">{${item.itemset.join(', ')}}</div>
                            ${item.support !== 'N/A' ? `<div class="text-gray-600">Support: ${item.support}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
            <div>
                <h3 class="text-lg font-semibold mb-4 text-green-600">Thư viện mlxtend (${libraryItemsets.length})</h3>
                <div class="space-y-2 max-h-96 overflow-y-auto">
                    ${libraryItemsets.map((item, index) => `
                        <div class="border border-green-200 rounded p-3 text-sm">
                            <div class="font-medium">{${item.itemset.join(', ')}}</div>
                            <div class="text-gray-600">Support: ${item.support}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function populateRulesComparison(customRules, libraryRules) {
    const rulesList = document.getElementById('rulesList');

    // Sắp xếp cả 2 danh sách theo confidence từ cao xuống thấp
    const sortedCustomRules = [...customRules].sort((a, b) => b.confidence - a.confidence);
    const sortedLibraryRules = [...libraryRules].sort((a, b) => b.confidence - a.confidence);

    rulesList.innerHTML = `
        <div class="mb-4 text-sm text-gray-600 bg-yellow-50 p-3 rounded-lg">
            <i class="fas fa-sort-amount-down mr-2"></i>
            <strong>Cả 2 danh sách đã được sắp xếp theo độ tin cậy từ cao xuống thấp</strong>
        </div>
        <div class="grid md:grid-cols-2 gap-6">
            <div>
                <h3 class="text-lg font-semibold mb-4 text-blue-600">
                    <i class="fas fa-code mr-2"></i>Thuật toán tự viết (${sortedCustomRules.length})
                </h3>
                <div class="space-y-3 max-h-96 overflow-y-auto">
                    ${sortedCustomRules.map((rule, index) => `
                        <div class="border border-blue-200 rounded p-3 text-sm">
                            <div class="flex items-start justify-between mb-2">
                                <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                                    #${index + 1}
                                </span>
                                <span class="text-blue-600 font-bold">
                                    ${(rule.confidence * 100).toFixed(1)}%
                                </span>
                            </div>
                            <div class="font-medium mb-1">${rule.description}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div>
                <h3 class="text-lg font-semibold mb-4 text-green-600">
                    <i class="fas fa-book mr-2"></i>Thư viện mlxtend (${sortedLibraryRules.length})
                </h3>
                <div class="space-y-3 max-h-96 overflow-y-auto">
                    ${sortedLibraryRules.map((rule, index) => `
                        <div class="border border-green-200 rounded p-3 text-sm">
                            <div class="flex items-start justify-between mb-2">
                                <span class="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">
                                    #${index + 1}
                                </span>
                                <span class="text-green-600 font-bold">
                                    ${(rule.confidence * 100).toFixed(1)}%
                                </span>
                            </div>
                            <div class="font-medium mb-1">${rule.description}</div>
                            <div class="text-xs text-gray-500">
                                Support: ${(rule.support * 100).toFixed(2)}% |
                                Lift: ${rule.lift.toFixed(2)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}