# Implementation Plan

- [x] 1. Setup development environment and branch management

  - Create new branch `vercel-supabase-migration` based on `multi-tenancy` branch
  - Configure MCP servers for Vercel and Supabase development
  - Set up local development environment with new dependencies
  - _Requirements: 2.1, 2.2_

- [ ] 2. Configure external services and environment

  - [x] 2.1 Create and configure Supabase project

    - Create new Supabase project
    - Configure database settings and connection pooling
    - Generate and secure API keys (anon key, service role key)
    - _Requirements: 1.1, 4.1, 4.2_

  - [x] 2.2 Setup Upstash Redis database

    - Create Upstash Redis database instance
    - Configure REST API access
    - Generate connection URL and token
    - _Requirements: 1.1, 4.1, 4.2_

  - [x] 2.3 Configure Vercel environment variables
    - Set up all required environment variables in Vercel dashboard
    - Configure Supabase, Upstash, and Evolution API credentials
    - Test environment variable access in serverless functions
    - _Requirements: 4.1, 4.2, 4.3_

- [ ] 3. Migrate database schema to Supabase

  - [x] 3.1 Export current PostgreSQL schema

    - Extract current database schema from existing setup
    - Document all tables, indexes, and relationships
    - Create migration scripts for schema recreation
    - _Requirements: 1.2, 3.1_

  - [x] 3.2 Create Supabase database schema

    - Execute schema creation scripts in Supabase
    - Create all tables (users, clients, messages, playbooks, agent_configs)
    - Set up proper indexes for performance optimization
    - _Requirements: 1.2, 3.1_

  - [x] 3.3 Configure Row Level Security (RLS) policies
    - Enable RLS on all tables
    - Create policies for multi-tenant data isolation
    - Test RLS policies with sample data
    - _Requirements: 1.2, 3.1_

- [ ] 4. Refactor backend for serverless architecture

  - [x] 4.1 Create Supabase database connection module

    - Implement `src/core/supabase_db.py` with connection management
    - Create database client initialization and connection pooling
    - Add error handling for connection failures
    - _Requirements: 1.1, 1.2, 3.1_

  - [x] 4.2 Implement Upstash Redis session management

    - Create `src/core/upstash_redis.py` for Redis operations
    - Refactor session management to use Upstash Redis
    - Implement session storage, retrieval, and cleanup functions
    - _Requirements: 1.1, 3.2_

  - [x] 4.3 Update Evolution API integration for external service

    - Refactor `src/core/evolution_integration.py` for external API
    - Update API calls to use centralsupernova.com.br endpoint
    - Implement proper authentication with provided API key
    - _Requirements: 1.1, 3.3_

  - [x] 4.4 Convert main application to serverless functions
    - Restructure FastAPI app for Vercel serverless deployment
    - Create individual API route files in `/api` directory
    - Update import paths and dependency injection for serverless
    - _Requirements: 1.1, 1.3_

- [ ] 5. Update API endpoints for serverless deployment

  - [x] 5.1 Create authentication API functions

    - Convert auth routes to `/api/auth/login.py` and `/api/auth/register.py`
    - Update JWT handling for serverless environment
    - Test authentication flow with Supabase backend
    - _Requirements: 1.1, 3.1_

  - [x] 5.2 Create client management API functions

    - Convert client routes to `/api/clients/index.py` and `/api/clients/[id].py`
    - Update database queries to use Supabase client
    - Implement proper error handling and validation
    - _Requirements: 1.1, 3.2_

  - [x] 5.3 Create message handling API functions

    - Convert message routes to `/api/messages/index.py` and `/api/messages/[id].py`
    - Update message processing with new Redis session management
    - Test message flow with Evolution API integration
    - _Requirements: 1.1, 3.3_

  - [x] 5.4 Create webhook API function
    - Convert webhook handler to `/api/webhook/whatsapp.py`
    - Update webhook processing for serverless environment
    - Implement proper request validation and error handling
    - _Requirements: 1.1, 3.3_

- [ ] 6. Resolve CORS issues and configure Vercel

  - [x] 6.1 Update Vercel configuration for CORS

    - Modify `vercel.json` with proper CORS headers
    - Configure specific origins instead of wildcards
    - Set up proper routing for API functions
    - _Requirements: 1.1, 1.3_

  - [x] 6.2 Update frontend API client configuration

    - Modify `frontend/src/lib/api.ts` for new API endpoints
    - Update base URLs for production and development
    - Implement proper error handling for API calls
    - _Requirements: 1.3, 3.4_

  - [x] 6.3 Test CORS resolution
    - Deploy to Vercel staging environment
    - Test all API endpoints from frontend
    - Verify no CORS errors in browser console
    - _Requirements: 1.1, 1.3_

- [ ] 7. Data migration and testing

  - [ ] 7.1 Migrate existing data to Supabase

    - Export data from current PostgreSQL database
    - Transform data format if needed for Supabase
    - Import data into Supabase with proper client isolation
    - _Requirements: 1.2, 3.1_

  - [ ] 7.2 Test multi-tenant functionality

    - Verify client data isolation works correctly
    - Test user authentication and authorization
    - Confirm RLS policies prevent cross-client data access
    - _Requirements: 3.1, 3.2_

  - [ ] 7.3 Test WhatsApp integration end-to-end
    - Test webhook reception from Evolution API
    - Verify message processing and AI responses
    - Test message sending through Evolution API
    - _Requirements: 3.3, 1.5_

- [ ] 8. Performance optimization and monitoring

  - [ ] 8.1 Optimize serverless function performance

    - Implement connection pooling and caching strategies
    - Optimize cold start times for API functions
    - Add performance monitoring and logging
    - _Requirements: 1.1, 1.4_

  - [ ] 8.2 Test application under load
    - Perform load testing on Vercel deployment
    - Monitor database performance with Supabase
    - Test Redis performance with Upstash
    - _Requirements: 1.4, 3.4_

- [ ] 9. Documentation and deployment

  - [x] 9.1 Create migration documentation

    - Document all configuration changes and new environment variables
    - Create deployment guide for Vercel + Supabase setup
    - Document troubleshooting steps for common issues
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 9.2 Deploy to production

    - Deploy final version to Vercel production environment
    - Configure production environment variables
    - Test all functionality in production environment
    - _Requirements: 1.1, 1.3, 1.4_

  - [ ] 9.3 Create rollback plan
    - Document steps to rollback to previous architecture if needed
    - Create backup of current production data
    - Test rollback procedure in staging environment
    - _Requirements: 5.4_
