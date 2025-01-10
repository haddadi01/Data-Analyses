// Configuration globale et état
let currentChart = null;

// Configuration des graphiques selon leur type
const chartConfig = {
    getBaseConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                zoom: {
                    zoom: {
                        wheel: { enabled: true },
                        pinch: { enabled: true },
                        mode: 'xy'
                    },
                    pan: { enabled: true },
                    limits: {
                        y: { min: 'original', max: 'original' }
                    }
                },
                title: {
                    display: true,
                    text: 'Analyse de données'
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        };
    },

    createChartConfig(chartData) {
        const baseConfig = this.getBaseConfig();
        const config = {
            type: chartData.type,
            data: {
                labels: chartData.data.labels,
                datasets: chartData.data.datasets.map(dataset => ({
                    ...dataset,
                    backgroundColor: dataset.backgroundColor || 'rgba(74, 144, 226, 0.5)',
                    borderColor: dataset.borderColor || 'rgba(74, 144, 226, 1)',
                    borderWidth: dataset.borderWidth || 1
                }))
            },
            options: {
                ...baseConfig,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: chartData.data.datasets[0].label || 'Valeur'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Données'
                        }
                    }
                }
            }
        };

        // Configurations spécifiques selon le type de graphique
        switch (chartData.type) {
            case 'pie':
                config.options.scales = {};
                break;
            case 'histogram':
                config.options.scales.y.title.text = 'Fréquence';
                break;
            case 'box':
                config.options.scales.y.title.text = 'Distribution';
                break;
        }

        return config;
    }
};

// Gestion des graphiques
const chartManager = {
    async generateChart(plotType, variable) {
        try {
            const response = await fetch('/generate-plot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    plot_type: plotType,
                    variable: variable,
                    params: { bins: 30 }
                })
            });

            if (!response.ok) {
                throw new Error('Erreur lors de la génération du graphique');
            }

            const chartData = await response.json();
            this.renderChart(chartData);
            return true;
        } catch (error) {
            console.error('Erreur:', error);
            alert(error.message);
            return false;
        }
    },

    renderChart(chartData) {
        if (currentChart) {
            currentChart.destroy();
        }

        const ctx = document.getElementById('dataChart').getContext('2d');
        const config = chartConfig.createChartConfig(chartData);
        currentChart = new Chart(ctx, config);
        
        // Activer les contrôles
        this.enableControls(true);
    },

    enableControls(enabled) {
        const controls = document.querySelectorAll('.chart-button');
        controls.forEach(control => {
            control.disabled = !enabled;
            control.style.opacity = enabled ? '1' : '0.5';
        });
    },

    resetZoom() {
        if (currentChart) {
            currentChart.resetZoom();
        }
    },

    async downloadChart(format) {
        if (!currentChart) return;

        try {
            const response = await fetch('/download-plot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    plot_data: currentChart.data,
                    format: format,
                    type: currentChart.config.type
                })
            });

            if (!response.ok) {
                throw new Error('Erreur lors du téléchargement');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `graphique.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur lors du téléchargement du graphique');
        }
    }
};