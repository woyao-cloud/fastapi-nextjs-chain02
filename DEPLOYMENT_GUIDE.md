# 部署指南

## 概述

本文档定义了用户管理系统的部署策略和流程。我们采用容器化部署，支持多环境配置，确保部署过程的可重复性、可靠性和安全性。

## 部署架构

### 1. 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        负载均衡器 (Nginx)                        │
│                    https://app.example.com                     │
└─────────────┬─────────────────────┬─────────────────────┬───────┘
              │                     │                     │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │   前端容器集群     │ │   后端容器集群     │ │    数据库集群      │
    │   Next.js App     │ │   FastAPI App     │ │   PostgreSQL      │
    │   Replica × 3     │ │   Replica × 3     │ │   Primary +       │
    │                   │ │                   │ │   Replica × 2     │
    └───────────────────┘ └───────────────────┘ └───────────────────┘
              │                     │                     │
    ┌─────────▼─────────┐ ┌─────────▼─────────┐ ┌─────────▼─────────┐
    │   对象存储         │ │   Redis缓存        │ │   监控栈          │
    │   MinIO/S3        │ │   Cluster × 3      │ │   Prometheus +    │
    │   (用户文件)       │ │   (会话/缓存)      │ │   Grafana +       │
    │                   │ │                   │ │   Loki + Tempo    │
    └───────────────────┘ └───────────────────┘ └───────────────────┘
```

### 2. 网络架构

```
公共互联网
    │
    ▼
Cloudflare/CDN (DDoS防护、SSL终止、缓存)
    │
    ▼
负载均衡器 (Nginx/HAProxy)
    │
    ├───────────────┬───────────────┐
    │               │               │
    ▼               ▼               ▼
前端服务        后端服务        管理服务
(端口3000)      (端口8000)      (端口9000)
    │               │               │
    └───────┬───────┘               │
            │                       │
            ▼                       ▼
    内部服务网络               监控/日志网络
    (10.0.1.0/24)             (10.0.2.0/24)
            │                       │
    ┌───────┴───────┐       ┌───────┴───────┐
    ▼               ▼       ▼               ▼
数据库            Redis    Prometheus      Loki
(10.0.1.10)     (10.0.1.20) (10.0.2.10)   (10.0.2.20)
```

## 环境配置

### 1. 环境定义

| 环境 | 目的 | 访问 | 数据 | 部署频率 |
|------|------|------|------|----------|
| **开发环境** | 开发者本地开发 | 本地网络 | 测试数据 | 持续部署 |
| **测试环境** | 自动化测试和QA | 内部网络 | 测试数据 | 每次PR合并 |
| **预发布环境** | 生产环境验证 | 受限访问 | 生产数据快照 | 每周或按需 |
| **生产环境** | 最终用户使用 | 公共访问 | 真实生产数据 | 稳定发布 |

### 2. 环境变量配置

**后端环境变量**:
```bash
# 通用配置
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# 服务器配置
HOST=0.0.0.0
PORT=8000
WORKERS=4
UVICORN_WORKERS=auto

# 数据库配置
DATABASE_URL=postgresql://user:password@postgres-primary:5432/user_management
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_RECYCLE=3600

# Redis配置
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=100

# JWT配置
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 安全配置
BCRYPT_ROUNDS=12
CORS_ALLOWED_ORIGINS=https://app.example.com

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
EMAILS_FROM_EMAIL=noreply@example.com

# 监控配置
PROMETHEUS_MULTIPROC_DIR=/tmp
OTEL_SERVICE_NAME=user-management-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```

**前端环境变量**:
```bash
# 通用配置
NEXT_PUBLIC_APP_NAME="用户管理系统"
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=production

# API配置
NEXT_PUBLIC_API_URL=https://api.example.com/api/v1
NEXT_PUBLIC_API_TIMEOUT=10000

# 功能开关
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_SENTRY=true
NEXT_PUBLIC_ENABLE_MAINTENANCE_MODE=false

