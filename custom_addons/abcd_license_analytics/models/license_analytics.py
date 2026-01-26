# -*- coding: utf-8 -*-
"""
Modèle d'analyses pour les licences ABCD
"""

from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class LicenseAnalytics(models.TransientModel):
    """Analyses et statistiques des licences"""
    
    _name = 'license.analytics'
    _description = 'ABCD License Analytics'
    
    @api.model
    def get_license_statistics(self):
        """Retourne les statistiques globales des licences"""
        License = self.env['license.license']
        
        total_licenses = License.search_count([])
        active_licenses = License.search_count([('state', '=', 'active')])
        expired_licenses = License.search_count([('state', '=', 'expired')])
        expiring_soon = License.search_count([('state', '=', 'expiring_soon')])
        
        return {
            'total': total_licenses,
            'active': active_licenses,
            'expired': expired_licenses,
            'expiring_soon': expiring_soon,
        }
    
    @api.model
    def get_license_by_edition(self):
        """Retourne la répartition des licences par édition"""
        License = self.env['license.license']
        
        editions = ['standard', 'pro', 'enterprise']
        result = {}
        
        for edition in editions:
            count = License.search_count([('edition', '=', edition)])
            result[edition] = count
        
        return result
    
    @api.model
    def get_license_by_client(self, limit=10):
        """Retourne les clients avec le plus de licences"""
        License = self.env['license.license']
        
        # Grouper par client
        query = """
            SELECT client_id, COUNT(*) as count
            FROM license_license
            WHERE client_id IS NOT NULL
            GROUP BY client_id
            ORDER BY count DESC
            LIMIT %s
        """
        
        self.env.cr.execute(query, (limit,))
        results = self.env.cr.dictfetchall()
        
        clients_data = []
        for row in results:
            client = self.env['license.client'].browse(row['client_id'])
            clients_data.append({
                'name': client.name,
                'code': client.code,
                'count': row['count']
            })
        
        return clients_data
    
    @api.model
    def get_expiring_licenses(self, days=30):
        """Retourne les licences expirant dans les X prochains jours"""
        License = self.env['license.license']
        now = fields.Datetime.now()
        future_date = now + timedelta(days=days)
        
        licenses = License.search([
            ('expiry_date', '>=', now),
            ('expiry_date', '<=', future_date),
            ('state', '!=', 'expired')
        ], order='expiry_date asc')
        
        return [{
            'name': lic.name,
            'client': lic.client_id.name,
            'expiry_date': lic.expiry_date.strftime('%d/%m/%Y'),
            'days_left': lic.days_until_expiry,
        } for lic in licenses]
    
    @api.model
    def get_license_trends(self, months=12):
        """Retourne les tendances de génération de licences sur X mois"""
        License = self.env['license.license']
        
        now = datetime.now()
        trends = []
        
        for i in range(months - 1, -1, -1):
            month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
            if i == 0:
                month_end = now
            else:
                next_month = month_start + timedelta(days=32)
                month_end = next_month.replace(day=1) - timedelta(seconds=1)
            
            count = License.search_count([
                ('issued_at', '>=', month_start),
                ('issued_at', '<=', month_end)
            ])
            
            trends.append({
                'month': month_start.strftime('%Y-%m'),
                'label': month_start.strftime('%b %Y'),
                'count': count
            })
        
        return trends
    
    @api.model
    def get_module_usage(self):
        """Retourne l'utilisation des modules (combien de licences incluent chaque module)"""
        License = self.env['license.license']
        
        all_licenses = License.search([])
        module_usage = {}
        
        for license in all_licenses:
            if license.modules:
                modules = [m.strip() for m in license.modules.split(',') if m.strip()]
                for module in modules:
                    module_usage[module] = module_usage.get(module, 0) + 1
        
        # Trier par utilisation décroissante
        sorted_modules = sorted(module_usage.items(), key=lambda x: x[1], reverse=True)
        
        return [{'module': mod, 'count': count} for mod, count in sorted_modules[:20]]
    
    @api.model
    def get_key_statistics(self):
        """Retourne les statistiques sur les clés"""
        Key = self.env['license.key']
        
        total_keys = Key.search_count([])
        active_keys = Key.search_count([('active', '=', True)])
        generated_keys = Key.search_count([('key_generated', '=', True)])
        
        # Clé la plus utilisée
        most_used_key = Key.search([('key_generated', '=', True)], order='license_count desc', limit=1)
        
        return {
            'total': total_keys,
            'active': active_keys,
            'generated': generated_keys,
            'most_used': {
                'name': most_used_key.name if most_used_key else None,
                'count': most_used_key.license_count if most_used_key else 0
            }
        }
