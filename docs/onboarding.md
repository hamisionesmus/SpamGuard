# User Onboarding Guide

## Welcome to SpamGuard

Congratulations on choosing SpamGuard for your spam and fraud detection needs! This guide will help you get started with our platform.

## Quick Start

### 1. Account Setup

1. **Visit the SpamGuard website** at [https://spamguard.com](https://spamguard.com)
2. **Click "Get Started"** and create your account
3. **Verify your email** using the link sent to your inbox
4. **Complete your profile** with company information

### 2. Choose Your Plan

Select from our three subscription tiers:

| Feature | Free | Business | Enterprise |
|---------|------|----------|------------|
| Monthly API Calls | 1,000 | 10,000 | 100,000 |
| Models Access | Basic | Advanced | Custom |
| Support | Community | Email | Phone + Email |
| SLA | - | 99.5% | 99.9% |
| Price | $0 | $49/month | $199/month |

### 3. Get Your API Key

1. Go to your **Dashboard > API Keys**
2. Click **"Generate New Key"**
3. Copy your API key (keep it secure!)

## Making Your First API Call

### Using cURL

```bash
# Get authentication token
curl -X POST "https://api.spamguard.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your-email@example.com",
    "password": "your-password"
  }'

# Make a prediction
curl -X POST "https://api.spamguard.com/api/v1/predict" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Congratulations! You have won a free iPhone. Click here to claim your prize!",
    "model_version": "latest"
  }'
```

### Using Python

```python
import requests

# Authentication
auth_response = requests.post('https://api.spamguard.com/api/v1/auth/login', json={
    'username': 'your-email@example.com',
    'password': 'your-password'
})
token = auth_response.json()['access_token']

# Headers for authenticated requests
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Make prediction
response = requests.post('https://api.spamguard.com/api/v1/predict',
    headers=headers,
    json={
        'text': 'Buy cheap viagra now!!! Limited time offer.',
        'model_version': 'latest'
    }
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}")
```

### Using JavaScript

```javascript
// Authentication
const authResponse = await fetch('https://api.spamguard.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'your-email@example.com',
    password: 'your-password'
  })
});
const { access_token } = await authResponse.json();

// Make prediction
const predictionResponse = await fetch('https://api.spamguard.com/api/v1/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'URGENT: Your account will be suspended unless you update your payment information.',
    model_version: 'latest'
  })
});

const result = await predictionResponse.json();
console.log(`Prediction: ${result.prediction}, Confidence: ${result.confidence}`);
```

## Understanding Predictions

### Response Format

```json
{
  "prediction": "spam",
  "confidence": 0.89,
  "explanation": {
    "keywords_found": ["URGENT", "account", "suspended"],
    "reason": "Detected 3 relevant keywords"
  },
  "model_version": "v2.1.0"
}
```

### Prediction Types

- **spam**: Content identified as spam
- **ham/legitimate**: Normal, non-spam content
- **fraud**: Content indicating fraudulent activity

### Confidence Scores

- **0.0 - 0.3**: Low confidence (review recommended)
- **0.3 - 0.7**: Medium confidence
- **0.7 - 1.0**: High confidence

## Dashboard Features

### Real-time Testing

1. Go to **Dashboard > Make Prediction**
2. Enter text in the input field
3. Click **"Analyze Text"**
4. View results instantly with confidence scores and explanations

### API Testing Playground

1. Navigate to **Dashboard > API Playground**
2. Select your preferred programming language
3. Copy generated code snippets
4. Test with different inputs

### Prediction History

1. Visit **Dashboard > Prediction History**
2. View all your previous predictions
3. Filter by date, prediction type, or confidence
4. Export results for analysis

### Analytics

1. Go to **Dashboard > Analytics**
2. View usage statistics and trends
3. Monitor API call volumes
4. Track model performance over time

## Best Practices

### Input Optimization

1. **Provide complete messages**: Include full email bodies or message threads
2. **Preserve formatting**: Keep original formatting when possible
3. **Use appropriate length**: 10-10,000 characters works best
4. **Test edge cases**: Try various types of content

### Rate Limiting

- **Free tier**: 1,000 calls/hour
- **Business**: 10,000 calls/hour
- **Enterprise**: 100,000 calls/hour

Monitor your usage in the dashboard and upgrade as needed.

### Error Handling

```python
try:
    response = requests.post('https://api.spamguard.com/api/v1/predict',
        headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.RequestException as e:
    print(f"API call failed: {e}")
    # Implement retry logic or fallback
```

### Caching Strategies

```python
import hashlib
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache

def get_prediction_cached(text):
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in cache:
        return cache[cache_key]

    result = make_api_call(text)
    cache[cache_key] = result
    return result
```

## Integration Examples

### Email Filtering

```python
def filter_email(subject, body):
    text = f"{subject} {body}"
    result = spamguard.predict(text)

    if result['prediction'] == 'spam' and result['confidence'] > 0.8:
        move_to_spam_folder(email)
    elif result['prediction'] == 'fraud':
        flag_for_review(email)
    else:
        deliver_to_inbox(email)
```

### Chat Moderation

```javascript
async function moderateMessage(message) {
  const result = await spamguard.predict(message.text);

  if (result.prediction === 'spam') {
    // Hide message or show warning
    message.hidden = true;
    message.warning = 'This message was flagged as spam';
  }

  return message;
}
```

### Fraud Detection

```python
def process_transaction(transaction):
    # Combine multiple fields for analysis
    analysis_text = f"""
    Amount: {transaction.amount}
    Merchant: {transaction.merchant}
    Location: {transaction.location}
    User History: {transaction.user_history}
    """

    result = spamguard.predict(analysis_text)

    if result['prediction'] == 'fraud' and result['confidence'] > 0.7:
        block_transaction(transaction)
        alert_security_team(transaction)
    else:
        approve_transaction(transaction)
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check API key is valid and not expired
   - Ensure Bearer token format: `Bearer <token>`
   - Verify account has sufficient permissions

2. **Rate Limiting**
   - Check `X-RateLimit-Remaining` header
   - Implement exponential backoff for retries
   - Consider upgrading your plan

3. **Low Confidence Scores**
   - Try providing more context
   - Test with similar examples from your domain
   - Consider custom model training

4. **Timeouts**
   - Increase timeout values (recommended: 30 seconds)
   - Check your internet connection
   - Contact support if persistent

### Getting Help

- **Documentation**: [docs.spamguard.com](https://docs.spamguard.com)
- **API Reference**: [api.spamguard.com](https://api.spamguard.com)
- **Community Forum**: [community.spamguard.com](https://community.spamguard.com)
- **Email Support**: support@spamguard.com
- **Phone Support**: Available for Business and Enterprise plans

## Advanced Features

### Custom Model Training

1. Go to **Dashboard > Dataset Upload**
2. Upload your labeled dataset (CSV format)
3. Configure training parameters
4. Monitor training progress
5. Deploy your custom model

### Webhooks

1. Navigate to **Dashboard > Webhooks**
2. Add webhook endpoint URL
3. Select events to monitor
4. Test webhook delivery
5. Monitor delivery logs

### Team Management

1. Go to **Dashboard > Team**
2. Invite team members
3. Assign roles and permissions
4. Monitor team activity
5. Manage API key access

## Security Best Practices

1. **Store API keys securely** - Never commit to version control
2. **Use HTTPS** - Always make API calls over secure connections
3. **Implement rate limiting** - Respect API limits and implement backoff
4. **Monitor usage** - Regularly check your dashboard for unusual activity
5. **Rotate keys regularly** - Generate new keys and retire old ones
6. **Validate inputs** - Sanitize data before sending to API

## What's Next?

- Explore advanced features in your dashboard
- Join our community forum for tips and best practices
- Check out our blog for the latest spam detection techniques
- Consider upgrading to access premium features

Welcome to the SpamGuard community! We're here to help you build safer, more trustworthy applications.