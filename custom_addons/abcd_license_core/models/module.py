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

    def button_immediate_install(self):
        """
        Bloque l'installation si le module est de catégorie ABCD et licence invalide
        """
        # Modules exclus de la vérification (serveur de licence)
        excluded_modules = ['abcd_license_server', 'abcd_license_core']
        
        # Vérifier si c'est un module ABCD (et non exclu)
        if (self.category_id and self.category_id.name == 'ABCD' and 
            self.name not in excluded_modules):
            license_service = self.env['abcd.license']
            try:
                # Vérifier la licence pour ce module spécifique
                license_service.check_license(self.name)
            except UserError as e:
                # Bloquer l'installation avec message clair
                raise UserError(
                    _("Impossible d'installer le module %s : %s\n\n"
                      "Contactez votre éditeur ABCD pour obtenir une licence valide.")
                    % (self.name, str(e))
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
            license_service = self.env['abcd.license']
            try:
                license_service.check_license(self.name)
            except UserError as e:
                raise UserError(
                    _("Impossible d'installer le module %s : %s\n\n"
                      "Contactez votre éditeur ABCD pour obtenir une licence valide.")
                    % (self.name, str(e))
                )
        
        return super().button_install()
