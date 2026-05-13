 document.querySelectorAll('.color-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.color-option').forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('selectedColor').value = this.dataset.color;
            });
        });
        
        // Icon selection handler
        document.querySelectorAll('.icon-option').forEach(option => {
            option.addEventListener('click', function() {
                document.querySelectorAll('.icon-option').forEach(opt => opt.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('selectedIcon').value = this.dataset.icon;
            });
        });