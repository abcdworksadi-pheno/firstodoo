# -*- coding: utf-8 -*-
"""
Module de vérification de licence ABCD
"""

import base64
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.getLogger(__name__).warning(
        "cryptography library not available. License verification disabled."
    )

_logger = logging.getLogger(__name__)


class AbcdLicenseException(Exception):
    """Exception personnalisée pour les erreurs de licence"""
    pass


class AbcdLicense(models.TransientModel):
    """
    Modèle de vérification de licence ABCD
    Utilisé comme service interne, pas de stockage persistant
    """
    _name = 'abcd.license'
    _description = 'ABCD License Verification Service'

    # Clé publique Ed25519 (hardcodée dans le module)
    # Format: hex string de 32 bytes (64 caractères)
    PUBLIC_KEY_HEX = (
        "c66558597a1da50efd19db0de3e3a438d5322d41ad05b4ab292f82d015dad2da"
        # Clé publique générée - peut être remplacée via ir.config_parameter
    )

    @api.model
    def _get_public_key(self) -> Optional[ed25519.Ed25519PublicKey]:
        """
        Charge et retourne la clé publique Ed25519
        
        Returns:
            Clé publique Ed25519 ou None si indisponible
        """
        if not CRYPTO_AVAILABLE:
            return None
        
        try:
            # Récupérer depuis ir.config_parameter (priorité)
            public_key_hex = self.env['ir.config_parameter'].sudo().get_param(
                'abcd.license.public_key_hex',
                default=self.PUBLIC_KEY_HEX
            )
            
            if not public_key_hex or public_key_hex == "0" * 64:
                _logger.warning("Clé publique ABCD non configurée")
                return None
            
            # Convertir hex -> bytes
            public_key_bytes = bytes.fromhex(public_key_hex)
            
            # Créer l'objet clé publique
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            return public_key
            
        except Exception as e:
            _logger.error(f"Erreur lors du chargement de la clé publique: {e}")
            return None

    @api.model
    def _decode_license_blob(self, license_blob: str) -> Tuple[Dict[str, Any], bytes]:
        """
        Décode un blob de licence
        
        Args:
            license_blob: Blob base64 encodé
        
        Returns:
            tuple: (payload_dict, signature_bytes)
        
        Raises:
            AbcdLicenseException: Si le format est invalide
        """
        try:
            # Nettoyer le blob (enlever espaces, retours à la ligne, etc.)
            # Mais préserver les caractères base64 valides
            license_blob_cleaned = ''.join(c for c in license_blob if c.isalnum() or c in ['+', '/', '='])
            
            # Vérifier que le nettoyage n'a pas supprimé trop de caractères
            if len(license_blob_cleaned) < len(license_blob) * 0.9:
                # Si on a supprimé plus de 10% des caractères, il y a un problème
                raise AbcdLicenseException(
                    "Le blob de licence contient trop de caractères invalides. "
                    "Vérifiez que vous avez copié le blob complet depuis le serveur de licence."
                )
            
            license_blob = license_blob_cleaned
            
            if not license_blob:
                raise AbcdLicenseException("Blob de licence vide après nettoyage")
            
            # Vérifier la longueur minimale (un blob valide fait au moins quelques centaines de caractères)
            if len(license_blob) < 200:
                raise AbcdLicenseException(
                    f"Blob de licence trop court ({len(license_blob)} caractères, minimum attendu: 200). "
                    "Vérifiez que vous avez copié le blob complet depuis le serveur de licence."
                )
            
            # Vérifier que c'est du base64 valide (doit être multiple de 4 après padding)
            # Base64 valide ne contient que A-Z, a-z, 0-9, +, /, et = pour le padding
            if not re.match(r'^[A-Za-z0-9+/]*={0,2}$', license_blob):
                raise AbcdLicenseException(
                    "Le blob de licence contient des caractères invalides pour le base64. "
                    "Vérifiez que vous avez copié le blob complet et correctement."
                )
            
            # Corriger le padding si nécessaire (base64 doit être multiple de 4)
            missing_padding = len(license_blob) % 4
            if missing_padding:
                license_blob += '=' * (4 - missing_padding)
            
            # Décoder base64
            try:
                license_data = base64.b64decode(license_blob.encode('ascii'), validate=True)
            except base64.binascii.Error as e:
                raise AbcdLicenseException(
                    f"Erreur de décodage base64: {e}\n"
                    f"Longueur du blob: {len(license_blob)} caractères\n"
                    "Le blob de licence semble être incomplet ou corrompu.\n"
                    "Vérifiez que vous avez copié le blob COMPLET depuis le serveur de licence "
                    "(onglet 'Blob de Licence' de la licence générée)."
                )
            except Exception as e:
                raise AbcdLicenseException(
                    f"Erreur de décodage base64: {e}\n"
                    "Vérifiez que le blob de licence est complet et correctement copié."
                )
            
            # Séparer JSON et signature (format: JSON + '|||' + SIGNATURE)
            # Utiliser '|||' comme séparateur au lieu de '.' pour éviter les conflits
            # avec les points dans les dates ISO (microsecondes)
            parts = license_data.split(b'|||', 1)
            if len(parts) != 2:
                raise AbcdLicenseException(
                    "Format de licence invalide: séparateur manquant.\n"
                    "Le blob doit être au format BASE64(JSON|||SIGNATURE).\n"
                    "Vérifiez que le blob est complet et correctement formaté."
                )
            
            json_bytes, signature = parts
            
            # Vérifier que le JSON n'est pas vide
            if not json_bytes:
                raise AbcdLicenseException("JSON payload vide dans le blob de licence")
            
            # Parser JSON avec gestion d'erreur détaillée
            try:
                payload = json.loads(json_bytes.decode('utf-8'))
            except json.JSONDecodeError as e:
                # Afficher plus d'informations pour le debugging
                json_preview = json_bytes[:100].decode('utf-8', errors='ignore')
                raise AbcdLicenseException(
                    f"Erreur de parsing JSON: {e}\n"
                    f"Aperçu du JSON: {json_preview}...\n"
                    "Le blob de licence semble être tronqué ou corrompu. "
                    "Vérifiez que vous avez copié le blob complet depuis le serveur de licence."
                )
            
            return payload, signature
            
        except AbcdLicenseException:
            # Relancer les exceptions AbcdLicenseException telles quelles
            raise
        except Exception as e:
            raise AbcdLicenseException(
                f"Erreur lors du décodage du blob de licence: {e}\n"
                "Vérifiez que le blob est complet et correctement formaté."
            )

    @api.model
    def _verify_signature(
        self,
        payload: Dict[str, Any],
        signature: bytes,
        public_key: ed25519.Ed25519PublicKey
    ) -> bool:
        """
        Vérifie la signature du payload
        
        Args:
            payload: Payload JSON
            signature: Signature à vérifier
            public_key: Clé publique
        
        Returns:
            bool: True si signature valide
        """
        try:
            # Recréer le JSON canonique (identique à la génération)
            json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            # Vérifier la signature
            public_key.verify(signature, json_bytes)
            return True
            
        except InvalidSignature:
            _logger.warning("Signature de licence invalide")
            return False
        except Exception as e:
            _logger.error(f"Erreur lors de la vérification de signature: {e}")
            return False

    @api.model
    def _get_db_uuid(self) -> str:
        """
        Récupère l'UUID de la base de données Odoo et le normalise
        
        Returns:
            str: UUID de la base normalisé (sans tirets, en minuscules)
        """
        # Odoo stocke l'UUID dans ir.config_parameter
        db_uuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        if not db_uuid:
            # Fallback: générer un UUID stable depuis le nom de la base
            db_name = config.get('db_name', 'odoo')
            # Hash simple pour stabilité (pas sécurisé, mais pour fallback)
            import hashlib
            db_uuid = hashlib.md5(db_name.encode()).hexdigest()
            _logger.warning(f"UUID base non trouvé, utilisation du fallback: {db_uuid}")
        
        # Normaliser l'UUID : enlever tirets et underscores, convertir en minuscules
        db_uuid_normalized = db_uuid.replace('-', '').replace('_', '').lower()
        return db_uuid_normalized

    @api.model
    def _check_expiry(self, expiry_str: str) -> Tuple[bool, Optional[str]]:
        """
        Vérifie si la licence est expirée
        
        Args:
            expiry_str: Date d'expiration ISO 8601
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Parser la date d'expiration
            expiry_str_normalized = expiry_str.replace('Z', '+00:00')
            expiry_dt = datetime.fromisoformat(expiry_str_normalized)
            
            # S'assurer que la date d'expiration est "aware" (avec timezone)
            # Si elle est "naive" (sans timezone), on assume UTC
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=timezone.utc)
            
            # Date actuelle UTC
            now = datetime.now(timezone.utc)
            
            if expiry_dt < now:
                # Vérifier la période de grâce
                grace_days = int(self.env['ir.config_parameter'].sudo().get_param(
                    'abcd.license.grace_period_days',
                    default='7'
                ))
                
                grace_end = expiry_dt + timedelta(days=grace_days)
                
                if now > grace_end:
                    # Expirée au-delà de la période de grâce
                    expiry_date_fr = expiry_dt.strftime('%d/%m/%Y')
                    return False, f"La licence a expiré le {expiry_date_fr}. Contactez votre éditeur ABCD."
                else:
                    # En période de grâce
                    _logger.warning(f"Licence expirée mais en période de grâce jusqu'au {grace_end}")
                    return True, None
            else:
                return True, None
                
        except Exception as e:
            _logger.error(f"Erreur lors de la vérification d'expiration: {e}")
            return False, "Erreur lors de la vérification de la date d'expiration."

    @api.model
    def _check_user_quota(self, max_users: int) -> Tuple[bool, Optional[str]]:
        """
        Vérifie le quota d'utilisateurs
        
        Args:
            max_users: Nombre maximum d'utilisateurs autorisés (0 = illimité)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if max_users == 0:
            return True, None
        
        # Compter les utilisateurs actifs
        active_users = self.env['res.users'].sudo().search_count([
            ('active', '=', True),
            ('id', '!=', 1)  # Exclure l'admin système
        ])
        
        if active_users > max_users:
            return False, (
                f"Quota d'utilisateurs dépassé ({active_users}/{max_users}). "
                "Contactez votre éditeur ABCD pour augmenter votre licence."
            )
        
        return True, None

    @api.model
    def _get_cached_license_info(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les informations de licence depuis le cache base (24h)
        
        Args:
            cache_key: Clé de cache
        
        Returns:
            dict ou None
        """
        # Cache dans ir.config_parameter avec timestamp
        cache_param = self.env['ir.config_parameter'].sudo().get_param(
            f'abcd.license.cache.{cache_key}'
        )
        
        if not cache_param:
            return None
        
        try:
            cache_data = json.loads(cache_param)
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            
            # Cache valide 24h
            if datetime.now(timezone.utc) - cache_time < timedelta(hours=24):
                return cache_data['payload']
            
        except Exception:
            pass
        
        return None

    @api.model
    def _set_cached_license_info(self, cache_key: str, payload: Dict[str, Any]):
        """
        Met en cache les informations de licence (24h)
        
        Args:
            cache_key: Clé de cache
            payload: Payload de licence
        """
        cache_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'payload': payload
        }
        
        self.env['ir.config_parameter'].sudo().set_param(
            f'abcd.license.cache.{cache_key}',
            json.dumps(cache_data)
        )

    @api.model
    def _verify_license_internal(self, module_name: str = None) -> Dict[str, Any]:
        """
        Vérifie la licence de manière interne (avec cache)
        
        Args:
            module_name: Nom du module à vérifier (optionnel)
        
        Returns:
            dict: Informations de licence validées
        
        Raises:
            AbcdLicenseException: Si la licence est invalide
        """
        # Récupérer le blob de licence
        license_blob = self.env['ir.config_parameter'].sudo().get_param(
            'abcd.license.blob'
        )
        
        if not license_blob:
            raise AbcdLicenseException(
                "Aucune licence ABCD configurée. Contactez votre éditeur."
            )
        
        # Nettoyer le blob (enlever espaces, retours à la ligne)
        license_blob = license_blob.strip().replace('\n', '').replace('\r', '').replace(' ', '')
        
        if not license_blob:
            raise AbcdLicenseException(
                "Blob de licence vide après nettoyage. "
                "Vérifiez que le paramètre 'abcd.license.blob' contient un blob valide."
            )
        
        # Cache base (24h)
        cache_key = f"license_{hash(license_blob)}"
        
        # Vérifier le cache base (24h)
        cached_payload = self._get_cached_license_info(cache_key)
        if cached_payload:
            payload = cached_payload
            _logger.debug("Licence validée depuis le cache base")
        else:
            # Décoder et vérifier
            payload, signature = self._decode_license_blob(license_blob)
            
            # Vérifier la signature
            public_key = self._get_public_key()
            if not public_key:
                raise AbcdLicenseException(
                    "Configuration de licence incomplète. Contactez le support ABCD."
                )
            
            if not self._verify_signature(payload, signature, public_key):
                raise AbcdLicenseException(
                    "Licence invalide ou corrompue. Contactez votre éditeur ABCD."
                )
            
            # Mettre en cache
            self._set_cached_license_info(cache_key, payload)
        
        # Vérifier l'UUID de la base
        db_uuid = self._get_db_uuid()
        # Normaliser l'UUID de la licence pour la comparaison
        license_uuid = (payload.get('db_uuid') or '').replace('-', '').replace('_', '').lower()
        
        if license_uuid != db_uuid:
            raise AbcdLicenseException(
                f"Licence non valide pour cette base de données. "
                f"UUID attendu: {payload.get('db_uuid')}, UUID actuel: {self.env['ir.config_parameter'].sudo().get_param('database.uuid')}"
            )
        
        # Vérifier l'expiration
        expiry = payload.get('expiry')
        if expiry:
            is_valid, error_msg = self._check_expiry(expiry)
            if not is_valid:
                raise AbcdLicenseException(error_msg or "Licence expirée.")
        
        # Vérifier le module si spécifié
        if module_name:
            modules = payload.get('modules', [])
            if module_name not in modules:
                raise AbcdLicenseException(
                    f"Le module '{module_name}' n'est pas autorisé par cette licence. "
                    f"Modules autorisés: {', '.join(modules)}"
                )
        
        # Vérifier le quota utilisateurs
        max_users = payload.get('max_users', 0)
        if max_users:
            is_valid, error_msg = self._check_user_quota(max_users)
            if not is_valid:
                raise AbcdLicenseException(error_msg or "Quota utilisateurs dépassé.")
        
        return payload

    @api.model
    def check_license(self, module_name: str = None) -> bool:
        """
        API publique de vérification de licence
        
        Args:
            module_name: Nom du module à vérifier (optionnel)
        
        Returns:
            bool: True si licence valide
        
        Raises:
            UserError: Si la licence est invalide (message utilisateur-friendly)
        """
        try:
            payload = self._verify_license_internal(module_name)
            _logger.debug(f"Licence validée pour module: {module_name}")
            return True
            
        except AbcdLicenseException as e:
            # Convertir en UserError pour affichage utilisateur
            raise UserError(str(e))
        except Exception as e:
            _logger.error(f"Erreur inattendue lors de la vérification de licence: {e}", exc_info=True)
            # En cas d'erreur inattendue, ne pas bloquer (fail-open avec log)
            # Mais loguer l'erreur pour investigation
            return True  # Fail-open pour ne pas bloquer Odoo

    @api.model
    def get_license_info(self) -> Dict[str, Any]:
        """
        Récupère les informations de la licence (sans validation stricte)
        
        Returns:
            dict: Informations de licence ou {}
        """
        try:
            return self._verify_license_internal()
        except Exception:
            return {}
