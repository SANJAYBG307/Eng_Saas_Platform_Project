#!/bin/bash
# Generate self-signed SSL certificate for development
# For production, use Let's Encrypt or a valid CA certificate

CERT_DIR="./docker/nginx/ssl"
DAYS=365

echo "Generating self-signed SSL certificate for development..."

openssl req -x509 -nodes -days $DAYS -newkey rsa:2048 \
    -keyout "$CERT_DIR/key.pem" \
    -out "$CERT_DIR/cert.pem" \
    -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=localhost"

echo "SSL certificate generated successfully!"
echo "Certificate: $CERT_DIR/cert.pem"
echo "Private Key: $CERT_DIR/key.pem"
echo ""
echo "Note: This is a self-signed certificate for development only."
echo "For production, use Let's Encrypt or a certificate from a trusted CA."
