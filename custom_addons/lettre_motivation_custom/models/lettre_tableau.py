# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LettreMotivationTableau(models.Model):
    """Tableau dynamique pour les lettres de motivation (niveau 2 et 3)"""
    _name = 'lettre.motivation.tableau'
    _description = 'Tableau Dynamique de Lettre de Motivation'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom du Tableau',
        required=True,
        help='Nom du tableau (ex: Compétences, Expériences)'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle',
        required=True,
        ondelete='cascade',
        help='Modèle de lettre associé'
    )

    variable_name = fields.Char(
        string='Nom de Variable',
        required=True,
        help='Nom de la variable utilisée dans le template (ex: tableau_competences)'
    )

    sequence = fields.Integer(
        string='Ordre',
        default=10,
        help='Ordre d\'affichage du tableau'
    )

    colonnes_ids = fields.One2many(
        'lettre.motivation.tableau.colonne',
        'tableau_id',
        string='Colonnes',
        help='Colonnes du tableau'
    )

    lignes_ids = fields.One2many(
        'lettre.motivation.tableau.ligne',
        'tableau_id',
        string='Lignes',
        help='Lignes de données du tableau'
    )

    source_excel_id = fields.Many2one(
        'lettre.motivation.excel.source',
        string='Source Excel',
        help='Source Excel pour remplir automatiquement le tableau (niveau 3)'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )


class LettreMotivationTableauColonne(models.Model):
    """Colonne d'un tableau dynamique"""
    _name = 'lettre.motivation.tableau.colonne'
    _description = 'Colonne de Tableau'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom Technique',
        required=True,
        help='Nom technique de la colonne (ex: competence)'
    )

    label = fields.Char(
        string='Libellé',
        required=True,
        help='Libellé affiché dans l\'en-tête (ex: Compétence)'
    )

    tableau_id = fields.Many2one(
        'lettre.motivation.tableau',
        string='Tableau',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Ordre',
        default=10,
        help='Ordre d\'affichage de la colonne'
    )

    type_colonne = fields.Selection(
        [
            ('texte', 'Texte'),
            ('nombre', 'Nombre'),
            ('date', 'Date'),
        ],
        string='Type',
        default='texte',
        help='Type de données de la colonne'
    )

    width = fields.Char(
        string='Largeur',
        help='Largeur de la colonne (ex: 100px, 20%)'
    )


class LettreMotivationTableauLigne(models.Model):
    """Ligne d'un tableau dynamique"""
    _name = 'lettre.motivation.tableau.ligne'
    _description = 'Ligne de Tableau'
    _order = 'sequence, id'

    tableau_id = fields.Many2one(
        'lettre.motivation.tableau',
        string='Tableau',
        required=True,
        ondelete='cascade'
    )

    sequence = fields.Integer(
        string='Ordre',
        default=10
    )

    valeurs = fields.Text(
        string='Valeurs',
        required=True,
        help='Valeurs de la ligne au format JSON: {"colonne1": "valeur1", "colonne2": "valeur2"}'
    )

    @api.constrains('valeurs')
    def _check_valeurs_json(self):
        """Vérifie que les valeurs sont au format JSON valide"""
        import json
        for record in self:
            if record.valeurs:
                try:
                    json.loads(record.valeurs)
                except:
                    raise ValidationError(_('Les valeurs doivent être au format JSON valide!'))

