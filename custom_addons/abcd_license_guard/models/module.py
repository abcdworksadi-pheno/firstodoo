# -*- coding: utf-8 -*-
"""
Hook de protection pour bloquer l'installation de modules ABCD sans licence
Ce module est TOUJOURS chargé car il ne dépend que de 'base'
"""

import logging
from odoo import models, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    """Extension pour bloquer l'installation de modules ABCD sans licence"""
    
    _inherit = 'ir.module.module'

    def _button_immediate_function(self, method):
        """
        Intercepte AVANT l'installation des dépendances
        C'est ici qu'on peut bloquer avant qu'Odoo n'installe abcd_license_core automatiquement
        """
        # Modules exclus de la vérification
        excluded_modules = ['abcd_license_server', 'abcd_license_core', 'abcd_license_guard', 'abcd_license_analytics']
        
        # Vérifier par nom de module (plus fiable)
        module_name = self.name or ''
        is_abcd_module = module_name.startswith('abcd_') and module_name not in excluded_modules
        
        # Vérifier aussi par catégorie si disponible
        if not is_abcd_module and self.category_id:
            is_abcd_module = (self.category_id.name == 'ABCD' and 
                            module_name not in excluded_modules)
        
        if is_abcd_module:
            _logger.warning(f"[ABCD LICENSE GUARD] Tentative d'installation module ABCD: {module_name}")
            
            # CRITIQUE : Vérifier AVANT que Odoo n'installe les dépendances
            # Si abcd_license_core n'est pas installé, bloquer immédiatement
            license_core_module = self.env['ir.module.module'].sudo().search([
                ('name', '=', 'abcd_license_core'),
                ('state', '=', 'installed')
            ], limit=1)
            
            if not license_core_module:
                _logger.error(f"[ABCD LICENSE GUARD] BLOQUÉ: abcd_license_core non installé pour {module_name}")
                raise UserError(
                    _("🔒 SÉCURITÉ : Le module 'abcd_license_core' doit être installé "
                      "et configuré AVANT d'installer des modules ABCD personnalisés.\n\n"
                      "Veuillez d'abord installer et configurer 'abcd_license_core' "
                      "avec une licence valide, puis réessayez.\n\n"
                      "ÉTAPES OBLIGATOIRES :\n"
                      "1. Installer le module 'abcd_license_core'\n"
                      "2. Configurer le paramètre 'abcd.license.public_key_hex'\n"
                      "3. Configurer le paramètre 'abcd.license.blob'\n"
                      "4. Réessayer l'installation de ce module")
                )
            
            # Vérifier que la clé publique est configurée
            public_key = self.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.public_key_hex',
                default=''
            )
            
            if not public_key or public_key == '0' * 64 or len(public_key) < 64:
                _logger.error(f"[ABCD LICENSE GUARD] BLOQUÉ: Clé publique non configurée pour {module_name}")
                raise UserError(
                    _("🔒 SÉCURITÉ : La clé publique ABCD n'est pas configurée.\n\n"
                      "Veuillez configurer le paramètre système 'abcd.license.public_key_hex' "
                      "avant d'installer des modules ABCD personnalisés.\n\n"
                      "Aller dans : Paramètres > Technique > Paramètres > Paramètres système")
                )
            
            # Vérifier que le license_blob est configuré
            license_blob = self.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.blob',
                default=''
            )
            
            if not license_blob or license_blob.strip() == '':
                _logger.error(f"[ABCD LICENSE GUARD] BLOQUÉ: Licence non configurée pour {module_name}")
                raise UserError(
                    _("🔒 SÉCURITÉ : Aucune licence ABCD configurée.\n\n"
                      "Veuillez configurer le paramètre système 'abcd.license.blob' "
                      "avec une licence valide avant d'installer des modules ABCD personnalisés.\n\n"
                      "Aller dans : Paramètres > Technique > Paramètres > Paramètres système")
                )
            
            _logger.info(f"[ABCD LICENSE GUARD] Vérifications OK pour {module_name}, installation autorisée")
        
        # Appeler la méthode originale
        return super()._button_immediate_function(method)
