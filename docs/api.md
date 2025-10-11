# API Documentation

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

Rate limiting is enforced:
- Signup: 5 requests/minute
- Login: 10 requests/minute
- Other endpoints: 100 requests/minute

### POST /auth/signup
Create a new user account.

**Rate Limit:** 5/minute

**Request Body:**
```json
{
  "username": "string",  // Min 3 chars, alphanumeric + hyphens/underscores/periods
  "password": "string"   // Min 8 chars, must contain uppercase, lowercase, and digit
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "string"
}
```

**Note:** The response no longer includes `message` or `user_id` fields. Use `id` instead.

### POST /auth/token
Login and receive access token.

**Rate Limit:** 10/minute

**Request Body (form-urlencoded):**
```
username=string&password=string
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later."
}
```

### GET /auth/me
Get current user information (requires authentication).

**Response:**
```json
{
  "id": 1,
  "username": "string"
}
```

## Notes

### POST /notes/
Create a new note.

**Request Body:**
```json
{
  "title": "string",
  "content": "string"
}
```

**Note:** The `node_type` field is no longer returned in responses. Node rendering is determined by the frontend based on note metadata.

### GET /notes/
List all notes for the authenticated user.

### PUT /notes/{note_id}
Update an existing note.

### DELETE /notes/{note_id}
Delete a note.

## Search

### POST /search/
Search notes using semantic similarity.

**Request Body:**
```json
{
  "query": "string",
  "limit": 10
}
```

## Map

### GET /map/
Get neural map visualization data.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "stats": {
    "total_nodes": 0,
    "total_edges": 0
  }
}
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options. Key settings:

- `SECRET_KEY`: **Required** for production (min 32 chars)
- `ENVIRONMENT`: Set to `production` for production deployments
- `ENABLE_HTTPS`: Enable HSTS headers when using HTTPS
- `DATABASE_URL`: Connection string (SQLite default, PostgreSQL recommended for production)