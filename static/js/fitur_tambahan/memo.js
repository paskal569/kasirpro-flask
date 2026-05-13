   // ============================================
        let memos = [];
        let editId = null;
        
        // Load memos from localStorage
        function loadMemos() {
            const storedMemos = localStorage.getItem('memos');
            if (storedMemos) {
                memos = JSON.parse(storedMemos);
            } else {
                // Sample data for demo
                memos = [
                    {
                        id: Date.now(),
                        title: 'Meeting dengan Tim',
                        content: 'Diskusi tentang project Q2 2026\n- Review progress\n- Planning next sprint\n- Resource allocation',
                        date: new Date().toISOString()
                    },
                    {
                        id: Date.now() + 1,
                        title: 'Ide Aplikasi Baru',
                        content: 'Buat aplikasi catatan dengan fitur reminder dan kolaborasi real-time menggunakan WebSocket',
                        date: new Date().toISOString()
                    }
                ];
                saveToLocalStorage();
            }
            renderMemos();
        }
        
        // Save to localStorage
        function saveToLocalStorage() {
            localStorage.setItem('memos', JSON.stringify(memos));
        }
        
        // Render memos to UI
        function renderMemos() {
            const memoListContainer = document.getElementById('memoList');
            
            if (memos.length === 0) {
                memoListContainer.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-sticky-note"></i>
                        <p>Belum ada memo. Yuk buat memo pertama Anda!</p>
                    </div>
                `;
                return;
            }
            
            memoListContainer.innerHTML = memos.map(memo => `
                <div class="memo-item" onclick="viewMemo(${memo.id})">
                    <div class="memo-item-title">
                        <i class="fas fa-file-alt"></i> ${escapeHtml(memo.title)}
                    </div>
                    <div class="memo-item-content">
                        ${escapeHtml(memo.content.substring(0, 150))}${memo.content.length > 150 ? '...' : ''}
                    </div>
                    <div class="memo-item-date">
                        <span><i class="far fa-calendar-alt"></i> ${formatDate(memo.date)}</span>
                        <span class="delete-memo" onclick="event.stopPropagation(); deleteMemo(${memo.id})">
                            <i class="fas fa-trash-alt"></i>
                        </span>
                    </div>
                </div>
            `).join('');
        }
        
        // Save or update memo
        function saveMemo() {
            const title = document.getElementById('memoTitle').value.trim();
            const content = document.getElementById('memoContent').value.trim();
            
            if (!title) {
                showToast('Judul memo tidak boleh kosong!', 'warning');
                return;
            }
            
            if (!content) {
                showToast('Konten memo tidak boleh kosong!', 'warning');
                return;
            }
            
            if (editId) {
                // Update existing memo
                const index = memos.findIndex(m => m.id === editId);
                if (index !== -1) {
                    memos[index] = {
                        ...memos[index],
                        title: title,
                        content: content,
                        updatedAt: new Date().toISOString()
                    };
                    showToast('Memo berhasil diperbarui!', 'success');
                }
                editId = null;
            } else {
                // Create new memo
                const newMemo = {
                    id: Date.now(),
                    title: title,
                    content: content,
                    date: new Date().toISOString()
                };
                memos.unshift(newMemo); // Add to beginning
                showToast('Memo berhasil ditambahkan!', 'success');
            }
            
            saveToLocalStorage();
            renderMemos();
            hideAddMemoForm();
            clearForm();
        }
        
        // Delete memo
        function deleteMemo(id) {
            if (confirm('Apakah Anda yakin ingin menghapus memo ini?')) {
                memos = memos.filter(memo => memo.id !== id);
                saveToLocalStorage();
                renderMemos();
                showToast('Memo berhasil dihapus!', 'success');
            }
        }
        
        // View memo (for editing)
        function viewMemo(id) {
            const memo = memos.find(m => m.id === id);
            if (memo) {
                document.getElementById('memoTitle').value = memo.title;
                document.getElementById('memoContent').value = memo.content;
                editId = id;
                showAddMemoForm();
                showToast('Klik simpan untuk mengupdate memo', 'info');
            }
        }
        
        // Show add memo form
        function showAddMemoForm() {
            const form = document.getElementById('addMemoForm');
            form.classList.remove('hidden');
            form.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Hide add memo form
        function hideAddMemoForm() {
            const form = document.getElementById('addMemoForm');
            form.classList.add('hidden');
            clearForm();
            editId = null;
        }
        
        // Clear form inputs
        function clearForm() {
            document.getElementById('memoTitle').value = '';
            document.getElementById('memoContent').value = '';
        }
        
        // Navigation
        function navigateTo(page) {
            showToast(`Navigasi ke halaman ${page} (coming soon)`, 'info');
            // Update active tab styling
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.closest('.nav-btn').classList.add('active');
        }
        
        // Format date
        function formatDate(dateString) {
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 0) {
                return 'Hari ini';
            } else if (diffDays === 1) {
                return 'Kemarin';
            } else if (diffDays < 7) {
                return `${diffDays} hari lalu`;
            } else {
                return date.toLocaleDateString('id-ID', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric'
                });
            }
        }
        
        // Escape HTML to prevent XSS
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Show toast notification
        function showToast(message, type = 'info') {
            const toast = document.createElement('div');
            toast.className = 'toast-notification';
            
            const icons = {
                success: '✓',
                error: '✗',
                warning: '⚠',
                info: 'ℹ'
            };
            
            toast.innerHTML = `${icons[type] || 'ℹ'} ${message}`;
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 3000);
        }
        
        // ============================================
        // INITIALIZATION
        // ============================================
        loadMemos();
        
        // Keyboard shortcut: Ctrl+N to add new memo
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'n') {
                e.preventDefault();
                showAddMemoForm();
            }
        });
        
        // Export for global access
        window.navigateTo = navigateTo;
        window.showAddMemoForm = showAddMemoForm;
        window.hideAddMemoForm = hideAddMemoForm;
        window.saveMemo = saveMemo;
        window.deleteMemo = deleteMemo;
        window.viewMemo = viewMemo;