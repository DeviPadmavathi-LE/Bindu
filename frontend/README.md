# Bindu Chat UI

<p align="center">
  <img src="../assets\new-ui.png" alt="Bindu Agent UI" width="640" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" />
</p>

A modern, production-ready chat interface for interacting with Bindu AI agents using the A2A (Agent-to-Agent) protocol. Built on SvelteKit with extensive modifications from HuggingFace Chat UI, it provides a seamless conversational experience for testing and deploying Bindu agents locally.

## 🚀 Quickstart

Get started in minutes with a local Bindu agent:

**Step 1 – Create `.env.local`:**

```env
# Bindu Agent Configuration
BINDU_BASE_URL=http://localhost:3773
USE_AGENT_API=true

# Optional: API key for authenticated agents
BINDU_API_KEY=your_agent_api_key

# App Configuration
PUBLIC_APP_NAME="Chat with Bindu"
PUBLIC_APP_DESCRIPTION="Chat with Bindu AI agents"
```

**Step 2 – Install and launch:**

```bash
npm install
npm run dev -- --open
```

Visit `http://localhost:5173` and start chatting with your Bindu agent!

## 📋 Table of Contents

0. [Quickstart](#quickstart)
1. [Architecture Overview](#architecture-overview)
2. [Key Features](#key-features)
3. [Bindu Agent Integration](#bindu-agent-integration)
4. [Database Configuration](#database-configuration)
5. [Development Setup](#development-setup)
6. [Docker Deployment](#docker-deployment)
7. [API Reference](#api-reference)
8. [Environment Variables](#environment-variables)
9. [Component Architecture](#component-architecture)
10. [Building & Deployment](#building--deployment)

## 🏗️ Architecture Overview

### Core Framework
- **SvelteKit 5.x**: Modern full-stack framework with TypeScript and Svelte 5 syntax
- **TailwindCSS**: Utility-first styling with dark mode support and custom themes
- **MongoDB**: Persistent storage for conversations, users, and settings
- **Vite**: Fast development server with HMR and optimized builds

### Bindu-Specific Architecture

#### A2A Protocol Integration
- **JSON-RPC 2.0**: Full protocol compliance for agent communication
- **Task State Machine**: Complete state handling (submitted → working → input-required → completed/failed)
- **Context Management**: Persistent conversation contexts with task continuity
- **Real-time Polling**: Background task status monitoring with exponential backoff

#### Key Components
```
src/
├── lib/
│   ├── services/
│   │   └── agent-api.ts          # JSON-RPC client for Bindu communication
│   ├── server/
│   │   ├── endpoints/
│   │   │   └── bindu/            # A2A protocol adapter
│   │   ├── models.ts             # Agent discovery and configuration
│   │   └── config.ts             # Environment configuration manager
│   ├── stores/
│   │   └── chat.ts               # State management for conversations
│   ├── components/
│   │   ├── AgentStatePanel.svelte # Real-time agent status display
│   │   └── chat/                 # Chat interface components
│   └── types/
│       └── agent.ts              # A2A protocol type definitions
├── routes/
│   ├── api/
│   │   ├── agent-card/           # Agent discovery endpoint
│   │   ├── agent-health/         # Health check endpoint
│   │   ├── agent-skills/         # Skills listing
│   │   └── did-resolve/          # DID resolution
│   └── +page.svelte             # Main chat interface
```

## ✨ Key Features

### 🤖 Agent Discovery & Management
- **Automatic Agent Discovery**: Fetch agent cards from `.well-known/agent.json`
- **Dynamic Configuration**: Real-time agent capability detection
- **Skills Browser**: Interactive exploration of agent skills with detailed modal views
- **DID Integration**: Decentralized identity support for agent authentication

### 🔐 Authentication & Security
- **Multiple Auth Methods**: API key, JWT/OAuth, and DID-based authentication
- **Payment Protocol**: x402 payment flow integration for paid agents
- **Token Management**: Secure storage and automatic token refresh
- **OAuth Flow**: Complete OpenID Connect implementation with CIMD support

### 💬 Advanced Chat Features
- **Real-time Messaging**: Live chat with typing indicators and status updates
- **Task Polling**: Background status updates with proper cleanup and error handling
- **Context Switching**: Multiple conversation management with persistent contexts
- **File Support**: File uploads and multimedia handling with base64 encoding
- **Markdown Rendering**: Rich text formatting with syntax highlighting

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first approach with proper breakpoints
- **Dark/Light Themes**: Built-in theme switching with system preference detection
- **Micro-interactions**: Smooth transitions and hover states
- **Accessibility**: WCAG compliance with keyboard navigation
- **Loading States**: Skeleton screens and progress indicators

## 🔗 Bindu Agent Integration

### Agent Discovery Protocol

The UI automatically discovers and configures Bindu agents:

```typescript
// Automatic agent card fetching
GET {BINDU_BASE_URL}/.well-known/agent.json

// Response structure
{
  "name": "Agent Name",
  "description": "Agent description",
  "capabilities": {
    "taskManagement": true,
    "streaming": true
  },
  "endpoints": {
    "jsonrpc": "https://agent.example.com"
  },
  "skills": [...]
}
```

### Task State Management

Complete A2A task lifecycle implementation:

```typescript
type TaskState = 
  | 'submitted'    // Task received by agent
  | 'working'      // Agent is processing
  | 'input-required' // Needs user input
  | 'auth-required'  // Needs authentication
  | 'completed'    // Task finished
  | 'failed'       // Task failed
  | 'canceled'     // Task was canceled
  | 'rejected';    // Task was rejected
```

### Context Continuity

- **Context IDs**: Map MongoDB conversation IDs to A2A context IDs
- **Task References**: Maintain conversation flow across messages
- **State Persistence**: Context survives page refreshes and reconnections
- **Non-terminal States**: Reuse same task ID for continued interactions

## 🗄️ Database Configuration

### MongoDB Setup

#### Option 1: MongoDB Atlas (Recommended for Production)
```bash
# 1. Create free cluster at mongodb.com
# 2. Add IP to network access list
# 3. Create database user
# 4. Set connection string in .env.local
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/chat-ui
MONGODB_DB_NAME=bindu-chat
```

#### Option 2: Local MongoDB
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongo-bindui mongo:8

# Set in .env.local
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=bindu-chat
```

#### Option 3: Embedded MongoDB (Development Only)
```bash
# No configuration needed - falls back to embedded DB
# Data persists to ./db directory
```

### Database Schema

- **Conversations**: Chat history with metadata and task associations
- **Messages**: Individual messages with task IDs and context references
- **Users**: Authentication data and user preferences
- **Settings**: Configuration and feature flags
- **Files**: Uploaded file metadata and base64 content

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ 
- npm 9+
- MongoDB (optional for development)

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env .env.local
# Edit .env.local with your configuration

# Start development server
npm run dev
```

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run test         # Run tests
npm run lint         # Run linting
npm run format       # Format code
npm run check        # Type checking
```

### Testing

The project includes comprehensive test suites:

```bash
# Client-side tests (Svelte components)
npm run test -- client

# Server-side tests (Node.js utilities)
npm run test -- server

# SSR tests (Server-side rendering)
npm run test -- ssr

# All tests
npm run test
```

## 🐳 Docker Deployment

### Production Dockerfile

Multi-stage build with security optimizations:

```dockerfile
# Build stage
FROM node:24 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runtime stage
FROM node:24-slim AS runtime
WORKDIR /app
COPY --from=builder /app/build ./build
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "build/index.js"]
```

### Deployment Options

#### Option 1: External MongoDB
```bash
docker run \
  -p 5173:3000 \
  -e BINDU_BASE_URL=http://localhost:3773 \
  -e USE_AGENT_API=true \
  -e MONGODB_URL=mongodb://your-mongo:27017 \
  -e PUBLIC_APP_NAME="Chat with Bindu" \
  bindu-chat-ui:latest
```

#### Option 2: Embedded MongoDB
```bash
docker run \
  -p 5173:3000 \
  -e INCLUDE_DB=true \
  -e BINDU_BASE_URL=http://localhost:3773 \
  -e USE_AGENT_API=true \
  bindu-chat-ui-db:latest
```

#### Option 3: Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5173:3000"
    environment:
      - BINDU_BASE_URL=http://localhost:3773
      - USE_AGENT_API=true
      - MONGODB_URL=mongodb://mongo:27017
    depends_on:
      - mongo
  
  mongo:
    image: mongo:8
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

## 📡 API Reference

### Agent Information Endpoints

#### `GET /api/agent-card`
Fetch agent card from `.well-known/agent.json`

```bash
curl http://localhost:5173/api/agent-card
```

**Response:**
```json
{
  "name": "Bindu Agent",
  "description": "AI agent for task automation",
  "capabilities": {
    "taskManagement": true,
    "streaming": true
  },
  "skills": [...],
  "endpoints": {
    "jsonrpc": "http://localhost:3773"
  }
}
```

#### `GET /api/agent-health`
Check agent health status

```bash
curl http://localhost:5173/api/agent-health
```

#### `GET /api/agent-skills`
List available agent skills

```bash
curl http://localhost:5173/api/agent-skills
```

#### `GET /api/agent-skills/[skillId]`
Get specific skill details

```bash
curl http://localhost:5173/api/agent-skills/skill-id
```

### Authentication & Payment

#### `POST /api/did-resolve`
Resolve DID documents for agent authentication

```bash
curl -X POST http://localhost:5173/api/did-resolve \
  -H "Content-Type: application/json" \
  -d '{"did": "did:method:identifier"}'
```

#### `POST /api/agent-negotiation`
Handle agent negotiation for payment and terms

```bash
curl -X POST http://localhost:5173/api/agent-negotiation \
  -H "Content-Type: application/json" \
  -d '{"terms": {...}}'
```

### Models Endpoints

#### `GET /api/models`
List available models (Bindu agents)

```bash
curl http://localhost:5173/api/models
```

#### `GET /api/v2/models`
Enhanced models endpoint with full metadata

```bash
curl http://localhost:5173/api/v2/models
```

### Conversation Management

#### `GET /api/conversations`
List all conversations

#### `POST /api/conversations`
Create new conversation

#### `GET /api/conversations/[id]`
Get conversation details

#### `POST /api/conversations/[id]/message`
Send message to conversation

## ⚙️ Environment Variables

### Required Variables

```env
# Bindu Agent Configuration
BINDU_BASE_URL=http://localhost:3773          # Base URL of your Bindu agent
USE_AGENT_API=true                            # Enable Bindu agent API mode
```

### Optional Variables

#### Agent Configuration
```env
BINDU_API_KEY=your_api_key                   # API key for authenticated agents
BINDU_AGENT_NAME=Custom Agent Name            # Override agent display name
BINDU_ONLY_MODE=false                         # Use Bindu as the only model
BINDU_TIMEOUT_MS=10000                       # Agent request timeout (ms)
```

#### Application Configuration
```env
PUBLIC_APP_NAME="Chat with Bindu"             # App title
PUBLIC_APP_DESCRIPTION="Chat with Bindu AI agents"  # App description
PUBLIC_APP_ASSETS=chatui                      # Asset folder name
PUBLIC_ORIGIN=https://your-domain.com         # Public origin URL
PUBLIC_SHARE_PREFIX=/share                    # URL prefix for shared conversations
```

#### Database Configuration
```env
MONGODB_URL=mongodb://localhost:27017         # MongoDB connection string
MONGODB_DB_NAME=chat-ui                       # Database name
```

#### Features & Behavior
```env
PUBLIC_SMOOTH_UPDATES=false                   # Enable message smoothing
AUTOMATIC_LOGIN=false                         # Require auth on all routes
USE_USER_TOKEN=false                          # Use user tokens for inference
ALLOW_IFRAME=true                             # Allow iframe embedding
```

#### OAuth/OpenID Configuration
```env
OPENID_CLIENT_ID=""                           # OAuth client ID
OPENID_CLIENT_SECRET=""                       # OAuth client secret
OPENID_SCOPES="openid profile inference-api read-mcp read-billing"
```

#### Legacy OpenAI Compatibility
```env
OPENAI_BASE_URL=https://router.huggingface.co/v1  # OpenAI-compatible endpoint
OPENAI_API_KEY=hf_************************         # OpenAI API key
```

> **Note**: When `USE_AGENT_API=true`, the UI prioritizes Bindu agent communication over OpenAI compatibility mode.

## 🧩 Component Architecture

### Core Components

#### `AgentStatePanel.svelte`
Real-time agent status display with:
- Context information display
- Task counters and statistics
- Clear context/tasks actions
- Authentication status indicators

#### `ChatWindow.svelte`
Main chat interface featuring:
- Message history display with task metadata
- Real-time message updates
- File upload support with drag-and-drop
- Task status indicators and state management

#### `ChatInput.svelte`
Message input component with:
- Multiline text input with auto-resize
- File attachment support
- Voice recording (if transcription enabled)
- Submit button with loading states

### Store Architecture

#### `chat.ts` - Conversation State
```typescript
export const currentTaskId = writable<string | null>(null);
export const currentTaskState = writable<TaskState | null>(null);
export const contextId = writable<string | null>(null);
export const messages = writable<DisplayMessage[]>([]);
export const authToken = writable<string | null>(null);
```

#### `settings.ts` - User Preferences
```typescript
export const theme = writable<'light' | 'dark' | 'system'>('system');
export const model = writable<string>('bindu');
export const customPrompts = writable<CustomPrompt[]>([]);
```

### API Client Architecture

#### `agent-api.ts` - Bindu Communication
```typescript
export class AgentAPI {
  async sendMessage(params: SendMessageParams): Promise<Task>
  async getTask(taskId: string): Promise<Task>
  async listContexts(): Promise<ContextListResult>
  async clearContext(contextId: string): Promise<void>
  async submitFeedback(taskId: string, rating: number): Promise<void>
}
```

## 🚀 Building & Deployment

### Production Build

```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview

# Build with specific adapter
npm run build
# Uses @sveltejs/adapter-node by default
```

### Deployment Targets

#### Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Self-Hosted
```bash
# Build and run with PM2
npm run build
pm2 start build/index.js --name bindu-chat-ui
```

### Performance Optimization

#### Build Optimizations
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Dead code elimination
- **Asset Optimization**: Image compression and lazy loading
- **Bundle Analysis**: Built-in bundle analyzer

#### Runtime Optimizations
- **Service Worker**: Offline support and caching
- **CDN Integration**: Static asset delivery
- **Database Indexing**: Optimized MongoDB queries
- **Connection Pooling**: Efficient database connections

## 🔧 Troubleshooting

### Common Issues

#### Agent Not Connecting
```bash
# Check agent URL
curl http://localhost:3773/.well-known/agent.json

# Verify environment variables
echo $BINDU_BASE_URL
echo $USE_AGENT_API
```

#### Authentication Issues
```bash
# Check token storage
localStorage.getItem('bindu_oauth_token')

# Verify API key
curl -H "Authorization: Bearer $BINDU_API_KEY" \
  http://localhost:3773/.well-known/agent.json
```

#### Database Connection
```bash
# Test MongoDB connection
mongosh $MONGODB_URL

# Check database logs
docker logs mongo-bindui
```

### Debug Mode

Enable debug logging:
```env
DEBUG=bindu:*
LOG_LEVEL=debug
```

### Health Checks

```bash
# Application health
curl http://localhost:5173/healthcheck

# Agent health
curl http://localhost:5173/api/agent-health

# Database health
curl http://localhost:5173/api/v2/debug/config
```

## 📚 Additional Resources

- [Bindu A2A Protocol Specification](https://docs.bindu.ai/a2a-protocol)
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [MongoDB Node.js Driver](https://mongodb.github.io/node-mongodb-native/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the Bindu Agent Ecosystem**
