// ============================================
// STATE MANAGEMENT
// ============================================

let currentDate   = new Date();
let selectedDate  = new Date().getDate();
let selectedMonth = new Date().getMonth();
let selectedYear  = new Date().getFullYear();

const today      = new Date();
const todayDate  = today.getDate();
const todayMonth = today.getMonth();
const todayYear  = today.getFullYear();

const monthNames = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
];

// ============================================
// HELPER FUNCTIONS
// ============================================

function getDaysInMonth(year, month) {
    return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
    return new Date(year, month, 1).getDay();
}

function updateMonthYearDisplay() {
    document.getElementById('currentMonth').textContent = monthNames[currentDate.getMonth()];
    document.getElementById('currentYear').textContent  = currentDate.getFullYear();
}

function updateSelectedDateDisplay() {
    var el = document.getElementById('selectedDateDisplay');
    if (!el) return;
    if (selectedDate) {
        el.textContent = selectedDate + ' ' + monthNames[selectedMonth] + ' ' + selectedYear;
    } else {
        el.textContent = '-';
    }
}

// ============================================
// RENDER CALENDAR
// ============================================

function renderCalendar() {
    var year        = currentDate.getFullYear();
    var month       = currentDate.getMonth();
    var daysInMonth = getDaysInMonth(year, month);
    var firstDay    = getFirstDayOfMonth(year, month);
    var calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;

    var totalCells = firstDay + daysInMonth;
    var totalWeeks = Math.ceil(totalCells / 7);

    var calendarHTML = '';
    var dayCounter   = 1;

    for (var week = 0; week < totalWeeks; week++) {
        var weekHTML = '<div class="week-row">';

        for (var dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
            var cellIndex = week * 7 + dayOfWeek;

            if (cellIndex < firstDay || dayCounter > daysInMonth) {
                weekHTML += '<div class="calendar-day empty"></div>';
            } else {
                var day = dayCounter;

                var isToday = (
                    day   === todayDate  &&
                    month === todayMonth &&
                    year  === todayYear
                );

                var isSelected = (
                    day   === selectedDate  &&
                    month === selectedMonth &&
                    year  === selectedYear
                );

                var isSunday = dayOfWeek === 0;

                var classes = 'calendar-day';
                if (isToday)    classes += ' today';
                if (isSelected) classes += ' selected';
                if (isSunday)   classes += ' sunday';

                weekHTML += '<button class="' + classes + '" onclick="handleDayClick(' + day + ')">' + day + '</button>';
                dayCounter++;
            }
        }

        weekHTML += '</div>';
        calendarHTML += weekHTML;
    }

    calendarGrid.innerHTML = calendarHTML;
    updateMonthYearDisplay();
    updateSelectedDateDisplay();
}

// ============================================
// EVENT HANDLERS
// ============================================

function handleDayClick(day) {
    if (!day) return;
    selectedDate  = day;
    selectedMonth = currentDate.getMonth();
    selectedYear  = currentDate.getFullYear();
    renderCalendar();
}

function navigateMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);

    var newMonth       = currentDate.getMonth();
    var newYear        = currentDate.getFullYear();
    var daysInNewMonth = getDaysInMonth(newYear, newMonth);

    // Reset seleksi saat pindah bulan
    selectedDate  = null;
    selectedMonth = newMonth;
    selectedYear  = newYear;

    renderCalendar();
}

function goToToday() {
    currentDate   = new Date();
    selectedDate  = todayDate;
    selectedMonth = todayMonth;
    selectedYear  = todayYear;
    renderCalendar();
}

// ============================================
// TAB HANDLER
// ============================================

function handleTabClick(tab) {
    var tabCalendar  = document.getElementById('tab-calendar');
    var tabMemo      = document.getElementById('tab-memo');
    var viewCalendar = document.getElementById('view-calendar');
    var viewMemo     = document.getElementById('view-memo');

    if (tab === 'calendar') {
        if (tabCalendar)  tabCalendar.classList.add('active');
        if (tabMemo)      tabMemo.classList.remove('active');
        if (viewCalendar) viewCalendar.style.display = 'block';
        if (viewMemo)     viewMemo.style.display     = 'none';
    } else if (tab === 'memo') {
        if (tabMemo)      tabMemo.classList.add('active');
        if (tabCalendar)  tabCalendar.classList.remove('active');
        if (viewMemo)     viewMemo.style.display     = 'block';
        if (viewCalendar) viewCalendar.style.display = 'none';
        loadMemo();
    }
}

// ============================================
// MEMO FUNCTIONS
// ============================================

function simpanMemo() {
    var isi  = document.getElementById('memo-input').value;
    var info = document.getElementById('memo-saved-info');
    localStorage.setItem('kasirpro_memo', isi);
    if (info) {
        info.textContent = 'Tersimpan otomatis ✓';
        setTimeout(function () { info.textContent = ''; }, 2000);
    }
}

function loadMemo() {
    var input = document.getElementById('memo-input');
    if (input) {
        input.value = localStorage.getItem('kasirpro_memo') || '';
    }
}

function hapusMemo() {
    if (!confirm('Hapus semua catatan memo?')) return;
    localStorage.removeItem('kasirpro_memo');
    var input = document.getElementById('memo-input');
    if (input) input.value = '';
}

// ============================================
// KEYBOARD NAVIGATION
// ============================================

document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft')              navigateMonth(-1);
    if (e.key === 'ArrowRight')             navigateMonth(1);
    if (e.key === 't' || e.key === 'T')     goToToday();
});

// ============================================
// INIT
// ============================================
renderCalendar();
handleTabClick('calendar');
loadMemo();

// Optional: Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        goToToday();
    }
});

