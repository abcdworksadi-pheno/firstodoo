# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LettreMotivationTemplateBinding(models.Model):
    """Liaison entre un template de lettre et un modèle Odoo"""
    _name = 'lettre.motivation.template.binding'
    _description = 'Liaison Template - Modèle Odoo'
    _order = 'name'

    name = fields.Char(
        string='Nom',
        required=True,
        help='Nom de la configuration (ex: "Lettre de Mission - Commande")'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle de Lettre',
        required=True,
        ondelete='cascade',
        help='Modèle de lettre à utiliser'
    )

    model_id = fields.Many2one(
        'ir.model',
        string='Modèle Odoo',
        required=True,
        ondelete='cascade',
        help='Modèle Odoo pour lequel ce template est disponible'
    )

    model_name = fields.Char(
        string='Nom Technique du Modèle',
        related='model_id.model',
        store=True,
        readonly=True,
        help='Nom technique du modèle (ex: sale.order)'
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Désactiver pour masquer cette configuration'
    )

    # Configuration du mapping automatique
    auto_map_fields = fields.Boolean(
        string='Mapping Automatique',
        default=True,
        help='Activer le mapping automatique des champs du modèle vers les variables'
    )

    field_mapping_ids = fields.One2many(
        'lettre.motivation.field.mapping',
        'binding_id',
        string='Mappings de Champs',
        help='Configuration du mapping des champs Odoo vers les variables'
    )

    # Configuration du bouton
    button_text = fields.Char(
        string='Texte du Bouton',
        default='Générer Lettre',
        help='Texte affiché sur le bouton dans le formulaire'
    )

    button_position = fields.Selection(
        [
            ('header', 'En-tête'),
            ('footer', 'Pied de page'),
        ],
        string='Position du Bouton',
        default='header',
        help='Où afficher le bouton dans le formulaire'
    )

    # Statistiques
    instance_count = fields.Integer(
        string='Nombre de Lettres Générées',
        compute='_compute_instance_count',
        help='Nombre de lettres générées avec ce binding'
    )

    @api.depends('template_id', 'model_name')
    def _compute_instance_count(self):
        """Compter les instances générées pour ce binding"""
        for binding in self:
            if binding.model_name:
                # Compter les instances liées à ce modèle
                # On utilise le template_id et le model_name pour filtrer
                domain = [
                    ('template_id', '=', binding.template_id.id),
                ]
                # Ajouter le filtre selon le modèle
                if binding.model_name == 'sale.order':
                    domain.append(('sale_order_id', '!=', False))
                elif binding.model_name == 'account.move':
                    domain.append(('account_move_id', '!=', False))
                # Ajouter d'autres modèles si nécessaire
                
                binding.instance_count = self.env['lettre.motivation.instance'].search_count(domain)
            else:
                binding.instance_count = 0

    @api.constrains('template_id', 'model_id')
    def _check_unique_binding(self):
        """Vérifier qu'il n'y a pas de doublon template+modèle"""
        for binding in self:
            existing = self.search([
                ('template_id', '=', binding.template_id.id),
                ('model_id', '=', binding.model_id.id),
                ('id', '!=', binding.id),
                ('active', '=', True),
            ])
            if existing:
                raise ValidationError(
                    _("Une configuration active existe déjà pour ce template et ce modèle.")
                )

    def action_view_instances(self):
        """Ouvrir la vue des instances générées"""
        self.ensure_one()
        domain = [('template_id', '=', self.template_id.id)]
        
        # Filtrer selon le modèle
        if self.model_name == 'sale.order':
            domain.append(('sale_order_id', '!=', False))
        elif self.model_name == 'account.move':
            domain.append(('account_move_id', '!=', False))
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'Lettres Générées - {self.name}',
            'res_model': 'lettre.motivation.instance',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {'default_template_id': self.template_id.id},
        }

