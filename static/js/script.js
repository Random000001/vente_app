document.addEventListener('DOMContentLoaded', function() {
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            html: true,
            trigger: 'hover'
        });
    });

    // Real-time calculations
    const calculateFields = () => {
        const prixEuro = parseFloat(document.getElementById('prix_euro')?.value) || 0;
        const prixVente = parseFloat(document.getElementById('prix_vente')?.value) || 0;
        const avance = parseFloat(document.getElementById('avance')?.value) || 0;
        
        // Calculate dinar price
        const prixDinar = prixEuro * {{ EURO_TO_DINAR }};
        if (document.getElementById('prix_dinar_display')) {
            document.getElementById('prix_dinar_display').textContent = prixDinar.toFixed(2);
        }
        
        // Calculate gain
        const gain = prixVente - prixDinar;
        if (document.getElementById('gain_display')) {
            document.getElementById('gain_display').textContent = gain.toFixed(2);
            
            // Color coding for gain
            if (gain > 0) {
                document.getElementById('gain_display').className = 'form-control text-success';
            } else if (gain < 0) {
                document.getElementById('gain_display').className = 'form-control text-danger';
            } else {
                document.getElementById('gain_display').className = 'form-control';
            }
        }
    };

    // Attach event listeners for real-time calculations
    ['prix_euro', 'prix_vente', 'avance'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('input', calculateFields);
        }
    });

    // Auto-count articles
    const articlesTextarea = document.getElementById('articles');
    if (articlesTextarea) {
        articlesTextarea.addEventListener('blur', function() {
            const articles = this.value.split('\n').filter(art => art.trim());
            const count = articles.length;
            
            if (count > 0 && !this.value.startsWith(`${count} pièce${count > 1 ? 's' : ''} :`)) {
                // Remove existing count if present
                if (this.value.includes(':')) {
                    this.value = this.value.split(':').slice(1).join(':').trim();
                }
                
                // Add count prefix
                this.value = `${count} pièce${count > 1 ? 's' : ''} :\n${this.value.trim()}`;
            }
        });
    }

    // Initial calculation
    calculateFields();
});