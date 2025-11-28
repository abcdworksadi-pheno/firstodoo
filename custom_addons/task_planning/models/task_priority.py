from odoo import models, fields


class TaskPriority(models.Model):
    """Modèle pour les niveaux de priorité des tâches"""
    _name = 'task.priority'
    _description = 'Priorité de la Tâche'
    _order = 'sequence asc'

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(string='Séquence', default=10)
    color = fields.Integer(string='Couleur')
    description = fields.Text(string='Description')


class TaskTag(models.Model):
    """Modèle pour les étiquettes de tâches"""
    _name = 'task.tag'
    _description = 'Étiquette de Tâche'

    name = fields.Char(string='Nom', required=True)
    color = fields.Integer(string='Couleur')
    description = fields.Text(string='Description')
