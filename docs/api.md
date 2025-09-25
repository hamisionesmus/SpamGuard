# API Documentation

## Overview

SpamGuard provides both REST and GraphQL APIs for spam and fraud detection. All endpoints require authentication except for health checks.

## Authentication

All API requests require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and receive access/refresh tokens.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAi..."
}
```

## Prediction API

### POST /api/v1/predict
Make a spam/fraud prediction on input text.

**Request Body:**
```json
{
  "text": "This is a sample message to analyze for spam",
  "model_version": "latest"
}
```

**Response:**
```json
{
  "prediction": "spam",
  "confidence": 0.89,
  "explanation": {
    "keywords_found": ["buy", "urgent"],
    "reason": "Detected 2 relevant keywords"
  },
  "model_version": "v1.2.0"
}
```

### GET /api/v1/predict/history
Get user's prediction history.

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "history": [
    {
      "id": "uuid",
      "prediction": "spam",
      "confidence": 0.85,
      "input_text": "Sample text...",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

### GET /api/v1/predict/models
List available ML models.

**Response:**
```json
{
  "models": [
    {
      "name": "spam_classifier_v1",
      "version": "1.0",
      "algorithm": "LogisticRegression",
      "metrics": {
        "accuracy": 0.92,
        "precision": 0.89,
        "recall": 0.88,
        "f1": 0.885
      },
      "training_samples": 10000,
      "created": 1704067200.0
    }
  ]
}
```

## GraphQL API

### Endpoint
```
POST /graphql
```

### Schema

```graphql
type Query {
  predict(input: PredictionInput!): PredictionResult!
  models: [ModelInfo!]!
  me: UserInfo!
}

type Mutation {
  predict(input: PredictionInput!): PredictionResult!
}

type PredictionResult {
  prediction: String!
  confidence: Float!
  explanation: JSON
  modelVersion: String!
}

type ModelInfo {
  name: String!
  version: String!
  algorithm: String!
  metrics: JSON
  trainingSamples: Int!
  created: Float!
}

type UserInfo {
  id: String!
  email: String!
  fullName: String!
  isActive: Boolean!
}

input PredictionInput {
  text: String!
  modelVersion: String
}
```

### Example Query

```graphql
query GetPrediction($text: String!) {
  predict(input: { text: $text }) {
    prediction
    confidence
    explanation
    modelVersion
  }
}
```

## Admin API

Admin endpoints require admin role authentication.

### GET /api/v1/admin/users
List all users (admin only).

**Query Parameters:**
- `limit` (optional): Number of records to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

### GET /api/v1/admin/stats
Get system statistics.

**Response:**
```json
{
  "total_users": 1250,
  "total_predictions": 45670,
  "total_datasets": 15,
  "total_models": 3,
  "recent_predictions_24h": 1250,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### POST /api/v1/admin/models/retrain
Trigger model retraining (admin only).

**Request Body:**
```json
{
  "model_version": "latest"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "started"
}
```

### GET /api/v1/admin/jobs/{job_id}
Get background job status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "message": "Model retraining completed successfully"
}
```

## Rate Limiting

API calls are rate limited based on subscription tier:

- **Free**: 100 requests/hour
- **Business**: 1000 requests/hour
- **Enterprise**: 10000 requests/hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Responses

All APIs return standardized error responses:

```json
{
  "detail": "Error message",
  "type": "error_type",
  "code": 400
}
```

### Common Error Codes

- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests (Rate Limited)
- `500`: Internal Server Error

## Webhooks

Configure webhooks to receive real-time notifications of predictions.

### Webhook Payload

```json
{
  "event": "prediction.created",
  "data": {
    "id": "uuid",
    "prediction": "spam",
    "confidence": 0.89,
    "input_text": "Sample text...",
    "user_id": "uuid",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## SDKs and Libraries

### Python Client

```python
from spamguard import SpamGuard

client = SpamGuard(api_key="your-api-key")
result = client.predict("Sample text to analyze")
print(f"Prediction: {result.prediction}, Confidence: {result.confidence}")
```

### JavaScript Client

```javascript
import { SpamGuard } from 'spamguard-js';

const client = new SpamGuard({ apiKey: 'your-api-key' });
const result = await client.predict('Sample text to analyze');
console.log(`Prediction: ${result.prediction}, Confidence: ${result.confidence}`);
```

## Support

For API support, contact support@spamguard.com or visit our [developer portal](https://developers.spamguard.com).