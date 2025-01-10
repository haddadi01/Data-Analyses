// script.js
let currentChart = null;

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

// Configuration des graphiques selon leur type
function getChartConfig(data, plotType, variable) {
    const baseConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            zoom: {
                zoom: {
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'xy'
                },
                pan: { enabled: true }
            },
            tooltip: {
                enabled: true
            }
        }
    };

    // Configurations spécifiques selon le type de graphique
    switch (plotType) {
        case 'pie':
            return {
                type: 'pie',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.values,
                        backgroundColor: data.labels.map(() => 
                            `hsl(${Math.random() * 360}, 70%, 50%)`
                        )
                    }]
                },
                options: {
                    ...baseConfig,
                    plugins: {
                        ...baseConfig.plugins,
                        legend: {
                            position: 'right'
                        }
                    }
                }
            };

        case 'histogram':
            return {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: variable,
                        data: data.values,
                        backgroundColor: 'rgba(74, 144, 226, 0.5)',
                        borderColor: 'rgba(74, 144, 226, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    ...baseConfig,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Fréquence'
                            }
                        }
                    }
                }
            };

        case 'box':
            return {
                type: 'boxplot',
                data: {
                    labels: [variable],
                    datasets: [{
                        data: [{
                            q1: data.stats.q1,
                            median: data.stats.median,
                            q3: data.stats.q3,
                            whiskers: data.stats.whiskers
                        }]
                    }]
                },
                options: baseConfig
            };

        case 'scatter':
            return {
                type: 'scatter',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: variable,
                        data: data.values.map((value, index) => ({
                            x: index,
                            y: value
                        })),
                        backgroundColor: 'rgba(74, 144, 226, 0.5)'
                    }]
                },
                options: {
                    ...baseConfig,
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom',
                            title: {
                                display: true,
                                text: 'Index'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: variable
                            }
                        }
                    }
                }
            };

        default:
            return {
                type: plotType,
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: variable,
                        data: data.values,
                        backgroundColor: 'rgba(74, 144, 226, 0.5)',
                        borderColor: 'rgba(74, 144, 226, 1)',
                        borderWidth: 1,
                        tension: plotType === 'line' ? 0.4 : 0
                    }]
                },
                options: {
                    ...baseConfig,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: variable
                            }
                        }
                    }
                }
            };
    }
}

// Gestion des graphiques
async function generateChart(chartData) {
    try {
        if (currentChart) {
            currentChart.destroy();
        }

        const ctx = document.getElementById('dataChart').getContext('2d');
        const config = getChartConfig(
            chartData.chart_data,
            chartData.plot_type,
            chartData.chart_data.datasets[0].label
        );

        currentChart = new Chart(ctx, config);

        // Activer les contrôles
        enableChartControls(true);
    } catch (error) {
        console.error('Erreur lors de la génération du graphique:', error);
        alert('Erreur lors de la génération du graphique');
        enableChartControls(false);
    }
}

// Activation/désactivation des contrôles
function enableChartControls(enabled) {
    const controls = ['zoom-in', 'zoom-out', 'reset-zoom', 'download-png', 'download-svg'];
    controls.forEach(controlId => {
        const element = document.getElementById(controlId);
        if (element) {
            element.disabled = !enabled;
            element.style.opacity = enabled ? '1' : '0.5';
        }
    });
}

// Gestion des contrôles du graphique
function setupChartControls() {
    // ... autres contrôles ...

    // Download controls
    ['png', 'svg'].forEach(format => {
        document.getElementById(`download-${format}`)?.addEventListener('click', async () => {
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

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `graphique.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Erreur lors du téléchargement');
                }
            } catch (error) {
                console.error('Erreur lors du téléchargement:', error);
                alert('Erreur lors du téléchargement du graphique');
            }
        });
    });
}
// Gestion du formulaire de visualisation
function setupVisualizationForm() {
    const form = document.getElementById('visualization-form');
    
    form?.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const plotType = formData.get('plot_type');
        const variable = formData.get('variable');

        if (!plotType || !variable) {
            alert('Veuillez sélectionner un type de graphique et une variable');
            return;
        }

        try {
            const response = await fetch('/generate-plot/', {  // Assurez-vous que cette URL correspond à votre configuration
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    plot_type: plotType,
                    variable: variable,
                    params: {
                        bins: 30
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erreur lors de la génération du graphique');
            }

            const chartData = await response.json();
            await generateChart(chartData);
        } catch (error) {
            console.error('Erreur:', error);
            alert(error.message);
        }
    });
}