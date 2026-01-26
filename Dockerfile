FROM odoo:18.0

USER root

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python pour alnas-docx
# Note: --break-system-packages est nécessaire pour Python 3.12+ dans Debian
RUN pip3 install --break-system-packages --no-cache-dir \
    docxtpl \
    htmldocx \
    git+https://github.com/tvuotila/docxcompose.git@hotfix/90

USER odoo

