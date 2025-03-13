#!/bin/bash

# Script to deploy Pars.Golf to Digital Ocean

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting deployment of Pars.Golf to Digital Ocean...${NC}"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}Error: doctl is not installed. Please install Digital Ocean CLI first.${NC}"
    echo "Visit https://github.com/digitalocean/doctl#installing-doctl for installation instructions."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found. Please create it with your production configuration.${NC}"
    exit 1
fi

# Ask for confirmation
echo -e "${YELLOW}This script will deploy Pars.Golf to Digital Ocean.${NC}"
echo -e "Make sure you have:"
echo -e "  1. Created a Droplet with Docker pre-installed"
echo -e "  2. Set up DNS records for your domain"
echo -e "  3. Created a .env file with production values"
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment canceled.${NC}"
    exit 1
fi

# Ask for Droplet IP
read -p "Enter your Droplet IP address: " DROPLET_IP

# Ask for domain name
read -p "Enter your domain (e.g., pars.golf): " DOMAIN_NAME

echo -e "${GREEN}Building and pushing Docker images...${NC}"

# Build and tag Docker image
docker build -t parsgolf:latest .
docker tag parsgolf:latest parsgolf:deploy

# Generate SSH key if it doesn't exist
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}Generating SSH key...${NC}"
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

# Copy files to the server
echo -e "${GREEN}Copying files to the server...${NC}"
rsync -avz --exclude 'venv' --exclude '.git' --exclude '__pycache__' --exclude 'app/static/uploads' . root@$DROPLET_IP:/opt/parsgolf

# Connect to the server and start the app
echo -e "${GREEN}Starting the application on the server...${NC}"
ssh root@$DROPLET_IP << EOF
    cd /opt/parsgolf
    docker-compose down
    docker-compose -f docker-compose.yml up -d

    # Setup Certbot for SSL
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

    # Restart Nginx
    docker-compose restart nginx

    # Initialize the database
    docker-compose exec web python init_db.py
EOF

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "Your application is now available at: https://$DOMAIN_NAME"