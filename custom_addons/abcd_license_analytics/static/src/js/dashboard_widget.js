/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState, onMounted, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class LicenseDashboardWidget extends Component {
    setup() {
        this.orm = useService("orm");
        this.editionChartRef = useRef("chart_edition");
        this.trendsChartRef = useRef("chart_trends");
        
        this.state = useState({
            stats: {},
            loading: true,
            clientsData: [],
            modulesData: [],
            expiringData: []
        });
        
        onWillStart(async () => {
            // Charger la librairie Chart.js incluse dans Odoo
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadData();
        });

        onMounted(() => {
            if (!this.state.loading) {
                this.renderCharts();
            }
        });
    }

    async loadData() {
        try {
            // Charger les statistiques via le service orm d'Odoo 16+
            const stats = await this.orm.call(
                "license.analytics",
                "get_license_statistics",
                []
            );
            
            this.state.stats = stats;
            await this.loadCharts();
            this.state.loading = false;
        } catch (error) {
            console.error("Erreur lors du chargement des données:", error);
            this.state.loading = false;
        }
    }

    async loadCharts() {
        try {
            // Charger les données pour les graphiques et tableaux
            let editionData = {};
            try {
                editionData = await this.orm.call(
                    "license.analytics",
                    "get_license_by_edition",
                    []
                );
            } catch (e) { console.log("get_license_by_edition failed", e); }

            let trendsData = [];
            try {
                trendsData = await this.orm.call(
                    "license.analytics",
                    "get_license_trends",
                    [12]
                );
            } catch (e) { console.log("get_license_trends failed", e); }

            let clientsData = [];
            try {
                clientsData = await this.orm.call(
                    "license.analytics",
                    "get_license_by_client",
                    [10]
                );
            } catch (e) { console.log("get_license_by_client failed", e); }

            let modulesData = [];
            try {
                modulesData = await this.orm.call(
                    "license.analytics",
                    "get_module_usage",
                    []
                );
            } catch (e) { console.log("get_module_usage failed", e); }

            let expiringData = [];
            try {
                expiringData = await this.orm.call(
                    "license.analytics",
                    "get_expiring_licenses",
                    [30]
                );
            } catch (e) { console.log("get_expiring_licenses failed", e); }

            this.state.editionData = editionData || {};
            this.state.trendsData = trendsData || [];
            this.state.clientsData = clientsData || [];
            this.state.modulesData = modulesData || [];
            this.state.expiringData = expiringData || [];
            
            // Si on est déjà monté (après un reload), on redessine les graphiques
            if (this.editionChartRef.el) {
                this.renderCharts();
            }
        } catch (error) {
            console.error("Erreur detail charts:", error);
        }
    }

    renderCharts() {
        if (!window.Chart) {
            console.error("Chart.js n'est pas chargé");
            return;
        }

        // --- Graphique Répartition par Édition (Pie/Doughnut) ---
        if (this.editionChartRef.el && this.state.editionData) {
            const ctx = this.editionChartRef.el.getContext('2d');
            
            // Détruire le chart existant si nécessaire
            if (this.editionChart) {
                this.editionChart.destroy();
            }

            const labels = Object.keys(this.state.editionData).map(
                key => key.charAt(0).toUpperCase() + key.slice(1)
            );
            const data = Object.values(this.state.editionData);

            this.editionChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: { position: 'bottom' }
                }
            });
        }

        // --- Graphique Tendances (Bar/Line) ---
        if (this.trendsChartRef.el && this.state.trendsData && this.state.trendsData.length > 0) {
            const ctx = this.trendsChartRef.el.getContext('2d');

            if (this.trendsChart) {
                this.trendsChart.destroy();
            }

            // Inverser si nécessaire (le serveur peut renvoyer du plus récent au plus ancien)
            let trends = [...this.state.trendsData];
            
            const labels = trends.map(t => t.label);
            const data = trends.map(t => t.count);

            this.trendsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Licences émises',
                        data: data,
                        backgroundColor: '#3498db',
                        borderColor: '#2980b9',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        yAxes: [{
                            ticks: { beginAtZero: true, precision: 0 }
                        }]
                    },
                    legend: { display: false }
                }
            });
        }
    }
}

LicenseDashboardWidget.template = "abcd_license_analytics.DashboardWidget";

registry.category("actions").add("license_dashboard", LicenseDashboardWidget);
