#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
npm run build

# Install Netlify CLI if not already installed
if ! command -v netlify &> /dev/null
then
    echo "Installing Netlify CLI..."
    npm install -g netlify-cli
fi

# Deploy to Netlify
echo "Deploying to Netlify..."
netlify deploy --prod

echo "Deployment complete!" 