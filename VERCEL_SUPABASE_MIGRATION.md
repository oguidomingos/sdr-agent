# SDR Agent - Vercel + Supabase Migration Guide

## Overview

This document describes the complete migration of the SDR Agent Multi-Client SaaS from a traditional architecture to a cloud-native serverless architecture using Vercel and Supabase.

## Architecture Changes

### Before (Traditional)
- **Backend**: FastAPI with PostgreSQL (Neon)
- **Frontend**: React/Vite with TypeScript
- **Database**: PostgreSQL via Neon
- **Cache**: Redis
- **Deployment**: Traditional server deployment

### After (Cloud-Native)
- **Backend**: FastAPI serverless functions on Vercel
- **Frontend**: React/Vite static deployment on Vercel
- **Database**: Supabase PostgreSQL with RLS
- **Cache**: Upstash Redis (serverless)
- **WhatsApp**: Evolution API external service
- **Authentication**: JWT with Supabase backend

## Environment Variables

### Required Environment Variables for Vercel

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Upstash Redis Configuration
UPSTASH_REDIS_REST_URL=https://your-redis-id.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-token

# Evolution API Configuration (External)
EVOLUTION_API_URL=https://evolutionapi.centralsupernova.com.br
EVOLUTION_API_KEY=509dbd54-c20c-4a5b-b889-a0494a861f5a

# Security
SECRET_KEY=your-secret-key-here
WEBHOOK_SECRET=your-webhook-secret-here
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRATION_HOURS=24

# Application Settings
ENVIRONMENT=production
DEBUG=false

# CORS Settings
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000

# AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-2.0-flash
```

### Frontend Environment Variables

```bash
# API Configuration
VITE_API_URL=https://your-app.vercel.app/api

# Application Configuration
VITE_APP_NAME=SDR Agent Multi-Client SaaS
VITE_APP_VERSION=2.0.0
```

## Deployment Steps

### 1. Setup External Services

#### Supabase Setup
1. Create a new Supabase project at https://supabase.com
2. Get your project URL and API keys
3. Run the schema migration:
   ```bash
   python scripts/apply_supabase_schema.py
   ```
4. Test the RLS policies:
   ```bash
   python scripts/test_rls_policies.py
   ```

#### Upstash Redis Setup
1. Create a new Redis database at https://upstash.com
2. Get the REST URL and token
3. Test the connection with the session manager

### 2. Configure Vercel Project

1. Connect your GitHub repository to Vercel
2. Set the build configuration:
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

3. Add all environment variables in Vercel dashboard

### 3. Deploy to Vercel

1. Push your code to the `vercel-supabase-migration` branch
2. Vercel will automatically deploy
3. Test all endpoints using the CORS test script:
   ```bash
   python scripts/test_cors.py
   ```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user

### Clients Management
- `GET /api/clients/` - List clients
- `POST /api/clients/` - Create client
- `GET /api/clients/[id]` - Get client by ID
- `PUT /api/clients/[id]` - Update client
- `DELETE /api/clients/[id]` - Delete client

### Messages
- `GET /api/messages/` - List messages with filters
- `GET /api/messages/stats` - Get message statistics

### Webhook
- `POST /api/webhook/whatsapp` - WhatsApp webhook handler

## Database Schema

The database schema includes the following tables with Row Level Security (RLS):

- **users** - User accounts with authentication
- **clients** - Multi-tenant client configurations
- **messages** - WhatsApp messages with conversation history
- **playbooks** - SPIN selling conversation flows
- **agent_configs** - AI agent configurations

All tables have RLS policies to ensure proper multi-tenant isolation.

## Session Management

Sessions are managed using Upstash Redis with the following structure:

```
session:{client_id}:{user_id} -> {
  user_id: string,
  messages: Message[],
  last_interaction: timestamp,
  metadata: object
}
```

## WhatsApp Integration

The system integrates with Evolution API external service:

- **Base URL**: https://evolutionapi.centralsupernova.com.br
- **API Key**: 509dbd54-c20c-4a5b-b889-a0494a861f5a
- **Instance Management**: Automatic instance creation per client
- **Webhook Processing**: Real-time message processing

## CORS Configuration

CORS is configured to allow requests from:
- Production frontend: `https://sdr-agent-frontend.vercel.app`
- Development: `http://localhost:3000`, `http://localhost:5173`

Headers allowed:
- `Authorization`
- `Content-Type`
- `X-Signature`
- `X-Hub-Signature-256`

## Testing

### Local Development
1. Set up environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python -m uvicorn api.index:app --reload --port 3000`

### Production Testing
1. Deploy to Vercel
2. Run CORS tests: `python scripts/test_cors.py`
3. Test webhook functionality
4. Verify database operations

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check that frontend domain is in CORS_ORIGINS
   - Verify Vercel headers configuration
   - Test with CORS test script

2. **Database Connection Issues**
   - Verify Supabase credentials
   - Check RLS policies
   - Test with health endpoint

3. **Redis Session Issues**
   - Verify Upstash credentials
   - Check session timeout settings
   - Test session storage/retrieval

4. **Webhook Issues**
   - Verify Evolution API credentials
   - Check webhook signature validation
   - Test with webhook test endpoint

### Logs and Monitoring

- **Vercel Functions**: Check function logs in Vercel dashboard
- **Supabase**: Monitor database performance in Supabase dashboard
- **Upstash**: Check Redis metrics in Upstash dashboard

## Migration Checklist

- [ ] Supabase project created and configured
- [ ] Upstash Redis database created
- [ ] Environment variables set in Vercel
- [ ] Database schema migrated
- [ ] RLS policies tested
- [ ] CORS configuration verified
- [ ] All API endpoints tested
- [ ] Webhook functionality verified
- [ ] Frontend updated and deployed
- [ ] End-to-end testing completed

## Rollback Plan

If issues occur, rollback steps:

1. Switch DNS/routing back to old infrastructure
2. Restore database from backup if needed
3. Update frontend to use old API endpoints
4. Monitor for any data inconsistencies

## Performance Considerations

- **Cold Starts**: Serverless functions may have cold start delays
- **Database Connections**: Supabase handles connection pooling
- **Redis Performance**: Upstash provides low-latency access
- **File Uploads**: Consider using Supabase Storage for media files

## Security Notes

- All API endpoints require authentication except webhook
- RLS policies ensure multi-tenant data isolation
- Webhook signatures are verified for security
- JWT tokens have configurable expiration
- Environment variables contain sensitive data - keep secure

## Support and Maintenance

- Monitor Vercel function performance and errors
- Keep Supabase and Upstash within usage limits
- Regular security updates for dependencies
- Monitor Evolution API service availability
- Backup database regularly through Supabase