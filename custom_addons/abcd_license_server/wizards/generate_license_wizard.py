# -*- coding: utf-8 -*-
"""
Wizard pour générer rapidement une licence
"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class GenerateLicenseWizard(models.TransientModel):
    """Wizard pour générer une licence rapidement"""
    
    _name = 'generate.license.wizard'
    _description = 'Wizard: Générer une Licence'
    
    client_id = fields.Many2one(
        'license.client',
        string="Client",
        required=True,
        help="Client pour lequel générer la licence"
    )
    
    db_uuid = fields.Char(
        string="UUID Base de Données",
        required=True,
        help=(
            "UUID de la base de données Odoo cible (32 caractères hexadécimaux).\n"
            "Pour l'obtenir : Paramètres > Technique > Paramètres > Paramètres système > database.uuid\n"
            "⚠️ NE PAS copier un blob de licence ici !"
        )
    )
    
    modules = fields.Char(
        string="Modules",
        required=True,
        default="abcd_sales_pro",
        help="Modules séparés par des virgules (ex: abcd_sales_pro,abcd_inventory_plus)"
    )
    
    edition = fields.Selection([
        ('standard', 'Standard'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ], string="Édition", required=True, default='pro')
    
    expiry_days = fields.Integer(
        string="Validité (jours)",
        required=True,
        default=365,
        help="Nombre de jours de validité à partir d'aujourd'hui"
    )
    
    max_users = fields.Integer(
        string="Nombre Maximum d'Utilisateurs",
        default=0,
        help="0 = illimité"
    )
    
    auto_generate_alias = fields.Boolean(
        string="Générer Alias Automatiquement",
        default=True
    )
    
    alias = fields.Char(
        string="Alias Personnalisé",
        help="Laissez vide pour génération automatique"
    )
    
    def action_generate(self):
        """Génère la licence"""
        self.ensure_one()
        
        # Valider l'UUID
        db_uuid = (self.db_uuid or "").strip()
        if not db_uuid:
            raise UserError(_("L'UUID de la base de données est requis."))
        
        # Vérifier que ce n'est pas un blob de licence
        if len(db_uuid) > 64:
            raise UserError(_(
                "L'UUID de la base de données semble être incorrect.\n"
                "Vous avez probablement copié un blob de licence au lieu de l'UUID.\n\n"
                "Pour obtenir l'UUID correct :\n"
                "1. Allez dans Paramètres > Technique > Paramètres > Paramètres système\n"
                "2. Recherchez 'database.uuid'\n"
                "3. Copiez la valeur (32 caractères hexadécimaux)\n"
                "4. Collez-la dans le champ 'UUID Base de Données'"
            ))
        
        # Vérifier le format UUID
        db_uuid_clean = db_uuid.replace('-', '').replace('_', '')
        if len(db_uuid_clean) != 32 or not all(c in '0123456789abcdefABCDEF' for c in db_uuid_clean):
            raise UserError(_(
                "Format d'UUID invalide.\n"
                "L'UUID doit être composé de 32 caractères hexadécimaux.\n"
                "UUID fourni: %s (longueur: %d)\n\n"
                "Pour obtenir l'UUID correct :\n"
                "1. Allez dans Paramètres > Technique > Paramètres > Paramètres système\n"
                "2. Recherchez 'database.uuid'\n"
                "3. Copiez la valeur"
            ) % (db_uuid[:50] + ('...' if len(db_uuid) > 50 else ''), len(db_uuid)))
        
        # Calculer la date d'expiration
        expiry_date = datetime.now() + timedelta(days=self.expiry_days)
        
        # Générer l'alias si nécessaire
        if self.auto_generate_alias and not self.alias:
            year = datetime.now().year
            code = self.client_id.code.upper()
            sequence = self.env['ir.sequence'].next_by_code('license.alias') or '001'
            alias = f"ABCD-LIC-{code}-{year}-{sequence}"
        else:
            alias = self.alias or f"ABCD-LIC-{self.client_id.code}-{datetime.now().year}"
        
        # Créer la licence
        license_obj = self.env['license.license'].create({
            'name': alias,
            'client_id': self.client_id.id,
            'db_uuid': db_uuid_clean.lower(),  # Normaliser en minuscules
            'modules': self.modules,
            'edition': self.edition,
            'expiry_date': expiry_date,
            'max_users': self.max_users,
        })
        
        # Générer le blob
        license_obj.action_generate_license()
        
        # Ouvrir la licence créée
        return {
            'type': 'ir.actions.act_window',
            'name': _('Licence Générée'),
            'res_model': 'license.license',
            'res_id': license_obj.id,
            'view_mode': 'form',
            'target': 'current',
        }
