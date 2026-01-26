# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LettreMotivationInstanceVariable(models.Model):
    """Variable avec valeur pour une instance de lettre"""
    _name = 'lettre.motivation.instance.variable'
    _description = 'Variable d\'Instance de Lettre'
    _order = 'sequence, name'

    instance_id = fields.Many2one(
        'lettre.motivation.instance',
        string='Instance',
        required=True,
        ondelete='cascade'
    )

    variable_id = fields.Many2one(
        'lettre.motivation.variable',
        string='Variable',
        required=True,
        ondelete='cascade'
    )
    
    @api.model
    def default_get(self, fields_list):
        """Valeur par défaut pour variable_id"""
        res = super().default_get(fields_list)
        # Si instance_id est dans le contexte, essayer de trouver une variable
        if 'default_instance_id' in self.env.context and 'variable_id' in fields_list:
            instance_id = self.env.context.get('default_instance_id')
            if instance_id:
                instance = self.env['lettre.motivation.instance'].browse(instance_id)
                if instance.exists() and instance.template_id and instance.template_id.variables_ids:
                    # Prendre la première variable disponible
                    res['variable_id'] = instance.template_id.variables_ids[0].id
        return res
    
    @api.constrains('variable_id')
    def _check_variable_id(self):
        """Vérifie que variable_id est défini"""
        for record in self:
            if not record.variable_id:
                raise ValidationError(_('Le champ Variable est obligatoire!'))
    
    @api.model_create_multi
    def create(self, vals_list):
        """S'assure que variable_id est toujours défini"""
        for vals in vals_list:
            # Si variable_id n'est pas défini, essayer de le trouver
            if not vals.get('variable_id'):
                variable = None
                
                # Méthode 1: Chercher par instance_id et name si instance_id est fourni
                if vals.get('instance_id'):
                    instance = self.env['lettre.motivation.instance'].browse(vals.get('instance_id'))
                    if instance.exists() and instance.template_id:
                        # Chercher par name si fourni
                        if vals.get('name'):
                            variable = instance.template_id.variables_ids.filtered(
                                lambda v: v.name == vals.get('name')
                            )
                            if variable:
                                variable = variable[0]
                        # Si pas de name, prendre la première variable disponible (ne devrait pas arriver)
                        elif instance.template_id.variables_ids:
                            variable = instance.template_id.variables_ids[0]
                
                # Méthode 2: Chercher par name dans toutes les variables (fallback)
                if not variable and vals.get('name'):
                    variable = self.env['lettre.motivation.variable'].search([
                        ('name', '=', vals.get('name'))
                    ], limit=1)
                
                # Si on a trouvé une variable, l'assigner
                if variable:
                    vals['variable_id'] = variable.id
                else:
                    # Si on ne peut pas trouver la variable, lever une erreur
                    raise ValidationError(_(
                        'Impossible de trouver la variable. '
                        'Assurez-vous que le modèle est sélectionné et que les variables sont définies.'
                    ))
        
        return super().create(vals_list)
    
    def write(self, vals):
        """S'assure que variable_id reste défini lors de la mise à jour"""
        # Si on essaie de supprimer variable_id, l'empêcher
        if 'variable_id' in vals and not vals.get('variable_id'):
            raise ValidationError(_('Le champ Variable est obligatoire et ne peut pas être supprimé!'))
        return super().write(vals)
    

    name = fields.Char(
        related='variable_id.name',
        string='Nom Technique',
        readonly=True,
        store=False
    )

    label = fields.Char(
        related='variable_id.label',
        string='Libellé',
        readonly=True,
        store=False
    )

    type = fields.Selection(
        related='variable_id.type',
        string='Type',
        readonly=True,
        store=False
    )

    valeur = fields.Text(
        string='Valeur',
        help='Valeur à injecter dans la lettre'
    )

    valeur_par_defaut = fields.Text(
        related='variable_id.valeur_par_defaut',
        string='Valeur par Défaut',
        readonly=True,
        store=False
    )

    required = fields.Boolean(
        related='variable_id.required',
        string='Obligatoire',
        readonly=True,
        store=False
    )

    sequence = fields.Integer(
        string='Ordre',
        default=10
    )
    
    @api.onchange('instance_id', 'name')
    def _onchange_instance_or_name(self):
        """Remplit automatiquement variable_id si manquant"""
        if not self.variable_id and self.instance_id and self.instance_id.template_id:
            # Chercher par name si disponible
            if self.name:
                variable = self.instance_id.template_id.variables_ids.filtered(
                    lambda v: v.name == self.name
                )
                if variable:
                    self.variable_id = variable[0]
            # Sinon, si on a un label, chercher par label
            elif self.label:
                variable = self.instance_id.template_id.variables_ids.filtered(
                    lambda v: v.label == self.label
                )
                if variable:
                    self.variable_id = variable[0]

