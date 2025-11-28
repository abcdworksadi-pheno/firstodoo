from odoo import models, fields, api
from datetime import datetime


class TaskPlanning(models.Model):
    """Modèle pour gérer les tâches planifiées"""
    _name = 'task.planning'
    _description = 'Planification des Tâches'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date asc'

    # Champs fondamentaux
    name = fields.Char(string='Titre de la tâche', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    
    # Gestion des statuts et priorités
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('completed', 'Complétée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', tracking=True)
    
    priority_id = fields.Many2one('task.priority', string='Priorité', tracking=True)
    
    # Assignation
    assigned_to = fields.Many2one('res.users', string='Assigné à', tracking=True)
    project_id = fields.Many2one('project.project', string='Projet', tracking=True)
    
    # Gestion des dates
    scheduled_date = fields.Date(string='Date planifiée', tracking=True)
    scheduled_start_time = fields.Float(string='Heure de début', help='Heure en format décimal (ex: 14.5 pour 14h30)')
    scheduled_end_time = fields.Float(string='Heure de fin', help='Heure en format décimal')
    duration_hours = fields.Float(string='Durée (heures)', compute='_compute_duration_hours')
    
    start_date = fields.Date(string='Date de début réelle', tracking=True)
    end_date = fields.Date(string='Date de fin réelle', tracking=True)
    deadline = fields.Date(string='Date limite', tracking=True)
    
    # Gestion des ressources
    estimated_hours = fields.Float(string='Heures estimées', tracking=True)
    actual_hours = fields.Float(string='Heures réelles', tracking=True)
    
    # Suivi
    completion_percentage = fields.Integer(
        string='% Complétude',
        default=0,
        tracking=True,
        help='Pourcentage d\'achèvement de la tâche'
    )
    
    tags = fields.Many2many('task.tag', string='Étiquettes')
    
    # Informations supplémentaires
    created_by = fields.Many2one('res.users', string='Créée par', default=lambda self: self.env.user, readonly=True)
    created_date = fields.Datetime(string='Créée le', default=fields.Datetime.now, readonly=True)
    
    # Gestion des tâches dépendantes
    parent_task_id = fields.Many2one('task.planning', string='Tâche parent')
    subtask_ids = fields.One2many('task.planning', 'parent_task_id', string='Sous-tâches')
    
    # Notifications
    send_reminder = fields.Boolean(string='Envoyer des rappels', default=True)
    reminder_days = fields.Integer(string='Rappel (jours avant)', default=1)

    @api.depends('scheduled_start_time', 'scheduled_end_time')
    def _compute_duration_hours(self):
        """Calculer la durée entre les heures de début et de fin"""
        for task in self:
            if task.scheduled_start_time and task.scheduled_end_time:
                task.duration_hours = task.scheduled_end_time - task.scheduled_start_time
            else:
                task.duration_hours = 0

    @api.model
    def create(self, vals):
        """Override de create pour ajouter des fonctionnalités"""
        result = super().create(vals)
        return result

    def write(self, vals):
        """Override de write pour logger les changements"""
        result = super().write(vals)
        return result

    def action_plan(self):
        """Marquer la tâche comme planifiée"""
        self.state = 'planned'

    def action_start(self):
        """Marquer la tâche comme en cours"""
        self.write({
            'state': 'in_progress',
            'start_date': fields.Date.today()
        })

    def action_complete(self):
        """Marquer la tâche comme complétée"""
        self.write({
            'state': 'completed',
            'end_date': fields.Date.today(),
            'completion_percentage': 100
        })

    def action_cancel(self):
        """Annuler la tâche"""
        self.state = 'cancelled'

    def action_reset(self):
        """Réinitialiser la tâche au statut brouillon"""
        self.write({
            'state': 'draft',
            'start_date': None,
            'end_date': None,
            'completion_percentage': 0
        })
