/**
 * Stenographer WebApp - Chunked File Upload
 * Telegram WebApp integration with 10MB chunks support up to 2GB
 */

// Telegram WebApp initialization
const tg = window.Telegram.WebApp;
tg.expand();
tg.ready();

// Configuration
const CONFIG = {
    CHUNK_SIZE: 10 * 1024 * 1024, // 10MB chunks
    MAX_FILE_SIZE: 2 * 1024 * 1024 * 1024, // 2GB
    ALLOWED_TYPES: ['audio/', 'video/'],
    // Fallback для iOS (m4a, mp4 могут иметь некорректный MIME тип)
    ALLOWED_EXTENSIONS: ['.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.opus', '.mp4', '.mov', '.avi', '.mkv', '.webm'],
    API_BASE: window.location.origin
};

// State
let selectedFile = null;
let uploadId = null;
let totalChunks = 0;
let uploadedChunks = 0;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressPercent = document.getElementById('progressPercent');
const progressStatus = document.getElementById('progressStatus');
const statusChip = document.getElementById('statusChip');

console.log("🔍 DOM Elements check:", {
    dropZone: !!dropZone,
    fileInput: !!fileInput,
    uploadBtn: !!uploadBtn
});

// Initialize
init();

function init() {
    // Set main button
    tg.MainButton.setText('Загрузить файл');
    tg.MainButton.hide();

    // Event listeners
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        if (file) processFile(file);
    });

    uploadBtn.addEventListener('click', startUpload);
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) {
        console.warn("⚠️ No file selected");
        return;
    }
    console.log("📂 File selected:", file.name);
    processFile(file);
}

/**
 * Проверка расширения файла (для iOS fallback)
 */
function getFileExtension(filename) {
    const ext = filename.toLowerCase().slice(((filename.lastIndexOf(".") - 1) >>> 0) + 2);
    return ext ? `.${ext}` : '';
}

function isValidFile(file) {
    // 1. Проверка MIME типа (основной способ)
    const mimeValid = CONFIG.ALLOWED_TYPES.some(type => file.type.startsWith(type));
    
    // 2. Fallback: проверка расширения (для iOS где MIME тип может быть некорректным)
    const ext = getFileExtension(file.name);
    const extValid = CONFIG.ALLOWED_EXTENSIONS.includes(ext);
    
    return mimeValid || extValid;
}

function processFile(file) {
    console.log("📱 processFile START", file.name);

    // Early activation for debugging
    uploadBtn.disabled = false;
    console.log("🔓 Button enabled immediately");

    // Validate file type (MIME + extension fallback for iOS)
    if (!isValidFile(file)) {
        console.warn("❌ File rejected - invalid type");
        console.log("MIME valid:", CONFIG.ALLOWED_TYPES.some(t => file.type.startsWith(t)));
        console.log("Extension:", getFileExtension(file.name));
        tg.showAlert('❌ Поддерживаются только аудио и видео файлы\n\nMime: ' + file.type + '\nExt: ' + getFileExtension(file.name));
        uploadBtn.disabled = true;
        return;
    }

    // Validate file size
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        tg.showAlert('❌ Файл превышает лимит в 2GB');
        return;
    }

    selectedFile = file;

    // Update UI
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.add('active');
    uploadBtn.disabled = false;

    // Update status
    updateStatus('Готово к загрузке', 'pending');
}

function formatFileSize(bytes) {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;

    while (size >= 1024 && unitIndex < units.length - 1) {
        size /= 1024;
        unitIndex++;
    }

    return `${size.toFixed(2)} ${units[unitIndex]}`;
}

function updateStatus(text, status) {
    statusChip.textContent = text;
    statusChip.className = `status-chip status-${status}`;
    statusChip.classList.remove('hidden');
}

async function startUpload() {
    if (!selectedFile) return;

    try {
        uploadBtn.disabled = true;
        progressContainer.classList.add('active');

        // Calculate chunks
        totalChunks = Math.ceil(selectedFile.size / CONFIG.CHUNK_SIZE);
        uploadedChunks = 0;

        // Initialize upload session
        const initResponse = await fetch(`${CONFIG.API_BASE}/api/upload/init`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Telegram-Init-Data': tg.initData
            },
            body: JSON.stringify({
                filename: selectedFile.name,
                size: selectedFile.size,
                type: selectedFile.type,
                total_chunks: totalChunks
            })
        });

        if (!initResponse.ok) throw new Error('Failed to initialize upload');

        const initData = await initResponse.json();
        uploadId = initData.upload_id;

        updateStatus('Загрузка...', 'uploading');

        // Upload chunks
        for (let i = 0; i < totalChunks; i++) {
            const start = i * CONFIG.CHUNK_SIZE;
            const end = Math.min(start + CONFIG.CHUNK_SIZE, selectedFile.size);
            const chunk = selectedFile.slice(start, end);

            await uploadChunk(uploadId, i, chunk, totalChunks);

            uploadedChunks++;
            const percent = Math.round((uploadedChunks / totalChunks) * 100);
            updateProgress(percent, `Часть ${uploadedChunks} из ${totalChunks}`);
        }

        // Complete upload
        await completeUpload(uploadId);

        updateStatus('Обработка файла...', 'processing');
        tg.showAlert('✅ Файл успешно загружен! Бот начинает расшифровку...');

        // Notify bot
        tg.sendData(JSON.stringify({
            action: 'upload_complete',
            upload_id: uploadId,
            filename: selectedFile.name
        }));

    } catch (error) {
        console.error('Upload error:', error);
        updateStatus('Ошибка загрузки', 'error');
        tg.showAlert(`❌ Ошибка: ${error.message}`);
        uploadBtn.disabled = false;
    }
}

async function uploadChunk(uploadId, chunkIndex, chunk, totalChunks) {
    console.log(`📤 Uploading chunk ${chunkIndex}/${totalChunks}`);
    console.log(`📱 initData exists: ${!!tg.initData}`);
    console.log(`📱 initData length: ${tg.initData?.length || 0}`);

    const formData = new FormData();
    formData.append('upload_id', uploadId);
    formData.append('chunk_index', chunkIndex);
    formData.append('chunk_data', chunk);

    console.log(`📦 FormData keys:`, [...formData.keys()]);

    const response = await fetch(`${CONFIG.API_BASE}/api/upload/chunk`, {
        method: 'POST',
        headers: {
            'X-Telegram-Init-Data': tg.initData || ''
        },
        body: formData
    });

    console.log(`📥 Response: ${response.status} ${response.statusText}`);

    if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Chunk error response:`, errorText);
        throw new Error(`Chunk ${chunkIndex} upload failed: ${response.status}`);
    }

    return await response.json();
}

async function completeUpload(uploadId) {
    const response = await fetch(`${CONFIG.API_BASE}/api/upload/complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Telegram-Init-Data': tg.initData
        },
        body: JSON.stringify({ upload_id: uploadId })
    });

    if (!response.ok) {
        throw new Error('Failed to complete upload');
    }
}

function updateProgress(percent, status) {
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
    progressStatus.textContent = status;
}

// Auto-start processing after upload (handled by bot notification)
tg.onEvent('mainButtonClicked', () => {
    if (selectedFile) startUpload();
});