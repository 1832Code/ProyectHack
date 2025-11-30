# Fashion app screen

*Automatically synced with your [v0.app](https://v0.app) deployments*

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/maxr-evenbizs-projects/v0-fashion-app-screen)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.app-black?style=for-the-badge)](https://v0.app/chat/q5banjBDrNB)

## Overview

This repository will stay in sync with your deployed chats on [v0.app](https://v0.app).
Any changes you make to your deployed app will be automatically pushed to this repository from [v0.app](https://v0.app).

## Deployment

Your project is live at:

**[https://vercel.com/maxr-evenbizs-projects/v0-fashion-app-screen](https://vercel.com/maxr-evenbizs-projects/v0-fashion-app-screen)**

## Build your app

Continue building your app on:

**[https://v0.app/chat/q5banjBDrNB](https://v0.app/chat/q5banjBDrNB)**

## How It Works

1. Create and modify your project using [v0.app](https://v0.app)
2. Deploy your chats from the v0 interface
3. Changes are automatically pushed to this repository
4. Vercel deploys the latest version from this repository

## Authentication (Google Sign-in)

This project now includes a real Google sign-in flow powered by NextAuth.

To enable it locally, do the following:

1. Install the dependency inside the `frontend` folder:

```bash
cd frontend
pnpm add next-auth    # or `npm i next-auth` / `yarn add next-auth`
```

2. Create a `.env.local` in `frontend/` (you can copy `.env.local.example`) and set:

```
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=replace-with-a-secure-random-string
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

3. In Google Cloud Console create OAuth 2.0 credentials and set the redirect URI to:
	- `http://localhost:3000/api/auth/callback/google`

4. Restart the dev server and click "Comenzar Análisis" → you'll be sent to the real Google sign-in flow.

If you want, I can also integrate a persistent database adapter (e.g. Prisma) so sessions and users are stored server-side.