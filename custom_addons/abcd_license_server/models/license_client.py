# -*- coding: utf-8 -*-
"""
Modèle Client pour les licences ABCD
"""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LicenseClient(models.Model):
    """Client pour lequel on génère des licences"""
    
    _name = 'license.client'
    _description = 'ABCD License Client'
    _order = 'name'
    
    name = fields.Char(
        string="Nom du Client",
        required=True,
        help="Nom de l'entreprise cliente"
    )
    
    code = fields.Char(
        string="Code Client",
        required=True,
        copy=False,
        index=True,
        help="Code unique du client (ex: CLIENTX)"
    )
    
    contact_name = fields.Char(
        string="Contact",
        help="Nom du contact principal"
    )
    
    email = fields.Char(
        string="Email",
        help="Email de contact"
    )
    
    phone = fields.Char(
        string="Téléphone",
        help="Numéro de téléphone"
    )
    
    active = fields.Boolean(
        string="Actif",
        default=True
    )
    
    license_ids = fields.One2many(
        'license.license',
        'client_id',
        string="Licences",
        help="Licences générées pour ce client"
    )
    
    license_count = fields.Integer(
        string="Nombre de Licences",
        compute='_compute_license_count',
        store=True
    )
    
    @api.depends('license_ids')
    def _compute_license_count(self):
        """Calcule le nombre de licences pour ce client"""
        for record in self:
            record.license_count = len(record.license_ids)
    
    @api.constrains('code')
    def _check_code_unique(self):
        """Vérifie que le code client est unique"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]):
                raise ValidationError(_("Le code client '%s' existe déjà.") % record.code)
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code client doit être unique.')
    ]
    
    def action_view_licenses(self):
        """Ouvre la vue des licences pour ce client"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Licences de %s') % self.name,
            'res_model': 'license.license',
            'view_mode': 'list,form',
            'domain': [('client_id', '=', self.id)],
            'context': {'default_client_id': self.id},
        }
