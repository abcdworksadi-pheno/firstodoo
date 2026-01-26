# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LettreMotivationFieldMapping(models.Model):
    """Mapping entre un champ Odoo et une variable de template"""
    _name = 'lettre.motivation.field.mapping'
    _description = 'Mapping Champs Odoo → Variables'
    _order = 'sequence, id'

    binding_id = fields.Many2one(
        'lettre.motivation.template.binding',
        string='Configuration',
        required=True,
        ondelete='cascade',
        help='Configuration de binding à laquelle appartient ce mapping'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        related='binding_id.template_id',
        store=True,
        readonly=True,
        help='Template associé'
    )

    variable_id = fields.Many2one(
        'lettre.motivation.variable',
        string='Variable',
        required=True,
        domain="[('template_id', '=', template_id)]",
        help='Variable du template à remplir'
    )

    model_field = fields.Char(
        string='Champ du Modèle',
        required=True,
        help='Chemin du champ dans le modèle (ex: partner_id.name, amount_total, date_order)'
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage'
    )

    # Transformation optionnelle
    transform_function = fields.Selection(
        [
            ('format_date', 'Formater Date'),
            ('format_currency', 'Formater Monnaie'),
            ('format_phone', 'Formater Téléphone'),
            ('format_email', 'Formater Email'),
            ('upper', 'Majuscules'),
            ('lower', 'Minuscules'),
            ('title', 'Titre (Première lettre majuscule)'),
        ],
        string='Fonction de Transformation',
        help='Fonction à appliquer à la valeur avant injection'
    )

    # Valeur par défaut si le champ est vide
    default_value = fields.Char(
        string='Valeur par Défaut',
        help='Valeur à utiliser si le champ est vide ou None'
    )

    # Description
    description = fields.Text(
        string='Description',
        help='Description de ce mapping'
    )

    @api.constrains('model_field', 'binding_id')
    def _check_model_field(self):
        """Vérifier que le champ existe dans le modèle"""
        for mapping in self:
            if not mapping.binding_id.model_id:
                continue
            
            model_name = mapping.binding_id.model_name
            field_path = mapping.model_field.split('.')
            
            # Vérifier le premier champ
            model = self.env[model_name]
            field_name = field_path[0]
            
            if field_name not in model._fields:
                raise ValidationError(
                    _("Le champ '%s' n'existe pas dans le modèle '%s'.") % 
                    (field_name, model_name)
                )
            
            # Si c'est une relation, vérifier les champs suivants
            field = model._fields[field_name]
            if len(field_path) > 1:
                if field.type not in ('many2one', 'one2many', 'many2many'):
                    raise ValidationError(
                        _("Le champ '%s' n'est pas une relation, impossible d'accéder à '%s'.") %
                        (field_name, '.'.join(field_path[1:]))
                    )
                
                # Vérifier le champ suivant dans le modèle lié
                related_model = self.env[field.comodel_name]
                related_field = field_path[1]
                if related_field not in related_model._fields:
                    raise ValidationError(
                        _("Le champ '%s' n'existe pas dans le modèle '%s'.") %
                        (related_field, field.comodel_name)
                    )

    def get_value_from_record(self, record):
        """Récupérer la valeur du champ depuis l'enregistrement"""
        self.ensure_one()
        
        if not record:
            return self.default_value or ''
        
        # Récupérer la valeur en suivant le chemin
        field_path = self.model_field.split('.')
        value = record
        
        for field_name in field_path:
            if not value:
                return self.default_value or ''
            value = getattr(value, field_name, None)
            if value is None:
                return self.default_value or ''
        
        # Appliquer la transformation
        if self.transform_function and value:
            value = self._apply_transform(value, record)
        
        # Convertir en string si nécessaire
        if value is None:
            return self.default_value or ''
        
        return str(value) if not isinstance(value, str) else value

    def _apply_transform(self, value, record):
        """Appliquer la fonction de transformation"""
        if not value:
            return value
        
        if self.transform_function == 'format_date':
            if hasattr(value, 'strftime'):
                return value.strftime('%d/%m/%Y')
            return str(value)
        
        elif self.transform_function == 'format_currency':
            # Utiliser la devise de l'enregistrement si disponible
            currency = getattr(record, 'currency_id', None) or \
                      getattr(record, 'company_id', self.env.company).currency_id
            if currency:
                return f"{value:,.2f} {currency.symbol}"
            return f"{value:,.2f}"
        
        elif self.transform_function == 'format_phone':
            # Format basique de téléphone
            phone = str(value).replace(' ', '').replace('-', '').replace('.', '')
            if len(phone) == 10:
                return f"{phone[:2]} {phone[2:4]} {phone[4:6]} {phone[6:8]} {phone[8:]}"
            return str(value)
        
        elif self.transform_function == 'format_email':
            return str(value).lower()
        
        elif self.transform_function == 'upper':
            return str(value).upper()
        
        elif self.transform_function == 'lower':
            return str(value).lower()
        
        elif self.transform_function == 'title':
            return str(value).title()
        
        return value

