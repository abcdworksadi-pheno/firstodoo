# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LettreMotivationSelectionWizard(models.TransientModel):
    """Wizard pour sélectionner un modèle de lettre depuis une commande"""
    _name = 'lettre.motivation.selection.wizard'
    _description = 'Assistant de Sélection de Modèle de Lettre'

    sale_order_id = fields.Many2one(
        'sale.order',
        string='Commande',
        required=True,
        readonly=True,
        help='Commande depuis laquelle générer la lettre'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle de Lettre',
        required=True,
        domain=[('active', '=', True)],
        help='Sélectionner le modèle de lettre à utiliser'
    )

    format_sortie = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('html', 'HTML'),
            ('docx', 'DOCX'),
        ],
        string='Format de Sortie',
        required=True,
        default='pdf',
        help='Format du fichier à générer'
    )

    @api.model
    def default_get(self, fields_list):
        """Initialiser avec les templates disponibles"""
        res = super().default_get(fields_list)
        
        if 'sale_order_id' in fields_list and not res.get('sale_order_id'):
            # Récupérer depuis le contexte
            sale_order_id = self.env.context.get('default_sale_order_id')
            if sale_order_id:
                res['sale_order_id'] = sale_order_id
        
        # Si un template est fourni dans le contexte, utiliser son format par défaut
        if 'template_id' in self.env.context:
            template = self.env['lettre.motivation.template'].browse(self.env.context['template_id'])
            if template and 'format_sortie' in fields_list and not res.get('format_sortie'):
                res['format_sortie'] = template.format_sortie
        
        return res

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Mettre à jour le format de sortie avec celui du template"""
        if self.template_id:
            self.format_sortie = self.template_id.format_sortie

    def action_generer(self):
        """Génère la lettre avec le modèle sélectionné"""
        self.ensure_one()
        
        if not self.sale_order_id:
            raise UserError(_('Aucune commande sélectionnée'))
        
        if not self.template_id:
            raise UserError(_('Veuillez sélectionner un modèle de lettre'))
        
        # Créer l'instance de lettre
        instance = self.env['lettre.motivation.instance'].create({
            'template_id': self.template_id.id,
            'sale_order_id': self.sale_order_id.id,
            'name': f"{self.template_id.name} - {self.sale_order_id.name}",
            'format_sortie': self.format_sortie,
        })
        
        # Mapper automatiquement les champs de la commande vers les variables
        # S'assurer que toutes les variables sont créées d'abord
        instance._ensure_all_variables_present()
        instance._auto_map_from_sale_order(self.sale_order_id)
        
        # Générer le contenu automatiquement
        instance.action_generer_contenu()
        
        # Générer le fichier dans le format choisi
        instance.action_generer_fichier()
        
        # Retourner la vue de l'instance
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lettre de Motivation'),
            'res_model': 'lettre.motivation.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'target': 'current',
        }