# 第三方服务
NEXT_PUBLIC_GOOGLE_ANALYTICS_ID=UA-XXXXXX-X
NEXT_PUBLIC_SENTRY_DSN=${SENTRY_DSN}

# 性能配置
NEXT_PUBLIC_IMAGE_OPTIMIZATION=true
NEXT_PUBLIC_COMPRESSION_ENABLED=true
```

## 容器化部署

### 1. Dockerfile 配置

**后端 Dockerfile**:
```dockerfile
# 构建阶段
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml .

# 安装 Python 依赖
RUN pip install --no-cache-dir -e .

# 运行阶段
FROM python:3.11-slim

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# 复制 Python 依赖
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/tmp && \
    chown -R appuser:appgroup /app

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**前端 Dockerfile**:
```dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./
COPY yarn.lock ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 运行阶段
FROM node:18-alpine AS runner

WORKDIR /app

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 从构建阶段复制必要的文件
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切换到非 root 用户
USER nextjs

# 暴露端口
EXPOSE 3000

# 设置环境变量
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NODE_ENV=production

# 运行应用
CMD ["node", "server.js"]
```

### 2. Docker Compose 配置

**开发环境**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: user_management
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d user_management"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/user_management
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@example.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
```

**生产环境**:
```yaml
version: '3.8'

services:
  postgres-primary:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: user_management
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C"
    volumes:
      - postgres_primary_data:/var/lib/postgresql/data
      - ./postgres/conf/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./postgres/conf/pg_hba.conf:/etc/postgresql/pg_hba.conf
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
      -c hba_file=/etc/postgresql/pg_hba.conf
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d user_management"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal

  postgres-replica:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: user_management
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
      - ./postgres/conf/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./postgres/conf/pg_hba.conf:/etc/postgresql/pg_hba.conf
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
      -c hba_file=/etc/postgresql/pg_hba.conf
    depends_on:
      - postgres-primary
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d user_management"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - internal

  backend:
    image: ${BACKEND_IMAGE}:${BACKEND_TAG}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres-primary:5432/user_management
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    networks:
      - internal
      - public

  frontend:
    image: ${FRONTEND_IMAGE}:${FRONTEND_TAG}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M
    environment:
      NEXT_PUBLIC_API_URL: https://api.example.com/api/v1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
    networks:
      - public

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - public

networks:
  internal:
    internal: true
  public:

volumes:
  postgres_primary_data:
  postgres_replica_data:
  redis_data:
```

## 编排平台部署

### 1. Kubernetes 部署配置

**后端 Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: user-management
  labels:
    app: backend
    tier: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: backend
        version: v1.0.0
    spec:
      containers:
      - name: backend
        image: registry.example.com/user-management-backend:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 30
      imagePullSecrets:
      - name: registry-credentials
```

**后端 Service**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: user-management
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  type: ClusterIP
```

**后端 Ingress**:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-ingress
  namespace: user-management
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls-secret
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### 2. Helm Chart 配置

**Chart.yaml**:
```yaml
apiVersion: v2
name: user-management
description: 用户管理系统 Helm Chart
version: 1.0.0
appVersion: "1.0.0"
dependencies:
  - name: postgresql
    version: "12.1.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "17.0.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

**values.yaml**:
```yaml
# 全局配置
global:
  environment: production
  domain: example.com

# 后端配置
backend:
  replicaCount: 3
  image:
    repository: registry.example.com/user-management-backend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80
    targetMemoryUtilizationPercentage: 80
  env:
    DATABASE_URL: postgresql://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ .Release.Name }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
    REDIS_URL: redis://:{{ .Values.redis.auth.password }}@{{ .Release.Name }}-redis-master:6379/0

# 前端配置
frontend:
  replicaCount: 3
  image:
    repository: registry.example.com/user-management-frontend
    tag: v1.0.0
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      memory: 128Mi
      cpu: 100m
    limits:
      memory: 256Mi
      cpu: 200m
  env:
    NEXT_PUBLIC_API_URL: https://api.{{ .Values.global.domain }}/api/v1

# PostgreSQL 配置
postgresql:
  enabled: true
  architecture: replication
  auth:
    username: user
    password: password
    database: user_management
    replicationUsername: replicator
    replicationPassword: replicationpassword
  primary:
    persistence:
      size: 10Gi
  readReplicas:
    replicaCount: 2
    persistence:
      size: 10Gi

# Redis 配置
redis:
  enabled: true
  architecture: replication
  auth:
    password: redispassword
  master:
    persistence:
      size: 5Gi
  replica:
    replicaCount: 2
    persistence:
      size: 5Gi
```

