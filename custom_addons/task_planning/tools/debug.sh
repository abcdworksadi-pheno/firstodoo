#!/bin/bash
# Odoo module XML debugging script
# Clear module caches and reload

echo "=== Checking XML files ==="
for f in /mnt/extra-addons/task_planning/views/*.xml /mnt/extra-addons/task_planning/data/*.xml; do
    if [ -f "$f" ]; then
        echo "File: $f"
        head -c 50 "$f" | od -c | head -2
        tail -c 50 "$f" | od -c | head -2
        xmllint --noout "$f" 2>&1 && echo "  ✓ Well-formed" || echo "  ✗ Parse error"
        echo ""
    fi
done

echo "=== Checking __manifest__.py ==="
python3 -c "import sys; sys.path.insert(0, '/mnt/extra-addons'); from task_planning.__manifest__ import *; print('Manifest loaded OK')" 2>&1

echo "=== Clearing Odoo module cache ==="
rm -rf /var/lib/odoo/.local/share/Odoo/*/modules/*task_planning* 2>/dev/null
rm -rf /tmp/odoo* 2>/dev/null
echo "Cache cleared"
