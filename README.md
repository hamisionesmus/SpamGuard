# SpamGuard: Production-Ready Spam & Fraud Detection Platform

A comprehensive platform for detecting spam and fraud using supervised machine learning, featuring a modern web UI and robust APIs for third-party integrations.

## Features

- **Machine Learning Engine**: Supervised learning with TF-IDF, embeddings, and transformers
- **REST & GraphQL APIs**: Prediction, training, and health endpoints with JWT authentication
- **Web Dashboard**: Modern React/Next.js UI with real-time testing and analytics
- **User Management**: Authentication, roles, and subscription tiers
- **Admin Panel**: User and system management
- **DevOps Ready**: Docker, Kubernetes, CI/CD with monitoring

## Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (React) + TailwindCSS + ShadCN UI
- **Database**: PostgreSQL
- **ML**: scikit-learn, PyTorch, HuggingFace Transformers
- **Caching**: Redis
- **Deployment**: AWS/GCP/Azure with Docker/K8s

## Getting Started

1. Clone the repository
2. Set up environment (see docs/)
3. Run with Docker: `docker-compose up`
4. Access UI at http://localhost:3000
5. API docs at http://localhost:8000/docs

## Documentation

- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)
- [User Onboarding](./docs/onboarding.md)

## License

MIT