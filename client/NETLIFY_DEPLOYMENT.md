# Netlify Deployment Instructions

This document provides instructions for deploying the frontend application to Netlify.

## Prerequisites

- A Netlify account
- Git repository connected to Netlify
- Railway backend deployed and running

## Deployment Steps

1. **Connect your repository to Netlify**:
   - Log in to Netlify
   - Click "New site from Git"
   - Select your Git provider (GitHub, GitLab, etc.)
   - Select your repository
   - Select the branch to deploy (usually `main` or `master`)

2. **Configure build settings**:
   - Build command: `npm run build`
   - Publish directory: `.next`

3. **Configure environment variables**:
   - Go to Site settings > Build & deploy > Environment
   - Add the following environment variables:
     - `NEXT_PUBLIC_API_URL`: Your Railway backend URL (e.g., `https://your-railway-app-url.railway.app/api`)

4. **Deploy the site**:
   - Click "Deploy site"
   - Wait for the build to complete
   - Your site will be available at a Netlify subdomain (e.g., `your-site-name.netlify.app`)

## Custom Domain (Optional)

To use a custom domain:

1. Go to Site settings > Domain management
2. Click "Add custom domain"
3. Follow the instructions to configure your domain

## Continuous Deployment

Netlify will automatically deploy your site when you push changes to your repository. You can configure deployment settings in the Netlify dashboard.

## Troubleshooting

If you encounter issues with the deployment:

1. Check the build logs in the Netlify dashboard
2. Ensure all environment variables are correctly set
3. Verify that the backend URL is correct and accessible
4. Check for any build errors in the Next.js application 