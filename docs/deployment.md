# Deployment Guide

## Overview

This guide covers deploying SpamGuard to production environments using Docker and Kubernetes.

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (optional, for production scaling)
- PostgreSQL database
- Redis instance
- Domain name with SSL certificate

## Local Development

### Using Docker Compose

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hamisionesmus/SpamGuard.git
   cd SpamGuard
   ```

2. **Start the services:**
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - GraphQL Playground: http://localhost:8000/graphql

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Manual Setup

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Production Deployment

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/spamguard
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://host:6379

# Security
SECRET_KEY=your-production-secret-key-change-this
DEBUG=false
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# Stripe (for payments)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Uploads
MAX_UPLOAD_SIZE=104857600  # 100MB
```

### Docker Production Build

1. **Build and push images:**
   ```bash
   # Backend
   docker build -f docker/Dockerfile.backend -t your-registry/spamguard-backend:latest .
   docker push your-registry/spamguard-backend:latest

   # Frontend
   docker build -f docker/Dockerfile.frontend -t your-registry/spamguard-frontend:latest .
   docker push your-registry/spamguard-frontend:latest
   ```

2. **Update docker-compose.yml for production:**
   ```yaml
   version: '3.8'
   services:
     backend:
       image: your-registry/spamguard-backend:latest
       environment:
         - DATABASE_URL=postgresql://user:password@prod-db:5432/spamguard
         - REDIS_URL=redis://prod-redis:6379
         - SECRET_KEY=${SECRET_KEY}
         - DEBUG=false
       restart: unless-stopped

     frontend:
       image: your-registry/spamguard-frontend:latest
       restart: unless-stopped
   ```

### Kubernetes Deployment

1. **Create namespace:**
   ```bash
   kubectl create namespace spamguard
   ```

2. **Apply Kubernetes manifests:**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Check deployment status:**
   ```bash
   kubectl get pods -n spamguard
   kubectl get services -n spamguard
   ```

### Sample Kubernetes Manifests

#### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spamguard-backend
  namespace: spamguard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: spamguard-backend
  template:
    metadata:
      labels:
        app: spamguard-backend
    spec:
      containers:
      - name: backend
        image: your-registry/spamguard-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: spamguard-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: spamguard-secrets
              key: redis-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: spamguard-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: spamguard-frontend
  namespace: spamguard
spec:
  replicas: 2
  selector:
    matchLabels:
      app: spamguard-frontend
  template:
    metadata:
      labels:
        app: spamguard-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/spamguard-frontend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

#### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: spamguard-ingress
  namespace: spamguard
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - api.yourdomain.com
    secretName: spamguard-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: spamguard-frontend
            port:
              number: 3000
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: spamguard-backend
            port:
              number: 8000
```

## Database Setup

### PostgreSQL

1. **Create database and user:**
   ```sql
   CREATE DATABASE spamguard;
   CREATE USER spamguard WITH ENCRYPTED PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE spamguard TO spamguard;
   ```

2. **Run migrations:**
   ```bash
   # Using Alembic
   cd backend
   alembic upgrade head
   ```

### Redis

1. **Basic Redis setup:**
   ```bash
   # Install Redis
   # Ubuntu/Debian
   sudo apt-get install redis-server

   # CentOS/RHEL
   sudo yum install redis

   # macOS
   brew install redis
   ```

2. **Configure Redis:**
   ```redis.conf
   # Bind to all interfaces (production)
   bind 0.0.0.0

   # Set password
   requirepass your-redis-password

   # Enable persistence
   save 900 1
   save 300 10
   save 60 10000
   ```

## Monitoring and Logging

### Prometheus Metrics

The backend exposes metrics at `/metrics` endpoint. Configure Prometheus:

```yaml
scrape_configs:
  - job_name: 'spamguard-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
```

### Grafana Dashboards

Import the provided dashboard JSON or create custom dashboards for:
- API response times
- Error rates
- User activity
- Model performance metrics

### Logging

Logs are output to stdout/stderr. In production:

1. **Centralized logging:** Use ELK stack or similar
2. **Log aggregation:** Fluentd, Filebeat, or Logstash
3. **Log storage:** Elasticsearch or cloud logging service

## Backup Strategy

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U spamguard -h localhost spamguard > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U spamguard spamguard > /backups/spamguard_$DATE.sql
find /backups -name "spamguard_*.sql" -mtime +30 -delete
```

### File Backups

```bash
# ML models backup
tar -czf /backups/models_$(date +%Y%m%d).tar.gz /app/ml/models/

# Uploaded datasets backup
tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz /app/uploads/
```

## Scaling

### Horizontal Scaling

1. **Backend:** Increase replica count in Kubernetes
2. **Frontend:** Use CDN for static assets
3. **Database:** Read replicas for read-heavy workloads

### Vertical Scaling

1. **Increase resource limits** in Kubernetes manifests
2. **Database optimization:** Indexing, query optimization
3. **Caching:** Redis for API responses and session data

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Database connections encrypted
- [ ] Environment variables for secrets
- [ ] Firewall rules configured
- [ ] Regular security updates
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Regular backup testing
- [ ] Log monitoring alerts

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check DATABASE_URL environment variable
   - Verify PostgreSQL is running and accessible
   - Check database user permissions

2. **Redis connection errors:**
   - Verify REDIS_URL configuration
   - Check Redis service status
   - Confirm password authentication

3. **Container startup failures:**
   - Check logs: `docker logs <container_id>`
   - Verify environment variables
   - Check volume mounts and permissions

4. **API timeouts:**
   - Increase timeout values in nginx config
   - Check backend performance
   - Monitor database query performance

### Health Checks

- Backend: `GET /health`
- Database: `pg_isready -U spamguard`
- Redis: `redis-cli ping`

### Performance Monitoring

- API response times
- Database query performance
- Memory and CPU usage
- Error rates and types

## Support

For deployment issues, check:
1. Application logs
2. Container logs
3. Database logs
4. Network connectivity
5. Resource utilization

Contact support@spamguard.com for assistance.