## CI/CD 流水线

### 1. GitHub Actions 工作流

**构建和推送镜像**:
```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main, develop]
    tags: ['v*']

jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: registry.example.com/user-management-backend
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push backend image
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  build-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: registry.example.com/user-management-frontend
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push frontend image
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**部署到 Kubernetes**:
```yaml
name: Deploy to Kubernetes

on:
  workflow_run:
    workflows: ["Build and Push Docker Images"]
    types:
      - completed

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: ${{ github.event.workflow_run.conclusion == 'success' }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.26.0'

      - name: Set up Helm
        uses: azure/setup-helm@v3
        with:
          version: 'v3.11.0'

      - name: Configure kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
          chmod 600 $HOME/.kube/config

      - name: Deploy with Helm
        run: |
          helm upgrade --install user-management \
            ./charts/user-management \
            --namespace user-management \
            --create-namespace \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --atomic \
            --timeout 10m \
            --wait

      - name: Run smoke tests
        run: |
          # 运行冒烟测试验证部署
          kubectl run smoke-test --rm -i --restart=Never \
            --image=curlimages/curl \
            --command -- curl -f http://backend-service.user-management.svc.cluster.local:8000/health

      - name: Notify Slack
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: success
          text: "部署成功: ${{ github.event.workflow_run.head_commit.message }}"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. GitLab CI/CD 配置

**.gitlab-ci.yml**:
```yaml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  BACKEND_IMAGE: $CI_REGISTRY_IMAGE/backend
  FRONTEND_IMAGE: $CI_REGISTRY_IMAGE/frontend

# 测试阶段
unit-tests:
  stage: test
  image: python:3.11
  services:
    - postgres:14
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    DATABASE_URL: postgresql://test:test@postgres:5432/test_db
    REDIS_URL: redis://redis:6379/0
  script:
    - cd backend
    - pip install -e .[test]
    - pytest tests/unit/ --cov=app --cov-report=xml
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml

integration-tests:
  stage: test
  image: python:3.11
  services:
    - postgres:14
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    DATABASE_URL: postgresql://test:test@postgres:5432/test_db
    REDIS_URL: redis://redis:6379/0
  script:
    - cd backend
    - pip install -e .[test]
    - pytest tests/integration/
  dependencies:
    - unit-tests

# 构建阶段
build-backend:
  stage: build
  image: docker:20.10
  services:
    - docker:20.10-dind
  script:
    - cd backend
    - docker build -t $BACKEND_IMAGE:$CI_COMMIT_SHA .
    - docker push $BACKEND_IMAGE:$CI_COMMIT_SHA
  only:
    - main
    - develop
    - tags

build-frontend:
  stage: build
  image: docker:20.10
  services:
    - docker:20.10-dind
  script:
    - cd frontend
    - docker build -t $FRONTEND_IMAGE:$CI_COMMIT_SHA .
    - docker push $FRONTEND_IMAGE:$CI_COMMIT_SHA
  only:
    - main
    - develop
    - tags

# 部署阶段
deploy-staging:
  stage: deploy
  image: alpine/k8s:1.26
  environment:
    name: staging
    url: https://staging.example.com
  script:
    - |
      kubectl config set-cluster k8s \
        --server="$KUBE_SERVER" \
        --certificate-authority="$KUBE_CA_CERT"
      kubectl config set-credentials gitlab \
        --token="$KUBE_TOKEN"
      kubectl config set-context default \
        --cluster=k8s \
        --user=gitlab \
        --namespace=user-management-staging
      kubectl config use-context default
    - |
      helm upgrade --install user-management-staging \
        ./charts/user-management \
        --namespace user-management-staging \
        --create-namespace \
        --set backend.image.tag=$CI_COMMIT_SHA \
        --set frontend.image.tag=$CI_COMMIT_SHA \
        --set global.environment=staging \
        --atomic \
        --wait
  only:
    - develop

deploy-production:
  stage: deploy
  image: alpine/k8s:1.26
  environment:
    name: production
    url: https://app.example.com
  when: manual
  script:
    - |
      kubectl config set-cluster k8s \
        --server="$KUBE_SERVER" \
        --certificate-authority="$KUBE_CA_CERT"
      kubectl config set-credentials gitlab \
        --token="$KUBE_TOKEN"
      kubectl config set-context default \
        --cluster=k8s \
        --user=gitlab \
        --namespace=user-management
      kubectl config use-context default
    - |
      helm upgrade --install user-management \
        ./charts/user-management \
        --namespace user-management \
        --create-namespace \
        --set backend.image.tag=$CI_COMMIT_SHA \
        --set frontend.image.tag=$CI_COMMIT_SHA \
        --set global.environment=production \
        --atomic \
        --wait
  only:
    - main
    - tags
```

## 数据库部署和迁移

### 1. 数据库迁移策略

**Alembic 迁移配置**:
```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/user_management

# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.infrastructure.database.models import Base

config = context.config
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()
```

**迁移脚本示例**:
```python
# alembic/versions/20240101000000_create_users_table.py
"""create users table

Revision ID: 20240101000000
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

def downgrade():
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

### 2. 数据库备份和恢复

**备份策略**:
```bash
#!/bin/bash
# backup-database.sh

set -e

BACKUP_DIR="/backups/database"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
PGPASSWORD=$DB_PASSWORD pg_dump \
  -h $DB_HOST \
  -U $DB_USER \
  -d $DB_NAME \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  | gzip > $BACKUP_FILE

# 保留最近30天的备份
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# 上传到云存储
aws s3 cp $BACKUP_FILE s3://backup-bucket/database/
```

**恢复策略**:
```bash
#!/bin/bash
# restore-database.sh

set -e

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>"
  exit 1
fi

# 下载备份文件
aws s3 cp s3://backup-bucket/database/$BACKUP_FILE /tmp/backup.sql.gz

# 解压并恢复
gunzip -c /tmp/backup.sql.gz | \
  PGPASSWORD=$DB_PASSWORD psql \
    -h $DB_HOST \
    -U $DB_USER \
    -d $DB_NAME \
    --single-transaction

echo "Database restored successfully"
```

## 监控和告警

### 1. 监控指标

**应用指标**:
- HTTP 请求率、错误率、延迟
- 数据库连接池使用率
- Redis 缓存命中率
- JVM/Node.js 内存使用率
- 用户活跃会话数

**业务指标**:
- 用户注册率、激活率
- 登录成功/失败率
- API 使用频率
- 功能使用统计

**基础设施指标**:
- CPU、内存、磁盘使用率
- 网络带宽使用
- 容器资源使用
- 服务可用性

### 2. Prometheus 监控配置

**后端指标端点**:
```python
# app/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi.routing import APIRoute

# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP Request Latency',
    ['method', 'endpoint']
)

class PrometheusRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request):
            method = request.method
            endpoint = request.url.path

            # 记录请求开始时间
            with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
                response = await original_route_handler(request)

            # 记录请求计数
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()

            return response

        return custom_route_handler

# 添加指标端点
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**Prometheus 配置**:
```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend-service:8000']
    metrics_path: /metrics
    scrape_interval: 10s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### 3. 告警规则

**Alertmanager 配置**:
```yaml
# prometheus/alert.rules.yml
groups:
  - name: user-management
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "高错误率检测"
          description: "错误率超过5%持续2分钟"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高响应时间"
          description: "95%的请求响应时间超过2秒"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务宕机"
          description: "{{ $labels.job }} 服务不可用"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "高内存使用率"
          description: "内存使用率超过90%"
```

## 安全部署实践

### 1. 安全配置

**SSL/TLS 配置**:
```nginx
# nginx/ssl.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_timeout 1d;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;

# HSTS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

**安全头配置**:
```nginx
# nginx/security-headers.conf
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self';" always;
```

### 2. 密钥管理

**使用 Vault 管理密钥**:
```yaml
# vault-policy.hcl
path "secret/data/user-management/*" {
  capabilities = ["read"]
}

# 应用配置中使用 Vault
DATABASE_URL={{ with secret "secret/data/user-management/database" }}{{ .Data.data.url }}{{ end }}
JWT_SECRET_KEY={{ with secret "secret/data/user-management/jwt" }}{{ .Data.data.secret }}{{ end }}
```

