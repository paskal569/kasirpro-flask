
        // STATE MANAGEMENT
        // ============================================
        let currentTime = new Date();
        let timerInterval = null;
        let isOnline = true;
        
        // DOM Elements
        const timeDisplay = document.getElementById('currentTime');
        const dateDisplay = document.getElementById('currentDate');
        const hoursDisplay = document.getElementById('hoursDisplay');
        const minutesDisplay = document.getElementById('minutesDisplay');
        const secondsDisplay = document.getElementById('secondsDisplay');
        const connectionStatus = document.getElementById('connectionStatus');
        
        // ============================================
        // HELPER FUNCTIONS
        // ============================================
        
        /**
         * Format number with leading zero
         */
        function formatNumber(num) {
            return num.toString().padStart(2, '0');
        }
        
        /**
         * Get Indonesian day name
         */
        function getIndonesianDay(dayIndex) {
            const days = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
            return days[dayIndex];
        }
        
        /**
         * Get Indonesian month name
         */
        function getIndonesianMonth(monthIndex) {
            const months = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 
                           'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'];
            return months[monthIndex];
        }
        
        /**
         * Update all displays with current time
         */
        function updateDisplay() {
            const hours = currentTime.getHours();
            const minutes = currentTime.getMinutes();
            const seconds = currentTime.getSeconds();
            
            // Update main time display
            timeDisplay.textContent = `${formatNumber(hours)}:${formatNumber(minutes)}:${formatNumber(seconds)}`;
            
            // Update individual displays
            hoursDisplay.textContent = formatNumber(hours);
            minutesDisplay.textContent = formatNumber(minutes);
            secondsDisplay.textContent = formatNumber(seconds);
            
            // Update date display
            const day = getIndonesianDay(currentTime.getDay());
            const date = currentTime.getDate();
            const month = getIndonesianMonth(currentTime.getMonth());
            const year = currentTime.getFullYear();
            dateDisplay.textContent = `${day}, ${date} ${month} ${year}`;
        }
        
        /**
         * Update time (increment by 1 second)
         */
        function updateTime() {
            currentTime.setSeconds(currentTime.getSeconds() + 1);
            updateDisplay();
        }
        
        /**
         * Start the clock timer
         */
        function startClock() {
            if (timerInterval) {
                clearInterval(timerInterval);
            }
            timerInterval = setInterval(updateTime, 1000);
        }
        
        /**
         * Adjust specific time component
         */
        function adjustTime(component, delta) {
            switch(component) {
                case 'hours':
                    currentTime.setHours(currentTime.getHours() + delta);
                    break;
                case 'minutes':
                    currentTime.setMinutes(currentTime.getMinutes() + delta);
                    break;
                case 'seconds':
                    currentTime.setSeconds(currentTime.getSeconds() + delta);
                    break;
                default:
                    console.warn('Unknown time component:', component);
            }
            updateDisplay();
            
            // Visual feedback
            showFeedback(component);
        }
        
        /**
         * Show visual feedback when adjusting time
         */
        function showFeedback(component) {
            let element;
            switch(component) {
                case 'hours':
                    element = hoursDisplay;
                    break;
                case 'minutes':
                    element = minutesDisplay;
                    break;
                case 'seconds':
                    element = secondsDisplay;
                    break;
            }
            
            if (element) {
                element.style.transform = 'scale(1.2)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            }
        }
        
        /**
         * Check online status
         */
        function checkOnlineStatus() {
            isOnline = navigator.onLine;
            if (isOnline) {
                connectionStatus.textContent = 'Online';
                connectionStatus.style.background = '#e8f5e9';
                connectionStatus.style.color = '#2e7d32';
            } else {
                connectionStatus.textContent = 'Offline';
                connectionStatus.style.background = '#ffebee';
                connectionStatus.style.color = '#c62828';
            }
        }
        
        /**
         * Sync with server time (optional feature)
         */
        async function syncWithServer() {
            try {
                const response = await fetch('https://worldtimeapi.org/api/timezone/Asia/Jakarta');
                if (response.ok) {
                    const data = await response.json();
                    const serverTime = new Date(data.datetime);
                    currentTime = serverTime;
                    updateDisplay();
                    console.log('Time synced with server');
                }
            } catch (error) {
                console.log('Using local time (server sync unavailable)');
            }
        }
        
        /**
         * Reset to current real time
         */
        function resetToRealTime() {
            currentTime = new Date();
            updateDisplay();
            showToast('Waktu telah direset ke waktu sebenarnya');
        }
        
        /**
         * Show toast notification
         */
        function showToast(message) {
            // Create toast element if it doesn't exist
            let toast = document.querySelector('.toast-notification');
            if (!toast) {
                toast = document.createElement('div');
                toast.className = 'toast-notification';
                document.body.appendChild(toast);
                
                // Add styles for toast
                toast.style.position = 'fixed';
                toast.style.bottom = '20px';
                toast.style.left = '50%';
                toast.style.transform = 'translateX(-50%)';
                toast.style.background = '#333';
                toast.style.color = 'white';
                toast.style.padding = '12px 24px';
                toast.style.borderRadius = '8px';
                toast.style.fontSize = '14px';
                toast.style.zIndex = '1000';
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s ease';
                toast.style.pointerEvents = 'none';
            }
            
            toast.textContent = message;
            toast.style.opacity = '1';
            
            setTimeout(() => {
                toast.style.opacity = '0';
            }, 2000);
        }
        
        // ============================================
        // EVENT LISTENERS & INITIALIZATION
        // ============================================
        
        // Listen for online/offline events
        window.addEventListener('online', () => {
            checkOnlineStatus();
            showToast('Koneksi pulih - waktu akan disinkronkan');
            syncWithServer();
        });
        
        window.addEventListener('offline', () => {
            checkOnlineStatus();
            showToast('Koneksi terputus - menggunakan waktu lokal');
        });
        
        // Initialize the clock
        function init() {
            // Try to sync with server, then start clock
            syncWithServer().finally(() => {
                updateDisplay();
                startClock();
                checkOnlineStatus();
            });
            
            // Optional: Add keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'r') {
                    e.preventDefault();
                    resetToRealTime();
                }
            });
        }
        
        // Start the application
        init();
        
        // Export functions for global access (for debugging)
        if (typeof window !== 'undefined') {
            window.adjustTime = adjustTime;
            window.resetToRealTime = resetToRealTime;
        }