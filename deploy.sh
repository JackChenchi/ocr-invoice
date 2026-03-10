#!/bin/bash

set -e

echo "=========================================="
echo "  OCR Invoice System - One-Click Deploy"
echo "=========================================="

echo "[1/5] Updating system..."
sudo apt update && sudo apt upgrade -y

echo "[2/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
fi

echo "[3/5] Installing docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install docker-compose -y
fi

echo "[4/5] Installing git..."
sudo apt install git -y

echo "[5/5] Starting services..."
cd "$(dirname "$0")"
docker-compose down 2>/dev/null || true
docker-compose up -d --build

echo ""
echo "=========================================="
echo "  Deployment Complete!"
echo "=========================================="
echo ""
echo "Access your application at: http://$(curl -s ifconfig.me)"
echo ""
echo "Useful commands:"
echo "  View status: docker-compose ps"
echo "  View logs:   docker-compose logs -f"
echo "  Restart:     docker-compose restart"
echo "  Stop:        docker-compose down"
echo ""