## 灾难恢复

### 1. 备份策略

**数据备份**:
- 数据库: 每日完整备份 + 每小时增量备份
- 文件存储: 每日快照
- 配置: 版本控制 + 每日备份
- 密钥: 安全存储 + 定期轮换

**备份验证**:
- 每周恢复测试
- 备份完整性检查
- 恢复时间目标验证

### 2. 恢复流程

**灾难恢复步骤**:
1. **评估影响**: 确定影响范围和严重程度
2. **启动应急响应**: 通知相关团队
3. **数据恢复**: 从备份恢复数据
4. **服务恢复**: 启动备用环境
5. **数据同步**: 同步最新数据
6. **切换流量**: 将流量切换到恢复环境
7. **验证功能**: 运行完整性检查
8. **事后分析**: 分析原因并改进

**恢复时间目标 (RTO)**: 4小时
**恢复点目标 (RPO)**: 1小时

## 性能优化

### 1. 前端优化

**Next.js 优化**:
```javascript
// next.config.js
module.exports = {
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  images: {
    domains: ['images.example.com'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
}
```

**CDN 配置**:
- 静态资源缓存: 1年
- API 响应缓存: 根据需求配置
- 图片优化: 自动格式转换和大小调整

### 2. 后端优化

**数据库优化**:
```sql
-- 创建优化索引
CREATE INDEX CONCURRENTLY idx_users_email_active
ON users(email) WHERE is_active = true;

-- 查询优化
EXPLAIN ANALYZE SELECT * FROM users
WHERE is_active = true
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

**缓存策略**:
```python
# 使用 Redis 缓存
from redis import Redis
from functools import lru_cache

redis = Redis.from_url(REDIS_URL)

def get_user_with_cache(user_id: str):
    cache_key = f"user:{user_id}"

    # 尝试从缓存获取
    cached_data = redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # 从数据库获取
    user = user_repository.get_by_id(user_id)

    # 缓存结果 (5分钟)
    if user:
        redis.setex(cache_key, 300, json.dumps(user.to_dict()))

    return user
```

## 维护和更新

### 1. 定期维护任务

**每日任务**:
- 检查系统健康状态
- 监控警报响应
- 日志文件清理
- 备份验证

**每周任务**:
- 安全补丁更新
- 性能指标分析
- 存储空间检查
- 证书有效期检查

**每月任务**:
- 系统更新和升级
- 安全审计
- 性能调优
- 灾难恢复演练

### 2. 版本更新流程

**更新步骤**:
1. **准备阶段**: 测试环境验证，备份数据
2. **通知阶段**: 通知用户维护窗口
3. **部署阶段**: 滚动更新服务
4. **验证阶段**: 功能验证和监控
5. **回滚阶段**: 准备回滚计划（如有问题）
6. **完成阶段**: 更新文档，清理临时文件

**滚动更新策略**:
```yaml
# Kubernetes 滚动更新配置
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # 最多可以比期望Pod数多1个
    maxUnavailable: 0  # 更新时不可用Pod数为0
```

---
*本文档是部署指南的权威参考，所有部署操作必须遵循此指南。部署流程变更需要更新此文档并通知相关团队。*