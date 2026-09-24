#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$DIR/pdm" ]; then
    cd "$DIR/pdm"
else
    cd "$DIR"
fi

echo "=============================================================================="
echo "      INDUSTRIAL PREDICTIVE MAINTENANCE PLATFORM - WORKSTATION LAUNCHER       "
echo "                 Asset: Turbine Motor Unit A1 (MCH-802X)                      "
echo "=============================================================================="
echo ""

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

IP_ADDR=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "[*] Platform launching on Port 8001..."
echo "  - Local Dashboard URL    : http://localhost:8001"
if [ -n "$IP_ADDR" ]; then
    echo "  - Workstation Network URL: http://${IP_ADDR}:8001"
fi
echo "  - REST API & Swagger Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the platform."
echo "=============================================================================="
echo ""

exec python3 -u -m uvicorn main:app --host 0.0.0.0 --port 8001
