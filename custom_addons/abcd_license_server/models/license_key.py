# -*- coding: utf-8 -*-
"""
Modèle pour la gestion des clés cryptographiques
"""

import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class LicenseKey(models.Model):
    """Gestion des clés cryptographiques Ed25519"""
    
    _name = 'license.key'
    _description = 'ABCD License Key Pair'
    _order = 'create_date desc'
    
    name = fields.Char(
        string="Nom",
        required=True,
        default="Nouvelle paire de clés",
        help="Nom descriptif de cette paire de clés"
    )
    
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Seule la clé active est utilisée pour générer de nouvelles licences"
    )
    
    private_key_pem = fields.Text(
        string="Clé Privée (PEM)",
        readonly=True,
        help="Clé privée Ed25519 - NE JAMAIS PARTAGER"
    )
    
    public_key_pem = fields.Text(
        string="Clé Publique (PEM)",
        readonly=True
    )
    
    public_key_hex = fields.Char(
        string="Clé Publique (Hex)",
        readonly=True,
        help="Clé publique en format hex (64 caractères) pour Odoo"
    )
    
    key_generated = fields.Boolean(
        string="Clés Générées",
        default=False,
        readonly=True
    )
    
    license_count = fields.Integer(
        string="Licences Générées",
        compute='_compute_license_count',
        store=False  # Recalculé à chaque affichage pour être toujours à jour
    )
    
    def _compute_license_count(self):
        """Compte les licences générées avec cette clé"""
        # Récupérer tous les IDs des clés en cours de calcul
        key_ids = self.ids if self.ids else [r.id for r in self if r.id]
        
        if not key_ids:
            for record in self:
                record.license_count = 0
            return
        
        # Faire une seule requête pour toutes les clés
        license_counts = {}
        for license in self.env['license.license'].search([('key_id', 'in', key_ids)]):
            key_id = license.key_id.id
            license_counts[key_id] = license_counts.get(key_id, 0) + 1
        
        # Assigner les compteurs
        for record in self:
            record.license_count = license_counts.get(record.id, 0)
    
    def action_generate_keys(self):
        """Génère une nouvelle paire de clés Ed25519"""
        self.ensure_one()
        
        if not CRYPTO_AVAILABLE:
            raise UserError(_(
                "La bibliothèque 'cryptography' n'est pas installée.\n"
                "Installez-la avec: pip install cryptography"
            ))
        
        if self.key_generated:
            raise UserError(_(
                "Des clés ont déjà été générées pour cet enregistrement.\n"
                "Créez un nouvel enregistrement pour générer une nouvelle paire de clés."
            ))
        
        try:
            # Générer les clés
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            # Encoder la clé privée (PEM)
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Encoder la clé publique (PEM)
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Encoder la clé publique (raw hex)
            public_raw = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            public_hex = public_raw.hex()
            
            # Désactiver les autres clés actives (une seule clé active à la fois)
            self.env['license.key'].search([
                ('id', '!=', self.id),
                ('active', '=', True)
            ]).write({'active': False})
            
            # Sauvegarder et activer automatiquement cette clé
            self.write({
                'private_key_pem': private_pem.decode('ascii'),
                'public_key_pem': public_pem.decode('ascii'),
                'public_key_hex': public_hex,
                'key_generated': True,
                'active': True,  # Activer automatiquement la nouvelle clé
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _('Clés générées avec succès et activées automatiquement !'),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_("Erreur lors de la génération des clés: %s") % str(e))
    
    def action_download_private_key(self):
        """Télécharge la clé privée (attention: sécurité)"""
        self.ensure_one()
        
        if not self.private_key_pem:
            raise UserError(_("Aucune clé privée disponible."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/license.key/{self.id}/private_key_pem/download?download=true',
            'target': 'self',
        }
    
    def action_download_public_key(self):
        """Télécharge la clé publique"""
        self.ensure_one()
        
        if not self.public_key_pem:
            raise UserError(_("Aucune clé publique disponible."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/license.key/{self.id}/public_key_pem/download?download=true',
            'target': 'self',
        }
    
    def action_deactivate_others(self):
        """Désactive les autres clés et active celle-ci"""
        self.ensure_one()
        
        # Désactiver les autres
        self.env['license.key'].search([
            ('id', '!=', self.id),
            ('active', '=', True)
        ]).write({'active': False})
        
        # Activer celle-ci
        self.write({'active': True})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Succès'),
                'message': _('Clé activée. Les autres clés ont été désactivées.'),
                'type': 'success',
                'sticky': False,
            }
        }
