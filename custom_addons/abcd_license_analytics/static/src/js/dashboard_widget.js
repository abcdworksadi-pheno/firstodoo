/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LicenseDashboardWidget extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            stats: {},
            loading: true
        });
        
        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        try {
            // Charger les statistiques
            const stats = await this.rpc("/web/dataset/call_kw/license.analytics/get_license_statistics", {
                model: "license.analytics",
                method: "get_license_statistics",
                args: [],
                kwargs: {},
            });
            
            this.state.stats = stats;
            this.state.loading = false;
            
            // Mettre à jour les éléments DOM
            this.updateStats();
            await this.loadCharts();
        } catch (error) {
            console.error("Erreur lors du chargement des données:", error);
        }
    }

    updateStats() {
        const stats = this.state.stats;
        document.getElementById('stat_total').textContent = stats.total || 0;
        document.getElementById('stat_active').textContent = stats.active || 0;
        document.getElementById('stat_expired').textContent = stats.expired || 0;
        document.getElementById('stat_expiring').textContent = stats.expiring_soon || 0;
    }

    async loadCharts() {
        // Charger les données pour les graphiques
        const editionData = await this.rpc("/web/dataset/call_kw/license.analytics/get_license_by_edition", {
            model: "license.analytics",
            method: "get_license_by_edition",
            args: [],
            kwargs: {},
        });

        const trendsData = await this.rpc("/web/dataset/call_kw/license.analytics/get_license_trends", {
            model: "license.analytics",
            method: "get_license_trends",
            args: [12],
            kwargs: {},
        });

        const clientsData = await this.rpc("/web/dataset/call_kw/license.analytics/get_license_by_client", {
            model: "license.analytics",
            method: "get_license_by_client",
            args: [10],
            kwargs: {},
        });

        const modulesData = await this.rpc("/web/dataset/call_kw/license.analytics/get_module_usage", {
            model: "license.analytics",
            method: "get_module_usage",
            args: [],
            kwargs: {},
        });

        const expiringData = await this.rpc("/web/dataset/call_kw/license.analytics/get_expiring_licenses", {
            model: "license.analytics",
            method: "get_expiring_licenses",
            args: [30],
            kwargs: {},
        });

        // Mettre à jour les tableaux
        this.updateTopClients(clientsData);
        this.updateTopModules(modulesData);
        this.updateExpiringLicenses(expiringData);
    }

    updateTopClients(data) {
        const tbody = document.getElementById('top_clients');
        if (!tbody) return;
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="text-center">Aucune donnée</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(client => `
            <tr>
                <td>${client.name} (${client.code})</td>
                <td class="text-right">${client.count}</td>
            </tr>
        `).join('');
    }

    updateTopModules(data) {
        const tbody = document.getElementById('top_modules');
        if (!tbody) return;
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="2" class="text-center">Aucune donnée</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(mod => `
            <tr>
                <td>${mod.module}</td>
                <td class="text-right">${mod.count}</td>
            </tr>
        `).join('');
    }

    updateExpiringLicenses(data) {
        const tbody = document.getElementById('expiring_licenses');
        if (!tbody) return;
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">Aucune licence n\'expire dans les 30 prochains jours</td></tr>';
            return;
        }

        tbody.innerHTML = data.map(lic => `
            <tr>
                <td>${lic.name}</td>
                <td>${lic.client}</td>
                <td>${lic.expiry_date}</td>
                <td><span class="badge badge-warning">${lic.days_left} jours</span></td>
            </tr>
        `).join('');
    }
}

LicenseDashboardWidget.template = "abcd_license_analytics.DashboardWidget";

registry.category("actions").add("license_dashboard", LicenseDashboardWidget);
