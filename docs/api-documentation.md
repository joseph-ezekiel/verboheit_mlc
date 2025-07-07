# Verboheit Mathematics League Competition (VMLC) API Documentation

A comprehensive REST API for managing VMLC candidates, staff, exams, and leaderboards.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [User Roles & Permissions](#user-roles--permissions)
- [API Endpoints](#api-endpoints)
- [Query Parameters](#query-parameters)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Versioning](#versioning)
- [Interactive Documentation](#interactive-documentation)
- [Support](#support)
- [Changelog](#changelog)

---

## Overview

The VMLC API provides an integrated backend service for the Verboheit Mathematics League Competition, handling registration, exam administration, scoring, and leaderboard functionality with role-based access control.

### Key Features

- **User Management**: Candidate and staff registration with role-based access control
- **Exam System**: Create, manage, and administer timed exams with automatic scoring
- **Leaderboards**: Real-time ranking system based on candidate performance
- **Dashboard**: Personalized views for candidates and staff members
- **Security**: JWT-based authentication with API key protection

### API Characteristics

- **Format**: JSON-only API
- **Authentication**: JWT Bearer tokens with API key requirements
- **Pagination**: Cursor-based pagination for large datasets
- **Rate Limiting**: 100 requests per hour for authenticated users
- **CORS**: Enabled for web applications

---

## Base URL

```
https://verboheit-backend.onrender.com/api/v1/
```

All endpoints are relative to this base URL.

---

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with two-tier security:

### API Key Authentication (Public Endpoints)

Required for registration and login endpoints:

```http
Authorization: Api-Key <your_api_key>
```

### Bearer Token Authentication (Protected Endpoints)

Required for all authenticated endpoints:

```http
Authorization: Bearer <access_token>
```

### Login Flow

**Endpoint:** `POST /auth/login/`

**Headers:**
```http
Authorization: Api-Key <your_api_key>
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:** `200 OK`
```json
{
  "message": "Login successful",
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "user_type": "candidate",
  "user_route": "/api/v1/candidates/me/"
}
```

### Token Management

#### Refresh Token

**Endpoint:** `POST /auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout

**Endpoint:** `POST /auth/logout/`

**Headers:**
```http
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## User Roles & Permissions

### Candidate Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `screening` | Default role for new candidates | Dashboard access, screening exams, own profile |
| `league` | Advanced candidates (staff-assigned) | All screening + league exams + leaderboards |
| `final` | Top performers (staff-assigned) | All league permissions + final stage access |
| `winner` | Competition winner (staff-assigned) | Ceremonial role with all permissions |

### Staff Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `volunteer` | Basic staff member | Limited read access |
| `sponsor` | Competition sponsor | Volunteer permissions + sponsor badge |
| `moderator` | Content moderator | View candidates/staff, manage questions |
| `admin` | System administrator | Full management except staff roles |
| `owner` | Platform owner | All permissions including staff management |

### Role Progression

- **Candidates**: `screening` → `league` → `final` → `winner`
- **Staff**: `volunteer` → `moderator` → `admin` → `owner`

---

## API Endpoints

### Registration & System Controls

#### Toggle Registration Status

Control registration availability for new users.

**Candidate Registration Toggle**

- **Endpoint:** `POST /toggle-candidate-registration/`
- **Required Role:** `admin`, `owner`
- **Request Body:**
  ```json
  {
    "open": false
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "message": "candidate_registration_open: False"
  }
  ```

**Staff Registration Toggle**

- **Endpoint:** `POST /toggle-staff-registration/`
- **Required Role:** `owner`
- **Request Body:** Same as candidate toggle

#### Register New Users

**Candidate Registration**

- **Endpoint:** `POST /register/candidate/`
- **Headers:** `Authorization: Api-Key <your_api_key>`
- **Request Body:**
  ```json
  {
    "user": {
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "password1": "secure_password_123",
    "password2": "secure_password_123",
    "school": "Mathematics High School"
  }
  ```
- **Response:** `201 Created`
  ```json
  {
    "message": "Registration successful"
  }
  ```

**Staff Registration**

- **Endpoint:** `POST /register/staff/`
- **Headers:** `Authorization: Api-Key <your_api_key>`
- **Request Body:**
  ```json
  {
    "user": {
      "username": "jane_smith",
      "email": "jane@example.com",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "password1": "secure_password_123",
    "password2": "secure_password_123",
    "occupation": "Mathematics Teacher"
  }
  ```

### Candidate Management

#### List Candidates

**Endpoint:** `GET /candidates/`

**Required Role:** `moderator`, `admin`, `owner`

**Query Parameters:**
- `page` (integer): Page number for pagination
- `search` (string): Search by name, email, or school
- `role` (string): Filter by candidate role
- `school` (string): Filter by school name
- `verified` (boolean): Filter by verification status

**Response:** `200 OK`
```json
{
  "count": 150,
  "next": "https://verboheit-backend.onrender.com/api/v1/candidates/?page=2",
  "previous": null,
  "results": [
    {
      "user": {
        "id": 123,
        "username": "john_doe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-01-15T10:30:00Z"
      },
      "phone": "+1-555-0123",
      "school": "Mathematics High School",
      "role": "league",
      "is_verified": true,
      "latest_score": 95.5
    }
  ]
}
```

#### Get Candidate Profile

**Own Profile**

- **Endpoint:** `GET /candidates/me/`
- **Required Role:** Any candidate
- **Response:** `200 OK`
  ```json
  {
    "user": {
      "id": 123,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2024-01-15T10:30:00Z"
    },
    "phone": "+1-555-0123",
    "school": "Mathematics High School",
    "role": "league",
    "profile_photo": "https://verboheit.s3.eu-north-1.amazonaws.com/candidate_profile_photos/123.jpg",
    "is_verified": true,
    "date_created": "2024-01-15T10:30:00Z"
  }
  ```

**Specific Candidate**

- **Endpoint:** `GET /candidates/{candidate_id}/`
- **Required Role:** `admin`, `owner`
- **Methods:** `GET`, `PATCH`, `DELETE`

#### Role Management

**Assign Role**

- **Endpoint:** `POST /candidates/{candidate_id}/roles/assign/`
- **Required Role:** `admin`, `owner`
- **Request Body:**
  ```json
  {
    "role": "league"
  }
  ```
- **Valid Roles:** `screening`, `league`, `final`, `winner`

#### Performance Data

**Get Candidate Scores**

- **Endpoint:** `GET /candidates/{candidate_id}/scores/`
- **Required Role:** `admin`, `owner`
- **Response:** `200 OK`
  ```json
  {
    "user": {
      "id": 123,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "school": "Mathematics High School",
    "role": "league",
    "latest_score": 95.5,
    "total_score": 380.0,
    "average_score": 95.0,
    "scores": [
      {
        "exam_id": 1,
        "exam_title": "Algebra Screening",
        "score": 88.0,
        "date_recorded": "2024-01-20T15:30:00Z",
        "submitted_by": {
          "id": 10,
          "name": "Admin User"
        }
      }
    ]
  }
  ```

**Get Exam History**

- **Endpoint:** `GET /candidates/{candidate_id}/exam-history/`
- **Required Role:** `admin`, `owner`
- **Response:** `200 OK`
  ```json
  [
    {
      "exam": "Algebra Screening",
      "score": 88.0,
      "date": "2024-01-20T15:30:00Z",
      "duration_minutes": 87
    }
  ]
  ```

### Staff Management

#### List Staff

**Endpoint:** `GET /staff/`

**Required Role:** `moderator`, `admin`, `owner`

**Query Parameters:**
- `page` (integer): Page number
- `search` (string): Search by name or email
- `role` (string): Filter by staff role
- `occupation` (string): Filter by occupation

#### Staff Profile Management

**Own Profile**

- **Endpoint:** `GET /staff/me/`
- **Required Role:** Any staff member

**Specific Staff Member**

- **Endpoint:** `GET /staff/{staff_id}/`
- **Required Role:** `owner`
- **Methods:** `GET`, `PATCH`, `DELETE`

**Assign Staff Role**

- **Endpoint:** `POST /staff/{staff_id}/roles/assign/`
- **Required Role:** `owner`
- **Request Body:**
  ```json
  {
    "role": "admin"
  }
  ```
- **Valid Roles:** `volunteer`, `moderator`, `admin`, `owner`

### Exam Management

#### List Exams

**Endpoint:** `GET /exams/`

**Required Role:** `admin`, `owner`

**Query Parameters:**
- `page` (integer): Page number
- `stage` (string): Filter by exam stage (`screening`, `league`, `final`)
- `active` (boolean): Filter by active status
- `date_from` (date): Filter exams from date
- `date_to` (date): Filter exams to date

**Response:** `200 OK`
```json
{
  "count": 25,
  "next": "https://verboheit-backend.onrender.com/api/v1/exams/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Algebra Screening Exam",
      "stage": "screening",
      "exam_date": "2024-01-20T15:00:00Z",
      "question_count": 20,
      "is_active": true,
      "average_score": 78.5,
      "participants_count": 45,
      "date_created": "2024-01-10T09:00:00Z"
    }
  ]
}
```

#### Exam Details

**Get Exam Information**

- **Endpoint:** `GET /exams/{exam_id}/`
- **Required Role:** Role depends on exam stage
- **Response:** `200 OK`
  ```json
  {
    "id": 1,
    "title": "Algebra Screening Exam",
    "stage": "screening",
    "description": "Comprehensive algebra exam covering linear equations, polynomials, and systems.",
    "exam_date": "2024-01-20T15:00:00Z",
    "countdown_minutes": 90,
    "open_duration_hours": 24,
    "is_active": true,
    "questions": [1, 4, 8],
    "created_by": {
      "user": {
        "id": 10,
        "username": "admin_user",
        "first_name": "Admin",
        "last_name": "User"
      }
    },
    "average_score": 78.5,
    "participants_count": 45,
    "date_created": "2024-01-10T09:00:00Z"
  }
  ```

#### Exam Interaction

**View Exam Questions**

- **Endpoint:** `GET /exams/{exam_id}/questions/`
- **Required Role:** Appropriate role for exam stage
- **Response:** `200 OK`
  ```json
  {
    "count": 20,
    "results": [
      {
        "id": 1,
        "text": "What is 5 × 5?",
        "option_a": "20",
        "option_b": "25",
        "option_c": "205",
        "option_d": "250",
        "difficulty": "easy"
      }
    ]
  }
  ```

**Take Exam**

- **Endpoint:** `POST /exams/{exam_id}/take-exam/`
- **Required Role:** Candidate with appropriate stage access
- **Response:** `200 OK`
  ```json
  {
    "id": 1,
    "title": "Algebra Screening Exam",
    "stage": "screening",
    "countdown_minutes": 90,
    "questions": [
      {
        "id": 1,
        "text": "What is 5 × 5?",
        "option_a": "20",
        "option_b": "25",
        "option_c": "205",
        "option_d": "250"
      }
    ],
    "start_time": "2024-01-20T15:00:00Z"
  }
  ```

**Submit Exam Answers**

- **Endpoint:** `POST /exams/{exam_id}/submit-exam-answers/`
- **Required Role:** Candidate taking the exam
- **Note:** One submission per candidate per exam
- **Request Body:**
  ```json
  {
    "answers": [
      {
        "question": 1,
        "selected_option": "B"
      },
      {
        "question": 2,
        "selected_option": "A"
      }
    ]
  }
  ```
- **Response:** `200 OK`
  ```json
  {
    "message": "Exam submitted successfully",
    "score": 85.0,
    "correct_answers": 17,
    "total_questions": 20,
    "submission_time": "2024-01-20T16:27:00Z"
  }
  ```

**Submit Manual Score** (Staff only)

- **Endpoint:** `POST /exams/{exam_id}/submit-exam-score/`
- **Required Role:** `admin`, `owner`
- **Request Body:**
  ```json
  {
    "candidate_id": 123,
    "score": 95.5
  }
  ```

### Question Management

#### List Questions

**Endpoint:** `GET /questions/`

**Required Role:** `moderator`, `admin`, `owner`

**Query Parameters:**
- `page` (integer): Page number
- `difficulty` (string): Filter by difficulty (`easy`, `medium`, `hard`)
- `search` (string): Search question text
- `created_by` (integer): Filter by creator ID

**Response:** `200 OK`
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "text": "What is 5 × 5?",
      "difficulty": "easy",
      "date_created": "2024-01-10T09:00:00Z",
      "created_by": {
        "name": "Admin User"
      }
    }
  ]
}
```

#### Question Details

**Get Question**

- **Endpoint:** `GET /questions/{question_id}/`
- **Required Role:** `moderator`, `admin`, `owner`
- **Response:** `200 OK`
  ```json
  {
    "id": 1,
    "text": "What is 5 × 5?",
    "option_a": "20",
    "option_b": "25",
    "option_c": "205",
    "option_d": "250",
    "correct_answer": "B",
    "difficulty": "easy",
    "date_created": "2024-01-10T09:00:00Z",
    "created_by": {
      "user": {
        "id": 4,
        "username": "adminjoe",
        "first_name": "Joe",
        "last_name": "Admin"
      }
    }
  }
  ```

### Dashboard

#### Candidate Dashboard

**Endpoint:** `GET /dashboard/candidate/`

**Required Role:** Any candidate

**Response:** `200 OK`
```json
{
  "candidate_info": {
    "id": 8,
    "name": "Harvey Spectre",
    "email": "harvey@gmail.com",
    "school": "Real Harvard Law",
    "role": "Screening",
    "is_verified": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "profile_photo": "https://verboheit.s3.eu-north-1.amazonaws.com/candidate_profile_photos/8.jpg"
  },
  "exam_stats": {
    "total_exams_taken": 3,
    "available_exams_count": 2,
    "average_score": 87.5,
    "highest_score": 95.0,
    "lowest_score": 78.0,
    "latest_score": 88.0
  },
  "ranking": {
    "position": 15,
    "total_candidates": 150,
    "percentile": 90
  },
  "recent_scores": [
    {
      "exam": "Algebra Screening",
      "score": 88.0,
      "date": "2024-01-20T15:30:00Z"
    }
  ],
  "available_exams": [
    {
      "id": 2,
      "title": "Geometry Screening",
      "stage": "screening",
      "countdown_minutes": 90,
      "question_count": 25,
      "exam_date": "2024-01-25T14:00:00Z"
    }
  ]
}
```

#### Staff Dashboard

**Endpoint:** `GET /dashboard/staff/`

**Required Role:** `moderator`, `admin`, `owner`

**Response:** `200 OK`
```json
{
  "staff_info": {
    "id": 7,
    "name": "Emmanuel Obama",
    "email": "emmaob@gmail.com",
    "role": "Owner",
    "occupation": "Automation Engineer",
    "is_verified": true,
    "date_joined": "2024-01-01T08:00:00Z"
  },
  "candidates": {
    "total": 150,
    "active": 142,
    "verified": 130,
    "recent_registrations": 15,
    "by_role": {
      "screening": { "count": 85 },
      "league": { "count": 45 },
      "final": { "count": 15 },
      "winner": { "count": 5 }
    },
    "verification_rate": 86.7
  },
  "exams": {
    "total": 25,
    "active": 8,
    "recent": 3
  },
  "questions": {
    "total": 500,
    "by_difficulty": {
      "easy": { "count": 200 },
      "medium": { "count": 200 },
      "hard": { "count": 100 }
    }
  },
  "scores": {
    "total_submissions": 1250,
    "recent_submissions": 45,
    "average_score": 78.5,
    "highest_score": 98.0
  },
  "recent_activity": [
    {
      "candidate_name": "Alice Johnson",
      "exam_title": "Algebra Screening",
      "score": 92.0,
      "date": "2024-01-20T16:30:00Z",
      "candidate_school": "Riverdale High"
    }
  ]
}
```

### Leaderboard

#### Toggle Leaderboard Visibility

**Endpoint:** `POST /toggle-leaderboard/`

**Required Role:** `admin`, `owner`

**Request Body:**
```json
{
  "visible": true
}
```

**Response:** `200 OK`
```json
{
  "message": "leaderboard_visible: True"
}
```

#### Publish Leaderboard

**Endpoint:** `POST /publish-leaderboard/`

**Required Role:** `admin`, `owner`

**Response:** `200 OK`
```json
{
  "message": "Leaderboard published!",
  "published_at": "2024-01-20T18:00:00Z",
  "total_candidates": 150
}
```

#### Load Leaderboard

**Endpoint:** `GET /load-leaderboard/`

**Required Role:** `league` candidates and above, all staff

**Query Parameters:**
- `limit` (integer): Number of results (default: 50, max: 100)
- `offset` (integer): Starting position

**Response:** `200 OK`
```json
{
  "published_at": "2024-01-20T18:00:00Z",
  "total_candidates": 150,
  "results": [
    {
      "rank": 1,
      "candidate": {
        "user": {
          "id": 12,
          "first_name": "Alice",
          "last_name": "Johnson",
          "email": "alice@example.com"
        },
        "school": "Riverdale High",
        "profile_photo": "https://verboheit.s3.eu-north-1.amazonaws.com/candidate_profile_photos/12.jpg"
      },
      "total_score": 98.0,
      "exam_count": 4,
      "average_score": 24.5,
      "latest_exam_date": "2024-01-18T14:00:00Z"
    }
  ]
}
```

### Account Management

#### Get Account Information

**Endpoint:** `GET /account-management/`

**Required Role:** Any authenticated user

**Response:** `200 OK`
```json
{
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-15T10:30:00Z",
    "is_active": true
  },
  "profile": {
    "user_type": "candidate",
    "role": "league",
    "is_verified": true,
    "profile_photo": "https://verboheit.s3.eu-north-1.amazonaws.com/candidate_profile_photos/123.jpg"
  }
}
```

#### Update Account

**Endpoint:** `PATCH /account-management/{user_id}/`

**Required Role:** Own account or appropriate staff permissions

**Request Body:**
```json
{
  "first_name": "Jonathan",
  "email": "jonathan@example.com",
  "phone": "+1-555-0124"
}
```

#### Delete Account

**Endpoint:** `DELETE /account-management/{user_id}/`

**Required Role:** `owner`

**Response:** `204 No Content`

### API Root

**Endpoint:** `GET /`

**Response:** `200 OK`
```json
{
  "message": "Welcome to VMLC API",
  "version": "1.0.0",
  "status": "operational",
  "endpoints": {
    "auth": "/auth/",
    "candidates": "/candidates/",
    "staff": "/staff/",
    "exams": "/exams/",
    "questions": "/questions/",
    "dashboard": "/dashboard/",
    "leaderboard": "/leaderboard/",
    "account": "/account-management/"
  },
  "documentation": {
    "swagger": "/swagger/",
    "redoc": "/redoc/"
  }
}
```

---

## Query Parameters

### Common Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | integer | Page number for pagination | `?page=2` |
| `limit` | integer | Items per page (max: 100) | `?limit=25` |
| `search` | string | Search across relevant fields | `?search=john` |
| `ordering` | string | Sort results (`field` or `-field`) | `?ordering=-date_created` |

### Filtering Parameters

| Endpoint | Parameter | Type | Description |
|----------|-----------|------|-------------|
| `/candidates/` | `role` | string | Filter by candidate role |
| `/candidates/` | `school` | string | Filter by school name |
| `/candidates/` | `verified` | boolean | Filter by verification status |
| `/staff/` | `role` | string | Filter by staff role |
| `/staff/` | `occupation` | string | Filter by occupation |
| `/exams/` | `stage` | string | Filter by exam stage |
| `/exams/` | `active` | boolean | Filter by active status |
| `/questions/` | `difficulty` | string | Filter by question difficulty |

### Date Filtering

Use ISO 8601 format for date parameters:

| Parameter | Format | Example |
|-----------|--------|---------|
| `date_from` | YYYY-MM-DD | `?date_from=2024-01-01` |
| `date_to` | YYYY-MM-DD | `?date_to=2024-12-31` |
| `created_after` | YYYY-MM-DDTHH:MM:SS | `?created_after=2024-01-01T10:00:00` |

---

## Error Handling

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Resource deleted successfully |
| 400 | Bad Request | Invalid request data or parameters |
| 401 | Unauthorized | Authentication required or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data",
    "details": {
      "field": "username",
      "reason": "Username already exists"
    }
  },
  "timestamp": "2024-01-20T15:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | Valid authentication token required |
| `INVALID_TOKEN` | Token is expired or invalid |
| `INSUFFICIENT_PERMISSIONS` | User lacks required permissions |
| `VALIDATION_ERROR` | Request validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `DUPLICATE_RESOURCE` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `REGISTRATION_CLOSED` | Registration is currently disabled |
| `EXAM_NOT_AVAILABLE` | Exam is not available for this user |
| `EXAM_ALREADY_TAKEN` | Candidate has already taken this exam |

---

## Versioning

### Current Version

The API is currently at version `v1`. All endpoints are prefixed with `/api/v1/`.

### Versioning Strategy

- **Backwards Compatibility**: Minor changes maintain backwards compatibility
- **Breaking Changes**: Major version increments for breaking changes
- **Deprecation**: 6-month notice period for deprecated endpoints
- **Version Support**: Latest 2 major versions supported

### Version Headers

Include version in requests for explicit version control:

```http
Accept: application/vnd.vmlc.v1+json
```

---

## Interactive Documentation

Explore the API interactively using our documentation interfaces:

- **Swagger UI**: `https://verboheit-backend.onrender.com/swagger/`
- **ReDoc**: `https://verboheit-backend.onrender.com/redoc/`

---

## Support

For technical support, API key requests, or questions:

**Email:** `ezekieloluj@gmail.com`

**Response Time:** Within 48 hours for support requests

**API Key Requests:** Kindly include your organization name and intended use case

---

## Changelog

### Version 1.0.0 (Current)

- Initial API release
- Complete user management system
- Exam administration features
- Leaderboard functionality
- Role-based access control

---

_Last Updated: July 2025_
