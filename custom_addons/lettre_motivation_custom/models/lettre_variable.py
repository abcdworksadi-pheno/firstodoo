# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LettreMotivationVariable(models.Model):
    """Variable pour les modèles de lettres de motivation"""
    _name = 'lettre.motivation.variable'
    _description = 'Variable de Lettre de Motivation'
    _order = 'name'

    name = fields.Char(
        string='Nom Technique',
        required=True,
        help='Nom de la variable utilisé dans le template (ex: nom_candidat)'
    )

    label = fields.Char(
        string='Libellé',
        required=True,
        help='Libellé affiché à l\'utilisateur (ex: Nom du candidat)'
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
        required=True,
        default='texte',
        help='Type de la variable'
    )

    valeur_par_defaut = fields.Text(
        string='Valeur par Défaut',
        help='Valeur par défaut de la variable'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle',
        required=True,
        ondelete='cascade',
        help='Modèle de lettre associé'
    )

    required = fields.Boolean(
        string='Obligatoire',
        default=False,
        help='La variable doit être remplie pour générer la lettre'
    )

    help_text = fields.Text(
        string='Aide',
        help='Texte d\'aide pour guider l\'utilisateur'
    )

    _sql_constraints = [
        ('name_template_unique', 'unique(name, template_id)',
         'Une variable avec le même nom existe déjà pour ce modèle!'),
    ]

