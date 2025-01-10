// Fonctions utilitaires
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Gestionnaire des événements
const eventHandlers = {
    setupVisualizationForm() {
        const form = document.getElementById('visualization-form');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const plotType = formData.get('plot_type');
            const variable = formData.get('variable');

            if (!plotType || !variable) {
                alert('Veuillez sélectionner un type de graphique et une variable');
                return;
            }

            await chartManager.generateChart(plotType, variable);
        });
    },

    setupChartControls() {
        // Zoom controls
        document.getElementById('zoom-in')?.addEventListener('click', () => {
            if (currentChart) {
                currentChart.zoom(1.1);
            }
        });

        document.getElementById('zoom-out')?.addEventListener('click', () => {
            if (currentChart) {
                currentChart.zoom(0.9);
            }
        });

        document.getElementById('reset-zoom')?.addEventListener('click', () => {
            chartManager.resetZoom();
        });

        // Download controls
        ['png', 'svg'].forEach(format => {
            document.getElementById(`download-${format}`)?.addEventListener('click', () => {
                chartManager.downloadChart(format);
            });
        });

        // Désactiver initialement tous les contrôles
        chartManager.enableControls(false);
    },

    init() {
        this.setupVisualizationForm();
        this.setupChartControls();
    }
};

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    eventHandlers.init();
});