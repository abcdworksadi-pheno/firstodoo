# -*- coding: utf-8 -*-
"""
Modèle principal pour les licences ABCD
"""

import base64
import json
import logging
from datetime import datetime, timezone
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class License(models.Model):
    """Licence ABCD générée"""
    
    _name = 'license.license'
    _description = 'ABCD License'
    _order = 'create_date desc'
    
    name = fields.Char(
        string="Alias",
        required=True,
        index=True,
        help="Alias lisible de la licence (ex: ABCD-LIC-CLIENTX-2025)"
    )
    
    client_id = fields.Many2one(
        'license.client',
        string="Client",
        required=True,
        ondelete='restrict',
        help="Client pour lequel cette licence est générée"
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
        string="Modules Autorisés",
        required=True,
        help="Liste des modules séparés par des virgules (ex: abcd_sales_pro,abcd_inventory_plus)"
    )
    
    modules_list = fields.Text(
        string="Modules (Liste)",
        compute='_compute_modules_list',
        help="Liste formatée des modules"
    )
    
    edition = fields.Selection([
        ('standard', 'Standard'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ], string="Édition", required=True, default='standard')
    
    expiry_date = fields.Datetime(
        string="Date d'Expiration",
        required=True,
        help="Date et heure d'expiration de la licence (UTC)"
    )
    
    max_users = fields.Integer(
        string="Nombre Maximum d'Utilisateurs",
        default=0,
        help="0 = illimité"
    )
    
    license_blob = fields.Text(
        string="Blob de Licence",
        readonly=True,
        help="Blob de licence encodé en base64"
    )
    
    license_blob_length = fields.Integer(
        string="Longueur du Blob",
        compute="_compute_license_blob_length",
        help="Longueur du blob de licence en caractères"
    )
    
    @api.depends('license_blob')
    def _compute_license_blob_length(self):
        """Calcule la longueur du blob de licence"""
        for record in self:
            record.license_blob_length = len(record.license_blob) if record.license_blob else 0
    
    public_key_hex = fields.Char(
        string="Clé Publique Utilisée",
        readonly=True,
        help="Clé publique utilisée pour générer cette licence"
    )
    
    key_id = fields.Many2one(
        'license.key',
        string="Paire de Clés",
        readonly=True,
        help="Paire de clés utilisée pour générer cette licence"
    )
    
    issued_at = fields.Datetime(
        string="Date de Génération",
        readonly=True,
        default=fields.Datetime.now
    )
    
    issued_by = fields.Many2one(
        'res.users',
        string="Généré par",
        readonly=True,
        default=lambda self: self.env.user
    )
    
    # Champs calculés pour analyses
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('expired', 'Expirée'),
        ('expiring_soon', 'Expire Bientôt'),
    ], string="Statut", compute='_compute_state', store=True, index=True)
    
    days_until_expiry = fields.Integer(
        string="Jours jusqu'à Expiration",
        compute='_compute_days_until_expiry',
        store=True,
        help="Nombre de jours restants avant expiration"
    )
    
    is_expired = fields.Boolean(
        string="Expirée",
        compute='_compute_state',
        store=True
    )
    
    is_expiring_soon = fields.Boolean(
        string="Expire Bientôt",
        compute='_compute_state',
        store=True
    )
    
    module_count = fields.Integer(
        string="Nombre de Modules",
        compute='_compute_module_count',
        store=True
    )
    
    @api.depends('expiry_date', 'license_blob')
    def _compute_state(self):
        """Calcule le statut de la licence"""
        now = fields.Datetime.now()
        for record in self:
            if not record.license_blob:
                record.state = 'draft'
                record.is_expired = False
                record.is_expiring_soon = False
            elif not record.expiry_date:
                record.state = 'active'
                record.is_expired = False
                record.is_expiring_soon = False
            else:
                days_left = (record.expiry_date - now).days
                if days_left < 0:
                    record.state = 'expired'
                    record.is_expired = True
                    record.is_expiring_soon = False
                elif days_left <= 30:
                    record.state = 'expiring_soon'
                    record.is_expired = False
                    record.is_expiring_soon = True
                else:
                    record.state = 'active'
                    record.is_expired = False
                    record.is_expiring_soon = False
    
    @api.depends('expiry_date')
    def _compute_days_until_expiry(self):
        """Calcule le nombre de jours jusqu'à expiration"""
        now = fields.Datetime.now()
        for record in self:
            if record.expiry_date:
                delta = record.expiry_date - now
                record.days_until_expiry = delta.days
            else:
                record.days_until_expiry = 0
    
    @api.depends('modules')
    def _compute_module_count(self):
        """Compte le nombre de modules autorisés"""
        for record in self:
            if record.modules:
                modules_list = [m.strip() for m in record.modules.split(',') if m.strip()]
                record.module_count = len(modules_list)
            else:
                record.module_count = 0
    
    notes = fields.Text(
        string="Notes",
        help="Notes internes sur cette licence"
    )
    
    @api.depends('modules')
    def _compute_modules_list(self):
        """Formate la liste des modules"""
        for record in self:
            if record.modules:
                modules = [m.strip() for m in record.modules.split(',')]
                record.modules_list = '\n'.join(f'- {m}' for m in modules)
            else:
                record.modules_list = ''
    
    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        """Vérifie que la date d'expiration est dans le futur"""
        for record in self:
            if record.expiry_date and record.expiry_date <= fields.Datetime.now():
                raise ValidationError(_("La date d'expiration doit être dans le futur."))
    
    @api.constrains('max_users')
    def _check_max_users(self):
        """Vérifie que max_users est positif"""
        for record in self:
            if record.max_users < 0:
                raise ValidationError(_("Le nombre maximum d'utilisateurs doit être positif ou zéro (illimité)."))
    
    def _get_active_key(self):
        """
        Récupère la clé active pour la génération de licence
        
        Garantit qu'une seule clé active est utilisée.
        Si plusieurs clés sont actives, utilise la plus récente.
        """
        active_keys = self.env['license.key'].search([
            ('active', '=', True),
            ('key_generated', '=', True)
        ], order='create_date desc')
        
        if not active_keys:
            raise UserError(_(
                "Aucune clé active trouvée.\n"
                "Générez d'abord une paire de clés et activez-la."
            ))
        
        # Si plusieurs clés sont actives, désactiver les anciennes et garder la plus récente
        if len(active_keys) > 1:
            # Désactiver toutes sauf la plus récente
            active_keys[1:].write({'active': False})
            # Logger un avertissement
            _logger.warning(
                f"Plusieurs clés actives détectées. "
                f"Utilisation de la clé la plus récente (ID: {active_keys[0].id}). "
                f"Les autres ont été désactivées."
            )
        
        return active_keys[0]
    
    def _generate_license_blob(self, key):
        """Génère le blob de licence"""
        if not CRYPTO_AVAILABLE:
            raise UserError(_(
                "La bibliothèque 'cryptography' n'est pas installée.\n"
                "Installez-la avec: pip install cryptography"
            ))
        
        # Charger la clé privée
        try:
            private_key = serialization.load_pem_private_key(
                key.private_key_pem.encode('ascii'),
                password=None
            )
        except Exception as e:
            raise UserError(_("Erreur lors du chargement de la clé privée: %s") % str(e))
        
        # Préparer les modules
        modules_list = [m.strip() for m in self.modules.split(',') if m.strip()]
        modules_list = sorted(modules_list)  # Tri pour JSON canonique
        
        # Créer le payload avec validation des valeurs
        # S'assurer que tous les champs sont valides
        company_name = self.client_id.name or ""
        alias = self.name or ""
        
        # Valider que db_uuid est un UUID valide (32 caractères hexadécimaux)
        db_uuid = (self.db_uuid or "").strip()
        if not db_uuid:
            raise UserError(_("L'UUID de la base de données est requis."))
        
        # Vérifier que ce n'est pas un blob de licence (qui serait beaucoup plus long)
        if len(db_uuid) > 64:
            raise UserError(_(
                "L'UUID de la base de données semble être incorrect.\n"
                "Vous avez probablement copié un blob de licence au lieu de l'UUID.\n\n"
                "Pour obtenir l'UUID correct :\n"
                "1. Allez dans Paramètres > Technique > Paramètres > Paramètres système\n"
                "2. Recherchez 'database.uuid'\n"
                "3. Copiez la valeur (32 caractères hexadécimaux)\n"
                "4. Collez-la dans le champ 'UUID Base de Données' de la licence"
            ))
        
        # Vérifier le format UUID (32 caractères hexadécimaux, optionnellement avec tirets)
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
        
        payload = {
            "issuer": "ABCD",
            "company": company_name,
            "db_uuid": db_uuid_clean.lower(),  # Normaliser en minuscules
            "modules": modules_list,
            "edition": self.edition or "standard",
            "expiry": self.expiry_date.isoformat() if self.expiry_date else "",
            "max_users": int(self.max_users) if self.max_users else 0,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "alias": alias
        }
        
        # Créer le JSON canonique avec gestion d'erreur
        try:
            json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            _logger.error(f"Erreur lors de la création du JSON: {e}")
            _logger.error(f"Payload: {payload}")
            raise UserError(_(
                "Erreur lors de la création du JSON de licence.\n"
                "Vérifiez que tous les champs sont correctement remplis.\n"
                "Erreur: %s"
            ) % str(e))
        
        json_bytes = json_str.encode('utf-8')
        
        # Logger pour debug
        _logger.info(f"JSON généré (longueur: {len(json_bytes)} bytes)")
        _logger.debug(f"Aperçu JSON: {json_str[:200]}...")
        
        # Vérifier que le JSON peut être re-parsé (auto-validation)
        try:
            test_payload = json.loads(json_str)
            _logger.info("JSON auto-validation réussie avant encodage")
            _logger.debug(f"JSON complet (longueur: {len(json_str)}): {json_str}")
        except json.JSONDecodeError as e:
            _logger.error(f"JSON invalide généré! Erreur: {e}")
            _logger.error(f"JSON complet (longueur: {len(json_str)}): {json_str}")
            _logger.error(f"Caractères autour de l'erreur: {json_str[max(0, e.pos-50):e.pos+50]}")
            raise UserError(_(
                "Le JSON généré est invalide.\n"
                "Erreur: %s à la position %d\n"
                "Vérifiez les données de la licence."
            ) % (e.msg, e.pos))
        
        # Signer
        try:
            signature = private_key.sign(json_bytes)
            _logger.debug(f"Signature générée (longueur: {len(signature)} bytes)")
        except Exception as e:
            _logger.error(f"Erreur lors de la signature: {e}")
            raise UserError(_("Erreur lors de la signature de la licence: %s") % str(e))
        
        # Assembler: JSON + '|||' + SIGNATURE
        # Utiliser '|||' comme séparateur au lieu de '.' pour éviter les conflits
        # avec les points dans les dates ISO (microsecondes)
        SEPARATOR = b'|||'
        license_data = json_bytes + SEPARATOR + signature
        _logger.info(f"Données de licence assemblées (longueur: {len(license_data)} bytes)")
        _logger.debug(f"JSON bytes: {len(json_bytes)} bytes, Signature: {len(signature)} bytes")
        
        # Encoder en base64
        try:
            license_blob = base64.b64encode(license_data).decode('ascii')
            _logger.info(f"Blob généré (longueur: {len(license_blob)} caractères)")
            
            # Vérification immédiate : décoder et vérifier le JSON
            test_decode = base64.b64decode(license_blob.encode('ascii'), validate=True)
            test_parts = test_decode.split(SEPARATOR, 1)
            if len(test_parts) == 2:
                test_json = test_parts[0].decode('utf-8')
                _logger.info(f"Vérification immédiate: JSON décodé (longueur: {len(test_json)} caractères)")
                try:
                    json.loads(test_json)
                    _logger.info("Vérification immédiate: JSON valide après encodage/décodage")
                except json.JSONDecodeError as e:
                    _logger.error(f"Vérification immédiate échouée: {e}")
                    _logger.error(f"JSON décodé (longueur: {len(test_json)}): {test_json}")
                    raise ValueError(f"JSON invalide après encodage/décodage: {e}")
        except Exception as e:
            _logger.error(f"Erreur lors de l'encodage base64: {e}")
            raise UserError(_("Erreur lors de l'encodage base64: %s") % str(e))
        
        return license_blob
    
    def action_generate_license(self):
        """Génère le blob de licence"""
        self.ensure_one()
        
        if self.license_blob:
            raise UserError(_(
                "Une licence a déjà été générée pour cet enregistrement.\n"
                "Créez un nouvel enregistrement pour générer une nouvelle licence."
            ))
        
        # Récupérer la clé active
        key = self._get_active_key()
        
        # Générer le blob
        try:
            license_blob = self._generate_license_blob(key)
            
            # Valider que le blob peut être décodé (auto-vérification)
            try:
                _logger.info(f"Validation du blob (longueur: {len(license_blob)} caractères)")
                license_data = base64.b64decode(license_blob.encode('ascii'), validate=True)
                _logger.info(f"Blob décodé (longueur: {len(license_data)} bytes)")
                
                parts = license_data.split(b'|||', 1)
                if len(parts) != 2:
                    _logger.error(f"Format invalide: séparateur manquant. Nombre de parties: {len(parts)}")
                    _logger.error(f"Données décodées (premiers 200 bytes): {license_data[:200]}")
                    raise ValueError("Format invalide: séparateur manquant")
                
                json_bytes, signature = parts
                _logger.info(f"JSON extrait (longueur: {len(json_bytes)} bytes)")
                _logger.info(f"Signature extraite (longueur: {len(signature)} bytes)")
                
                # Vérifier que le JSON n'est pas vide
                if not json_bytes:
                    raise ValueError("JSON vide après extraction")
                
                # Décoder le JSON en string pour validation
                json_str = json_bytes.decode('utf-8')
                _logger.debug(f"JSON string (longueur: {len(json_str)} caractères): {json_str}")
                
                # Vérifier que le JSON est valide
                try:
                    payload = json.loads(json_str)
                    _logger.info(f"JSON valide. Payload contient {len(payload)} champs")
                except json.JSONDecodeError as json_err:
                    _logger.error(f"Erreur JSON à la position {json_err.pos}: {json_err.msg}")
                    _logger.error(f"JSON complet (longueur: {len(json_str)}): {json_str}")
                    _logger.error(f"Caractères autour de l'erreur: {json_str[max(0, json_err.pos-20):json_err.pos+20]}")
                    raise ValueError(f"JSON invalide: {json_err.msg} à la position {json_err.pos}")
                    
            except base64.binascii.Error as e:
                _logger.error(f"Erreur base64: {e}")
                raise UserError(_(
                    "Erreur de décodage base64 lors de la validation: %s\n"
                    "Le blob généré semble être corrompu."
                ) % str(e))
            except ValueError as e:
                _logger.error(f"Erreur de validation: {e}")
                raise UserError(_(
                    "Erreur lors de la validation du blob généré: %s\n"
                    "Le blob semble être corrompu. Veuillez réessayer."
                ) % str(e))
            except Exception as e:
                _logger.error(f"Erreur inattendue lors de la validation: {e}", exc_info=True)
                raise UserError(_(
                    "Erreur inattendue lors de la validation du blob: %s\n"
                    "Veuillez contacter le support technique."
                ) % str(e))
            
            # Sauvegarder avec vérification post-sauvegarde
            _logger.info(f"Sauvegarde du blob (longueur avant sauvegarde: {len(license_blob)} caractères)")
            self.write({
                'license_blob': license_blob,
                'public_key_hex': key.public_key_hex,
                'key_id': key.id,
            })
            
            # Vérifier que le blob a bien été sauvegardé (lecture depuis la base)
            self.invalidate_recordset(['license_blob'])
            saved_blob = self.license_blob
            if not saved_blob:
                raise UserError(_(
                    "Le blob de licence n'a pas pu être sauvegardé.\n"
                    "Vérifiez les logs pour plus de détails."
                ))
            
            if len(saved_blob) != len(license_blob):
                _logger.error(
                    f"Blob tronqué lors de la sauvegarde! "
                    f"Original: {len(license_blob)} caractères, "
                    f"Sauvegardé: {len(saved_blob)} caractères"
                )
                raise UserError(_(
                    "Le blob de licence a été tronqué lors de la sauvegarde.\n"
                    "Longueur originale: %d caractères\n"
                    "Longueur sauvegardée: %d caractères\n"
                    "Veuillez réessayer ou contacter le support."
                ) % (len(license_blob), len(saved_blob)))
            
            _logger.info(f"Blob sauvegardé avec succès (longueur: {len(saved_blob)} caractères)")
            
            # Forcer le recalcul du license_count de la clé
            # En invalidant le cache et en recalculant immédiatement
            key.invalidate_recordset(['license_count'])
            key._compute_license_count()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Succès'),
                    'message': _(
                        'Licence générée avec succès !\n'
                        'Longueur du blob: %d caractères\n'
                        'Le blob est valide et prêt à être utilisé.'
                    ) % len(license_blob),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_("Erreur lors de la génération de la licence: %s") % str(e))
    
    def action_copy_license_blob(self):
        """Copie le blob dans le presse-papiers via JavaScript"""
        self.ensure_one()
        
        if not self.license_blob:
            raise UserError(_("Aucune licence générée pour cet enregistrement."))
        
        # Retourner une action JavaScript pour copier dans le presse-papiers
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Instructions de Copie'),
                'message': _(
                    'Pour copier le blob de licence :\n'
                    '1. Allez dans l\'onglet "Blob de Licence"\n'
                    '2. Cliquez dans le champ du blob\n'
                    '3. Sélectionnez TOUT le texte (Ctrl+A)\n'
                    '4. Copiez (Ctrl+C)\n'
                    '5. Collez dans le paramètre abcd.license.blob\n\n'
                    '⚠️ IMPORTANT : Copiez TOUT le blob, sans rien oublier !'
                ),
                'type': 'warning',
                'sticky': True,
            }
        }
    
    def action_download_license(self):
        """Télécharge la licence sous forme de fichier texte"""
        self.ensure_one()
        
        if not self.license_blob:
            raise UserError(_("Aucune licence générée pour cet enregistrement."))
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/license.license/{self.id}/license_blob/download?filename={self.name}.txt&download=true',
            'target': 'self',
        }
    
    def action_generate_alias(self):
        """Génère automatiquement un alias pour la licence"""
        self.ensure_one()
        
        if not self.client_id:
            raise UserError(_("Sélectionnez d'abord un client."))
        
        # Générer l'alias: ABCD-LIC-{CODE_CLIENT}-{ANNEE}
        year = datetime.now().year
        code = self.client_id.code.upper()
        sequence = self.env['ir.sequence'].next_by_code('license.alias') or '001'
        
        alias = f"ABCD-LIC-{code}-{year}-{sequence}"
        
        self.write({'name': alias})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Alias généré'),
                'message': _('Alias généré: %s') % alias,
                'type': 'success',
                'sticky': False,
            }
        }
