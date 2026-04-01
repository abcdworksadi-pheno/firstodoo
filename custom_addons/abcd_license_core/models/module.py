# -*- coding: utf-8 -*-
"""
Hooks pour bloquer l'installation de modules ABCD sans licence valide
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
        DOUBLE PROTECTION : Vérifie aussi si abcd_license_guard est installé
        """
        # Modules exclus de la vérification (serveur de licence)
        excluded_modules = ['abcd_license_server', 'abcd_license_core', 'abcd_license_guard']
        
        # Vérifier par nom de module (plus fiable que category_id qui peut ne pas être chargé)
        module_name = self.name or ''
        is_abcd_module = module_name.startswith('abcd_') and module_name not in excluded_modules
        
        # Vérifier aussi par catégorie si disponible
        if not is_abcd_module and self.category_id:
            is_abcd_module = (self.category_id.name == 'ABCD' and 
                            module_name not in excluded_modules)
        
        if is_abcd_module:
            _logger.info(f"[ABCD LICENSE] Interception installation module ABCD: {module_name}")
            
            # Vérifier si abcd_license_guard est installé (protection supplémentaire)
            guard_module = self.env['ir.module.module'].sudo().search([
                ('name', '=', 'abcd_license_guard'),
                ('state', '=', 'installed')
            ], limit=1)
            
            if not guard_module:
                _logger.error(f"[ABCD LICENSE] BLOQUÉ: abcd_license_guard non installé pour {module_name}")
                raise UserError(
                    _("🔒 SÉCURITÉ CRITIQUE : Le module 'abcd_license_guard' doit être installé "
                      "AVANT tout module ABCD personnalisé.\n\n"
                      "Ce module est OBLIGATOIRE pour la protection des licences.\n\n"
                      "ÉTAPES OBLIGATOIRES :\n"
                      "1. Installer 'abcd_license_guard' EN PREMIER\n"
                      "2. Installer 'abcd_license_core'\n"
                      "3. Configurer la licence\n"
                      "4. Installer les autres modules ABCD")
                )
            
            # CRITIQUE : Vérifier AVANT que Odoo n'installe les dépendances
            # Si abcd_license_core n'est pas installé, bloquer immédiatement
            license_core_module = self.env['ir.module.module'].sudo().search([
                ('name', '=', 'abcd_license_core'),
                ('state', '=', 'installed')
            ], limit=1)
            
            if not license_core_module:
                _logger.warning(f"[ABCD LICENSE] Blocage: abcd_license_core non installé pour {module_name}")
                raise UserError(
                    _("Sécurité : Le module 'abcd_license_core' doit être installé "
                      "et configuré AVANT d'installer des modules ABCD personnalisés.\n\n"
                      "Veuillez d'abord installer et configurer 'abcd_license_core' "
                      "avec une licence valide, puis réessayez.\n\n"
                      "ÉTAPES :\n"
                      "1. Installer le module 'abcd_license_core'\n"
                      "2. Configurer le paramètre 'abcd.license.public_key_hex'\n"
                      "3. Configurer le paramètre 'abcd.license.blob'\n"
                      "4. Réessayer l'installation de ce module")
                )
            
            # Vérifier la configuration
            try:
                self._check_abcd_license_core_installed()
                _logger.info(f"[ABCD LICENSE] Configuration OK pour {module_name}")
            except UserError as e:
                _logger.warning(f"[ABCD LICENSE] Configuration invalide pour {module_name}: {e}")
                raise
        
        # Appeler la méthode originale
        return super()._button_immediate_function(method)

    def _check_abcd_license_core_installed(self):
        """
        Vérifie que abcd_license_core est installé et configuré
        
        Raises:
            UserError: Si abcd_license_core n'est pas installé ou configuré
        """
        # Vérifier si abcd_license_core est installé
        # Utiliser sudo() pour éviter les problèmes de droits
        license_core_module = self.env['ir.module.module'].sudo().search([
            ('name', '=', 'abcd_license_core'),
            ('state', '=', 'installed')
        ], limit=1)
        
        if not license_core_module:
            raise UserError(
                _("Sécurité : Le module 'abcd_license_core' doit être installé "
                  "et configuré AVANT d'installer des modules ABCD personnalisés.\n\n"
                  "Veuillez d'abord installer et configurer 'abcd_license_core' "
                  "avec une licence valide, puis réessayez.\n\n"
                  "ÉTAPES :\n"
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
            raise UserError(
                _("Sécurité : La clé publique ABCD n'est pas configurée.\n\n"
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
            raise UserError(
                _("Sécurité : Aucune licence ABCD configurée.\n\n"
                  "Veuillez configurer le paramètre système 'abcd.license.blob' "
                  "avec une licence valide avant d'installer des modules ABCD personnalisés.\n\n"
                  "Aller dans : Paramètres > Technique > Paramètres > Paramètres système")
            )
        
        return True

    def button_immediate_install(self):
        """
        Bloque l'installation si le module est de catégorie ABCD et licence invalide
        """
        # Modules exclus de la vérification (serveur de licence)
        excluded_modules = ['abcd_license_server', 'abcd_license_core']
        
        # Vérifier si c'est un module ABCD (et non exclu)
        if (self.category_id and self.category_id.name == 'ABCD' and 
            self.name not in excluded_modules):
            
            _logger.info(f"[ABCD LICENSE] Tentative d'installation du module ABCD: {self.name}")
            
            # CRITIQUE : Vérifier TOUJOURS que abcd_license_core est installé et configuré
            # AVANT qu'Odoo n'installe les dépendances (y compris abcd_license_core)
            # Cela empêche l'installation automatique de abcd_license_core sans vérification
            try:
                self._check_abcd_license_core_installed()
                _logger.info(f"[ABCD LICENSE] Vérification abcd_license_core OK pour {self.name}")
            except UserError as e:
                _logger.warning(f"[ABCD LICENSE] Blocage installation {self.name}: {e}")
                raise
            
            # Maintenant vérifier la licence pour ce module spécifique
            try:
                license_service = self.env['abcd.license']
                license_service.check_license(self.name)
                _logger.info(f"[ABCD LICENSE] Licence validée pour {self.name}")
            except Exception as e:
                # Bloquer l'installation avec message clair
                error_msg = str(e) if hasattr(e, '__str__') else repr(e)
                _logger.warning(f"[ABCD LICENSE] Licence invalide pour {self.name}: {error_msg}")
                raise UserError(
                    _("Impossible d'installer le module %s : %s\n\n"
                      "Contactez votre éditeur ABCD pour obtenir une licence valide.")
                    % (self.name, error_msg)
                )
        
        return super().button_immediate_install()

    def button_install(self):
        """
        Bloque l'installation planifiée si le module est de catégorie ABCD
        """
        # Modules exclus de la vérification (serveur de licence)
        excluded_modules = ['abcd_license_server', 'abcd_license_core']
        
        # Vérifier si c'est un module ABCD (et non exclu)
        if (self.category_id and self.category_id.name == 'ABCD' and 
            self.name not in excluded_modules):
            
            # CRITIQUE : Vérifier TOUJOURS que abcd_license_core est installé et configuré
            # AVANT qu'Odoo n'installe les dépendances (y compris abcd_license_core)
            self._check_abcd_license_core_installed()
            
            # Maintenant vérifier la licence pour ce module spécifique
            try:
                license_service = self.env['abcd.license']
                license_service.check_license(self.name)
            except Exception as e:
                # Bloquer l'installation avec message clair
                error_msg = str(e) if hasattr(e, '__str__') else repr(e)
                raise UserError(
                    _("Impossible d'installer le module %s : %s\n\n"
                      "Contactez votre éditeur ABCD pour obtenir une licence valide.")
                    % (self.name, error_msg)
                )
        
        return super().button_install()
