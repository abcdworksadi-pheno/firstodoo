# -*- coding: utf-8 -*-

from odoo import models, fields, api


class employee_mood(models.Model):
    _name = 'employee_mood.employee_mood'
    _description = 'employee_mood.employee_mood'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string="Employée", required=True)
    date = fields.Date(default=fields.Date.today, string="Date", required=True)
    mood = fields.Selection([
        ('1', '😞 Très mauvais'),
        ('2', '🙁 Mauvais'),
        ('3', '😐 Neutre'),
        ('4', '🙂 Bonne'),
        ('5', '😄 Excellente'),
        ('6', '🤩 Superbe'),
    ], string="Humeur", required=True)
    note = fields.Text("Commentaires")
    # Temporary compatibility field: stale views reference `value`.
    value = fields.Integer(string="Value", default=0)


