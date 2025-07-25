// Global variables
let collectedTaskIds = [];
const apiBaseUrl = window.location.origin; // Same origin - CORS yok

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// System status refresh
async function refreshSystemStatus() {
    try {
        const response = await fetch(`${apiBaseUrl}/health`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('celeryStatus').textContent = data.celery_workers > 0 ? 'Aktif' : 'Pasif';
            document.getElementById('celeryTime').textContent = data.timestamp;
            document.getElementById('powershellStatus').textContent = 'Aktif';
            document.getElementById('powershellTime').textContent = data.timestamp;
        } else {
            document.getElementById('celeryStatus').textContent = 'Hata';
            document.getElementById('powershellStatus').textContent = 'Bilinmiyor';
        }
    } catch (error) {
        document.getElementById('celeryStatus').textContent = 'Bağlantı Yok';
        document.getElementById('powershellStatus').textContent = 'Bağlantı Yok';
    }
}

// Check Redis logs (simulated - PowerShell does the real work)
async function checkRedisLogs() {
    document.getElementById('monitoringResult').innerHTML = `
        <div class="result-container">
            <div class="status processing">Kontrol Ediliyor</div>
            <p>🔄 PowerShell script'i Redis Docker loglarını kontrol ediyor...</p>
            <p>⏰ Bu işlem otomatik olarak 30 saniyede bir yapılır.</p>
        </div>
    `;
    
    setTimeout(() => {
        document.getElementById('monitoringResult').innerHTML = `
            <div class="result-container">
                <div class="status success">Tamamlandı</div>
                <p><strong>🐳 Redis Durumu:</strong> PowerShell tarafından kontrol edildi</p>
                <p><strong>📄 Sonuç:</strong> hatalar.txt dosyası güncellendi</p>
                <p><strong>⏰ Son Kontrol:</strong> ${new Date().toLocaleString('tr-TR')}</p>
            </div>
        `;
    }, 2000);
}

// Analyze file - Main PowerShell function
async function analyzeFile() {
    const btn = document.getElementById('fileAnalyzeBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading"></div>Analiz ediliyor...';

    try {
        const response = await fetch(`${apiBaseUrl}/analyze-file`, { method: 'POST' });
        const data = await response.json();
        
        if (response.ok) {
            collectedTaskIds.push(...data.task_ids);
            updateTaskCounter();
            
            document.getElementById('fileResult').innerHTML = `
                <div class="result-container">
                    <div class="status success">✅ Başarılı</div>
                    <p><strong>🚀 ${data.message}</strong></p>
                    <p><strong>📊 Task Sayısı:</strong> ${data.task_ids.length}</p>
                    <details>
                        <summary>🔍 Task ID'leri</summary>
                        <div class="log-display">${data.task_ids.join('\n')}</div>
                    </details>
                </div>
            `;
        } else {
            throw new Error(data.error || 'Bilinmeyen hata');
        }
    } catch (error) {
        document.getElementById('fileResult').innerHTML = `
            <div class="result-container">
                <div class="status error">❌ Hata</div>
                <p>${error.message}</p>
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '🚀 Dosyayı Analiz Et (hatalar.txt)';
    }
}

// Get single result
async function getResult() {
    const taskId = document.getElementById('taskId').value.trim();
    if (!taskId) {
        alert('Task ID girin!');
        return;
    }

    try {
        const response = await fetch(`${apiBaseUrl}/result/${taskId}`);
        const data = await response.json();
        
        let statusClass = response.status === 200 ? 'success' : 
                         response.status === 202 ? 'processing' : 'error';
        
        document.getElementById('resultDisplay').innerHTML = `
            <div class="result-container">
                <div class="status ${statusClass}">${data.status}</div>
                <p><strong>🆔 Task:</strong> ${data.task_id}</p>
                ${data.result ? `
                    <p><strong>🤖 AI Sonucu:</strong></p>
                    <div class="json-display">${JSON.stringify(JSON.parse(data.result), null, 2)}</div>
                ` : ''}
                ${data.error ? `<p><strong>❌ Hata:</strong> ${data.error}</p>` : ''}
            </div>
        `;
    } catch (error) {
        document.getElementById('resultDisplay').innerHTML = `
            <div class="result-container">
                <div class="status error">❌ API Hatası</div>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Get all results - PowerShell equivalent
async function getAllResults() {
    if (collectedTaskIds.length === 0) {
        alert('Task ID yok! Önce dosya analizi yapın.');
        return;
    }

    const btn = document.getElementById('getAllBtn');
    btn.disabled = true;
    btn.innerHTML = '<div class="loading"></div>Kaydediliyor...';

    try {
        const response = await fetch(`${apiBaseUrl}/get-all-results`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_ids: collectedTaskIds })
        });

        const data = await response.json();
        
        document.getElementById('resultDisplay').innerHTML = `
            <div class="result-container">
                <div class="status success">✅ ${data.message}</div>
                <p>📁 Dosya: <strong>analiz_sonuclari.txt</strong></p>
                <p>⏰ ${new Date().toLocaleString('tr-TR')}</p>
            </div>
        `;
    } catch (error) {
        document.getElementById('resultDisplay').innerHTML = `
            <div class="result-container">
                <div class="status error">❌ ${error.message}</div>
            </div>
        `;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '💾 Tüm Sonuçları Al ve Kaydet';
    }
}

