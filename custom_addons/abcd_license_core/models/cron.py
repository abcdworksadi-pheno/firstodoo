# -*- coding: utf-8 -*-
"""
Cron pour vérification online optionnelle de licence
"""

import logging
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from datetime import datetime, timezone
from odoo import models, api

_logger = logging.getLogger(__name__)


class AbcdLicense(models.TransientModel):
    """Extension pour ajouter la méthode de vérification online"""
    _inherit = 'abcd.license'

    @api.model
    def _check_online_license_verification(self):
        """
        Cron pour vérification online optionnelle (toutes les 24h)
        Ne bloque jamais, fallback sur vérification offline
        """
        if not REQUESTS_AVAILABLE:
            _logger.debug("Bibliothèque requests non disponible pour vérification online")
            return
        
        try:
            # Récupérer le blob de licence
            license_blob = self.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.blob'
            )
            
            if not license_blob:
                _logger.debug("Pas de licence configurée pour vérification online")
                return
            
            # URL du serveur de licence
            license_server_url = self.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.server_url',
                default=''
            )
            
            if not license_server_url:
                _logger.debug("Serveur de licence non configuré pour vérification online")
                return
            
            # Requête au serveur (timeout 3s)
            try:
                response = requests.post(
                    f"{license_server_url}/api/v1/license/verify",
                    json={'license': license_blob},
                    timeout=3
                )
                
                if response.status_code == 200:
                    # Mettre à jour le timestamp de dernière vérification
                    self.env['ir.config_parameter'].sudo().set_param(
                        'abcd.license.last_online_check',
                        datetime.now(timezone.utc).isoformat()
                    )
                    _logger.info("Vérification online de licence réussie")
                else:
                    _logger.warning(
                        f"Vérification online échouée: {response.status_code}"
                    )
                    
            except requests.Timeout:
                _logger.debug("Timeout lors de la vérification online (normal si offline)")
            except requests.RequestException as e:
                _logger.debug(f"Erreur réseau lors de la vérification online: {e}")
                
        except Exception as e:
            # Ne jamais faire échouer le cron
            _logger.error(
                f"Erreur dans le cron de vérification online: {e}",
                exc_info=True
            )
