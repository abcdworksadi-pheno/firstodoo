# -*- coding: utf-8 -*-
"""
Contrôleur pour la vérification online optionnelle de licence
"""

import logging
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from datetime import datetime, timezone
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AbcdLicenseController(http.Controller):
    """Contrôleur pour la vérification online de licence"""

    @http.route('/abcd/license/verify', type='json', auth='user', methods=['POST'])
    def verify_license_online(self, **kwargs):
        """
        Endpoint pour vérification online optionnelle
        
        Returns:
            dict: Statut de la vérification
        """
        if not REQUESTS_AVAILABLE:
            return {
                'success': False,
                'error': 'Bibliothèque requests non disponible'
            }
        
        try:
            # Récupérer le blob de licence
            license_blob = request.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.blob'
            )
            
            if not license_blob:
                return {
                    'success': False,
                    'error': 'Aucune licence configurée'
                }
            
            # URL du serveur de licence (configurable)
            license_server_url = request.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.server_url',
                default=''
            )
            
            if not license_server_url:
                return {
                    'success': False,
                    'error': 'Serveur de licence non configuré'
                }
            
            # Requête au serveur (timeout 3s)
            try:
                response = requests.post(
                    f"{license_server_url}/api/v1/license/verify",
                    json={'license': license_blob},
                    timeout=3
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Mettre à jour le cache avec le statut
                    request.env['ir.config_parameter'].sudo().set_param(
                        'abcd.license.last_online_check',
                        datetime.now(timezone.utc).isoformat()
                    )
                    
                    return {
                        'success': True,
                        'message': 'Licence vérifiée avec succès'
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Erreur serveur: {response.status_code}'
                    }
                    
            except requests.Timeout:
                _logger.warning("Timeout lors de la vérification online de licence")
                return {
                    'success': False,
                    'error': 'Timeout - vérification offline utilisée'
                }
            except requests.RequestException as e:
                _logger.warning(f"Erreur réseau lors de la vérification online: {e}")
                return {
                    'success': False,
                    'error': 'Erreur réseau - vérification offline utilisée'
                }
                
        except Exception as e:
            _logger.error(f"Erreur lors de la vérification online: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
