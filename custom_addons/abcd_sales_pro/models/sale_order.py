# -*- coding: utf-8 -*-
"""
Modèle exemple avec vérification de licence ABCD
"""

import logging
from odoo import models, api, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    """Extension de sale.order avec vérification de licence"""
    
    _inherit = 'sale.order'

    # Champ personnalisé exemple
    abcd_pro_notes = fields.Text(
        string="Notes Pro ABCD",
        help="Champ réservé à l'édition Pro"
    )

    @api.model
    def create(self, vals):
        """
        Création avec vérification de licence
        """
        # Vérifier la licence avant création
        license_service = self.env['abcd.license']
        try:
            license_service.check_license('abcd_sales_pro')
        except UserError as e:
            # Relancer l'erreur avec message utilisateur
            raise UserError(
                _("Impossible de créer la commande : %s") % str(e)
            )
        
        return super().create(vals)

    def write(self, vals):
        """
        Modification avec vérification de licence
        """
        # Vérifier la licence avant modification
        license_service = self.env['abcd.license']
        try:
            license_service.check_license('abcd_sales_pro')
        except UserError as e:
            # Relancer l'erreur avec message utilisateur
            raise UserError(
                _("Impossible de modifier la commande : %s") % str(e)
            )
        
        return super().write(vals)

    def action_abcd_pro_report(self):
        """
        Action métier exemple nécessitant une licence
        """
        self.ensure_one()
        
        # Vérifier la licence
        license_service = self.env['abcd.license']
        try:
            license_service.check_license('abcd_sales_pro')
        except UserError as e:
            raise UserError(str(e))
        
        # Logique métier ici
        _logger.info(f"Génération du rapport Pro pour la commande {self.name}")
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rapport Pro ABCD'),
            'res_model': 'sale.order',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
