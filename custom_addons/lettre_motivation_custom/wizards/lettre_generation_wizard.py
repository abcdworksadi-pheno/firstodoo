# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json


class LettreMotivationGenerationWizard(models.TransientModel):
    """Wizard pour générer une lettre de motivation"""
    _name = 'lettre.motivation.generation.wizard'
    _description = 'Assistant de Génération de Lettre de Motivation'

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle',
        required=True,
        help='Modèle de lettre à utiliser'
    )

    name = fields.Char(
        string='Nom de la Lettre',
        required=True,
        help='Nom de l\'instance de lettre'
    )

    valeurs_variables = fields.Text(
        string='Valeurs des Variables',
        compute='_compute_valeurs_variables',
        inverse='_inverse_valeurs_variables',
        help='Valeurs JSON des variables'
    )

    variable_ids = fields.One2many(
        'lettre.motivation.generation.wizard.variable',
        'wizard_id',
        string='Variables',
        help='Variables à remplir'
    )

    @api.depends('variable_ids.valeur')
    def _compute_valeurs_variables(self):
        """Calcule les valeurs JSON à partir des champs variables"""
        for wizard in self:
            valeurs = {}
            for var in wizard.variable_ids:
                if var.valeur:
                    valeurs[var.name] = var.valeur
            wizard.valeurs_variables = json.dumps(valeurs, ensure_ascii=False)

    def _inverse_valeurs_variables(self):
        """Met à jour les champs variables à partir du JSON"""
        for wizard in self:
            if wizard.valeurs_variables:
                try:
                    valeurs = json.loads(wizard.valeurs_variables)
                    for var in wizard.variable_ids:
                        if var.name in valeurs:
                            var.valeur = valeurs[var.name]
                except:
                    pass

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Met à jour les variables lorsque le modèle change"""
        if self.template_id:
            variables = []
            for var in self.template_id.variables_ids:
                variables.append((0, 0, {
                    'name': var.name,
                    'label': var.label,
                    'type': var.type,
                    'valeur_par_defaut': var.valeur_par_defaut or '',
                    'required': var.required,
                }))
            self.variable_ids = variables

    def action_generer(self):
        """Génère la lettre de motivation"""
        self.ensure_one()
        
        # Vérifier les variables obligatoires
        for var in self.variable_ids:
            if var.required and not var.valeur:
                raise UserError(_('La variable "%s" est obligatoire!') % var.label)
        
        # Préparer les lignes de variables avec valeurs
        variables_lines = []
        # Créer un mapping nom -> variable_id
        var_mapping = {v.name: v.id for v in self.template_id.variables_ids}
        
        # Utiliser toutes les variables du template, pas seulement celles du wizard
        for template_var in self.template_id.variables_ids:
            # Trouver la valeur correspondante dans le wizard
            wizard_var = self.variable_ids.filtered(lambda v: v.name == template_var.name)
            valeur = ''
            if wizard_var and wizard_var.valeur:
                valeur = wizard_var.valeur
            elif template_var.valeur_par_defaut:
                valeur = template_var.valeur_par_defaut
            
            variables_lines.append((0, 0, {
                'variable_id': template_var.id,
                'valeur': valeur,
                'sequence': 10,
            }))
        
        # Créer l'instance avec les variables
        instance = self.env['lettre.motivation.instance'].create({
            'name': self.name,
            'template_id': self.template_id.id,
            'valeurs_variables': self.valeurs_variables,
            'variables_valeurs_ids': variables_lines,
        })
        
        # Générer le contenu
        instance.action_generer_contenu()
        
        # Retourner la vue de l'instance
        return {
            'type': 'ir.actions.act_window',
            'name': _('Lettre Générée'),
            'res_model': 'lettre.motivation.instance',
            'res_id': instance.id,
            'view_mode': 'form',
            'target': 'current',
        }


class LettreMotivationGenerationWizardVariable(models.TransientModel):
    """Variable dans le wizard de génération"""
    _name = 'lettre.motivation.generation.wizard.variable'
    _description = 'Variable du Wizard'

    wizard_id = fields.Many2one(
        'lettre.motivation.generation.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )

    name = fields.Char(
        string='Nom Technique',
        required=True,
        readonly=True,
        default=''
    )
    
    @api.model
    def default_get(self, fields_list):
        """Valeur par défaut pour éviter les erreurs de validation"""
        res = super().default_get(fields_list)
        if 'name' in fields_list and not res.get('name'):
            res['name'] = ''
        if 'label' in fields_list and not res.get('label'):
            res['label'] = ''
        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        """S'assure que name et label sont toujours remplis"""
        for vals in vals_list:
            if not vals.get('name'):
                vals['name'] = vals.get('label', '').lower().replace(' ', '_') or 'variable'
            if not vals.get('label'):
                vals['label'] = vals.get('name', '').replace('_', ' ').title() or 'Variable'
        return super().create(vals_list)

    label = fields.Char(
        string='Libellé',
        required=True,
        readonly=True,
        default=''
    )

    type = fields.Selection(
        [
            ('texte', 'Texte'),
            ('nombre', 'Nombre'),
            ('date', 'Date'),
            ('tableau', 'Tableau'),
            ('excel', 'Source Excel'),
        ],
        string='Type',
        readonly=True
    )

    valeur = fields.Text(
        string='Valeur',
        help='Valeur à injecter dans la lettre'
    )

    valeur_par_defaut = fields.Text(
        string='Valeur par Défaut',
        readonly=True
    )

    required = fields.Boolean(
        string='Obligatoire',
        readonly=True
    )

