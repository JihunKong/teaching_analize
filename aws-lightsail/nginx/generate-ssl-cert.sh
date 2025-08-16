#!/bin/bash

# Generate self-signed SSL certificate for development
# For production, use Let's Encrypt or AWS Certificate Manager

echo "Generating self-signed SSL certificate for development..."

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/key.pem 2048

# Generate certificate signing request
openssl req -new -key ssl/key.pem -out ssl/csr.pem \
    -subj "/C=KR/ST=Seoul/L=Seoul/O=AIBOA/OU=Development/CN=localhost"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in ssl/csr.pem -signkey ssl/key.pem -out ssl/cert.pem

# Clean up CSR file
rm ssl/csr.pem

echo "SSL certificate generated successfully!"
echo "Files created:"
echo "  - ssl/cert.pem (certificate)"
echo "  - ssl/key.pem (private key)"
echo ""
echo "Note: This is a self-signed certificate for development only."
echo "For production, use Let's Encrypt or AWS Certificate Manager."