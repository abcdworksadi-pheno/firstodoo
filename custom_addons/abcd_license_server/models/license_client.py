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
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(
        string="Nom du Client",
        required=True,
        tracking=True,
        help="Nom de l'entreprise cliente"
    )
    
    code = fields.Char(
        string="Code Client",
        required=True,
        copy=False,
        index=True,
        tracking=True,
        help="Code unique du client (ex: CLIENTX)"
    )
    
    contact_name = fields.Char(
        string="Contact",
        help="Nom du contact principal"
    )
    
    email = fields.Char(
        string="Email",
        tracking=True,
        help="Email de contact"
    )
    
    phone = fields.Char(
        string="Téléphone",
        tracking=True,
        help="Numéro de téléphone"
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string="Contact / Adresse",
        help="Lien vers le contact pour localisation"
    )
    
    active = fields.Boolean(
        string="Actif",
        default=True,
        tracking=True
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
    
    def action_view_licenses(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("abcd_license_server.action_license")
        action['domain'] = [('client_id', '=', self.id)]
        action['context'] = {'default_client_id': self.id}
        return action
    
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