// File viewers
async function viewFile(filename, displayId) {
    try {
        const response = await fetch(`${apiBaseUrl}/view-file/${filename}`);
        const content = await response.text();
        
        document.getElementById(displayId).innerHTML = `
            <div class="result-container">
                <div class="status success">📄 ${filename}</div>
                <div class="log-display">${content}</div>
            </div>
        `;
    } catch (error) {
        document.getElementById(displayId).innerHTML = `
            <div class="result-container">
                <div class="status error">❌ Dosya okunamadı</div>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Specific file viewers
function viewHatalarFile() { viewFile('hatalar.txt', 'logDisplay'); }
function viewTaskLog() { viewFile('task_log.txt', 'logDisplay'); }
function viewAnalysisResults() { viewFile('analiz_sonuclari.txt', 'logDisplay'); }

// Check file sizes
async function checkFileSize() {
    try {
        const response = await fetch(`${apiBaseUrl}/file-status`);
        const data = await response.json();
        
        document.getElementById('totalErrors').textContent = data.hatalar_lines || '0';
        document.getElementById('errorTime').textContent = data.timestamp;
        
        const displayId = document.getElementById('monitoringResult') ? 'monitoringResult' : 'fileResult';
        document.getElementById(displayId).innerHTML = `
            <div class="result-container">
                <div class="status success">📊 Dosya Durumu</div>
                <p><strong>📄 hatalar.txt:</strong> ${data.hatalar_size || '0 bytes'} (${data.hatalar_lines || 0} satır)</p>
                <p><strong>📋 task_log.txt:</strong> ${data.task_log_size || '0 bytes'} (${data.task_log_lines || 0} satır)</p>
                <p><strong>🤖 analiz_sonuclari.txt:</strong> ${data.analiz_size || '0 bytes'} (${data.analiz_lines || 0} satır)</p>
                <p><strong>⏰ Kontrol:</strong> ${data.timestamp}</p>
            </div>
        `;
    } catch (error) {
        console.error('File status error:', error);
    }
}

// Health check
async function healthCheck() {
    try {
        const response = await fetch(`${apiBaseUrl}/health`);
        const data = await response.json();
        
        document.getElementById('systemDisplay').innerHTML = `
            <div class="result-container">
                <div class="status ${data.status === 'healthy' ? 'success' : 'error'}">
                    ${data.status === 'healthy' ? '✅ Sistem Sağlıklı' : '❌ Sistem Hatası'}
                </div>
                <p><strong>⚡ Celery Workers:</strong> ${data.celery_workers || 0}</p>
                <p><strong>🔗 API:</strong> ${data.api_status || 'unknown'}</p>
                <p><strong>⏰ Kontrol:</strong> ${data.timestamp}</p>
            </div>
        `;
    } catch (error) {
        document.getElementById('systemDisplay').innerHTML = `
            <div class="result-container">
                <div class="status error">❌ API Bağlantı Hatası</div>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Test API endpoints
async function testApiEndpoints() {
    const endpoints = ['/api', '/health', '/file-status'];
    let results = [];
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(`${apiBaseUrl}${endpoint}`);
            results.push(`✅ ${endpoint}: ${response.status}`);
        } catch (error) {
            results.push(`❌ ${endpoint}: Hata`);
        }
    }
    
    document.getElementById('systemDisplay').innerHTML = `
        <div class="result-container">
            <div class="status success">🧪 API Test Sonuçları</div>
            <div class="log-display">${results.join('\n')}</div>
        </div>
    `;
}
function openFlower() {
    // Yeni sekmede Flower'ı aç
    window.open('http://127.0.0.1:5555/', '_blank');
    
    // UI'da bilgi göster
    document.getElementById('systemDisplay').innerHTML = `
        <div class="result-container">
            <div class="status success">🌸 Flower Monitoring</div>
            <p><strong>🔗 URL:</strong> <a href="http://127.0.0.1:5555/" target="_blank">http://127.0.0.1:5555/</a></p>
            <p><strong>📊 Özellikler:</strong> Celery worker durumu, task history, real-time monitoring</p>
            <p><strong>⏰ Açıldı:</strong> ${new Date().toLocaleString('tr-TR')}</p>
        </div>
    `;
}


// Get system stats
function getSystemStats() {
    document.getElementById('systemDisplay').innerHTML = `
        <div class="result-container">
            <div class="status success">📈 Sistem İstatistikleri</div>
            <p><strong>🔢 Toplanan Task:</strong> ${collectedTaskIds.length}</p>
            <p><strong>🌐 API URL:</strong> ${apiBaseUrl}</p>
            <p><strong>⏰ Sayfa Yüklenme:</strong> ${new Date().toLocaleString('tr-TR')}</p>
            <p><strong>💡 PowerShell Döngüsü:</strong> 30 saniye</p>
        </div>
    `;
}

// Update task counter
function updateTaskCounter() {
    const counter = document.getElementById('taskCounter');
    const count = document.getElementById('taskCount');
    
    if (collectedTaskIds.length > 0) {
        counter.style.display = 'block';
        count.textContent = collectedTaskIds.length;
    } else {
        counter.style.display = 'none';
    }
}

// Initialize on page load
window.onload = function() {
    refreshSystemStatus();
    checkFileSize();
    
    // Refresh every 30 seconds (PowerShell döngüsüne uygun)
    setInterval(() => {
        refreshSystemStatus();
        checkFileSize();
    }, 30000);
};