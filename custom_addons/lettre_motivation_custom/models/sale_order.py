# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """Extension de sale.order pour générer des lettres de motivation"""
    _inherit = 'sale.order'

    lettre_motivation_ids = fields.One2many(
        'lettre.motivation.instance',
        'sale_order_id',
        string='Lettres Générées',
        help='Lettres de motivation générées depuis cette commande'
    )

    lettre_motivation_count = fields.Integer(
        string='Nombre de Lettres',
        compute='_compute_lettre_motivation_count',
        help='Nombre de lettres générées pour cette commande'
    )

    @api.depends('lettre_motivation_ids')
    def _compute_lettre_motivation_count(self):
        """Compter les lettres générées"""
        for order in self:
            order.lettre_motivation_count = len(order.lettre_motivation_ids)

    def action_generate_lettre(self):
        """Action pour générer une lettre depuis la commande"""
        self.ensure_one()
        
        # Ouvrir directement le wizard de sélection de modèle
        # Tous les modèles actifs sont disponibles
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sélectionner un Modèle de Lettre'),
            'res_model': 'lettre.motivation.selection.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            }
        }


    def action_view_lettres(self):
        """Ouvrir la vue des lettres générées"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lettres Générées',
            'res_model': 'lettre.motivation.instance',
            'view_mode': 'list,form',
            'domain': [('sale_order_id', '=', self.id)],
            'context': {'default_sale_order_id': self.id},
        }

