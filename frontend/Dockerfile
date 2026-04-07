# ==========================================
# Base Image
# ==========================================
FROM node:20-alpine AS base

# ==========================================
# Dependencies Stage
# ==========================================
FROM base AS deps
# libc6-compat is required by Alpine for some native Node modules
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package managers files and install
COPY package.json package-lock.json* ./
RUN npm ci

# ==========================================
# Build Stage
# ==========================================
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Pass in the API URL as a build argument so Next.js can bake it into the static files
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ==========================================
# Runner Stage (Production)
# ==========================================
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the public folder (images, fonts, etc.) if it exists
# COPY --from=builder /app/public ./public

# Copy the standalone build output and static files
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the standalone Node.js server
CMD ["node", "server.js"]

#docker build --build-arg NEXT_PUBLIC_API_URL=http://your-backend-url:8000 -t founderai-frontend .
#docker run -p 3000:3000 founderai-frontend