# -*- coding: utf-8 -*-
"""
Contrôleur pour les téléchargements de clés et licences
"""

from odoo import http
from odoo.http import request, content_disposition


class DownloadController(http.Controller):
    """Contrôleur pour télécharger les clés et licences"""

    @http.route('/web/content/license.key/<int:key_id>/private_key_pem/download', type='http', auth='user')
    def download_private_key(self, key_id, **kwargs):
        """Télécharge la clé privée"""
        key = request.env['license.key'].browse(key_id)
        
        if not key.exists() or not key.private_key_pem:
            return request.not_found()
        
        return request.make_response(
            key.private_key_pem.encode('utf-8'),
            headers=[
                ('Content-Type', 'application/x-pem-file'),
                ('Content-Disposition', content_disposition('private_key.pem')),
            ]
        )
    
    @http.route('/web/content/license.key/<int:key_id>/public_key_pem/download', type='http', auth='user')
    def download_public_key(self, key_id, **kwargs):
        """Télécharge la clé publique"""
        key = request.env['license.key'].browse(key_id)
        
        if not key.exists() or not key.public_key_pem:
            return request.not_found()
        
        return request.make_response(
            key.public_key_pem.encode('utf-8'),
            headers=[
                ('Content-Type', 'application/x-pem-file'),
                ('Content-Disposition', content_disposition('public_key.pem')),
            ]
        )
    
    @http.route('/web/content/license.license/<int:license_id>/license_blob/download', type='http', auth='user')
    def download_license(self, license_id, filename=None, **kwargs):
        """Télécharge le blob de licence"""
        license_obj = request.env['license.license'].browse(license_id)
        
        if not license_obj.exists() or not license_obj.license_blob:
            return request.not_found()
        
        filename = filename or f"{license_obj.name}.txt"
        
        return request.make_response(
            license_obj.license_blob.encode('utf-8'),
            headers=[
                ('Content-Type', 'text/plain'),
                ('Content-Disposition', content_disposition(filename)),
            ]
        )
