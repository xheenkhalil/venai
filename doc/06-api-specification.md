# VenAI API Specification Document

Version: 1.0  
Project: VenAI  
API Architecture: REST API  
Backend Framework: FastAPI  
Status: Development Planning

---

# 1. API Overview

The VenAI API is the central communication layer between:

- Frontend application
- AI agent system
- Database
- External integrations
- Background workers

The API must provide secure and structured access to all VenAI capabilities.

---

# 2. API Design Principles

## 2.1 REST Architecture

The API follows REST principles.

Requirements:

- Resource-based endpoints
- JSON request and response format
- HTTP status codes
- Versioned endpoints

Base URL:

```
/api/v1
```

---

## 2.2 Authentication

All protected endpoints require authentication.

Authentication method:

```
Bearer Token
```

Example:

```
Authorization: Bearer <token>
```

---

## 2.3 Response Format

Successful response:

```json
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully"
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request validation failed"
  }
}
```

---

# 3. Authentication API

## 3.1 Get Current User

Endpoint:

```
GET /auth/me
```

Purpose:

Retrieve authenticated user information.

Response:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

---

# 4. Organization API

## 4.1 Create Organization

Endpoint:

```
POST /organizations
```

Purpose:

Create a business workspace.

Request:

```json
{
  "name": "ABC Construction",
  "industry": "Construction",
  "country": "Nigeria"
}
```

Response:

```json
{
  "id": "uuid",
  "name": "ABC Construction"
}
```

---

## 4.2 Get Organization

Endpoint:

```
GET /organizations/{id}
```

---

## 4.3 Update Organization

Endpoint:

```
PATCH /organizations/{id}
```

---

# 5. Procurement Request API

## 5.1 Create Procurement Request

Endpoint:

```
POST /procurement-requests
```

Purpose:

Create a new AI procurement workflow.

Request:

```json
{
  "title": "Office Chairs",
  "product_name": "Office Chairs",
  "quantity": 500,
  "budget": 10000000,
  "currency": "NGN",
  "location": "Abuja",
  "requirements": [
    "3 year warranty",
    "Fast delivery"
  ]
}
```

Response:

```json
{
  "id": "uuid",
  "status": "draft"
}
```

---

## 5.2 List Procurement Requests

Endpoint:

```
GET /procurement-requests
```

Query parameters:

```
status
page
limit
```

---

## 5.3 Get Procurement Request

Endpoint:

```
GET /procurement-requests/{id}
```

Returns:

- Request details
- Agent progress
- Vendors
- Calls
- Recommendations

---

## 5.4 Start Procurement Workflow

Endpoint:

```
POST /procurement-requests/{id}/start
```

Purpose:

Start the AI agent workflow.

Process:

```
Request

↓

Supervisor Agent

↓

Research Agent

↓

Calling Agent

↓

Analysis Agent

↓

Report Agent
```

Response:

```json
{
  "task_id": "uuid",
  "status": "started"
}
```

---

# 6. Vendor API

## 6.1 List Vendors

Endpoint:

```
GET /vendors
```

Filters:

```
industry

location

verification_status
```

---

## 6.2 Get Vendor

Endpoint:

```
GET /vendors/{id}
```

Returns:

- Vendor details
- Previous interactions
- Offers
- Calls

---

## 6.3 Create Vendor

Endpoint:

```
POST /vendors
```

Purpose:

Allow manual vendor addition.

Request:

```json
{
  "company_name": "ABC Supplies",
  "phone": "+234XXXXXXXX",
  "location": "Lagos"
}
```

---

# 7. Agent Workflow API

## 7.1 Get Agent Tasks

Endpoint:

```
GET /agent-tasks
```

Returns:

Active and completed AI tasks.

---

## 7.2 Get Agent Task

Endpoint:

```
GET /agent-tasks/{id}
```

Response:

```json
{
  "agent": "research",
  "status": "completed",
  "result": {}
}
```

---

# 8. CALL-E Integration API

## 8.1 Start Vendor Call

Endpoint:

```
POST /calls/start
```

Purpose:

Initiate a phone conversation.

Request:

```json
{
  "vendor_id": "uuid",
  "objective": "Collect pricing information"
}
```

Response:

```json
{
  "call_id": "uuid",
  "status": "queued"
}
```

---

## 8.2 Get Call Status

Endpoint:

```
GET /calls/{id}
```

Returns:

```json
{
  "status": "completed",
  "duration": 240
}
```

---

## 8.3 Get Transcript

Endpoint:

```
GET /calls/{id}/transcript
```

Response:

```json
{
  "transcript": "Conversation text",
  "summary": "Vendor available"
}
```

---

# 9. Offer API

## 9.1 List Vendor Offers

Endpoint:

```
GET /offers
```

Filters:

```
procurement_request_id

vendor_id
```

---

## 9.2 Get Offer

Endpoint:

```
GET /offers/{id}
```

---

# 10. Recommendation API

## 10.1 Get Recommendation

Endpoint:

```
GET /recommendations/{procurement_request_id}
```

Response:

```json
{
  "vendor": "ABC Supplies",
  "score": 94,
  "reason": [
    "Lowest price",
    "Fast delivery"
  ]
}
```

---

# 11. AI Agent API

## 11.1 Execute Agent Task

Endpoint:

```
POST /agents/execute
```

Purpose:

Internal endpoint for agent execution.

Request:

```json
{
  "agent_type": "research",
  "task_id": "uuid",
  "input": {}
}
```

---

# 12. Search API

## 12.1 Search Vendors

Endpoint:

```
POST /search/vendors
```

Request:

```json
{
  "category": "Office Furniture",
  "location": "Abuja"
}
```

Response:

```json
{
  "vendors": []
}
```

---

# 13. Report API

## 13.1 Generate Report

Endpoint:

```
POST /reports/generate
```

Request:

```json
{
  "procurement_request_id": "uuid"
}
```

---

## 13.2 Get Report

Endpoint:

```
GET /reports/{id}
```

---

# 14. Notification API

## 14.1 Get Notifications

Endpoint:

```
GET /notifications
```

---

## 14.2 Mark Notification Read

Endpoint:

```
PATCH /notifications/{id}/read
```

---

# 15. WebSocket Events

For real-time updates:

Endpoint:

```
/ws
```

Events:

```
procurement.started

vendor.found

call.started

call.completed

analysis.completed

report.generated
```

Example:

```json
{
  "event": "call.completed",
  "data": {
    "call_id": "uuid"
  }
}
```

---

# 16. Internal Service Communication

Internal services communicate through:

- API calls
- Task queues
- Event messages

Example:

```
Supervisor Agent

↓

Task Queue

↓

Research Agent Worker

↓

Database Update

↓

Notification Event
```

---

# 17. API Security Requirements

The API must implement:

- Authentication
- Authorization
- Rate limiting
- Input validation
- Request logging
- Secure secret management

---

# 18. API Documentation

FastAPI must automatically generate:

```
/docs
```

and

```
/redoc
```

Documentation must remain updated with implementation changes.

---

# 19. Future API Expansion

Possible future endpoints:

```
/sales-agents

/customer-agents

/contracts

/purchase-orders

/integrations

/analytics
```

---

# 20. Final API Goal

The VenAI API should provide a reliable foundation for:

- AI workflows
- Business operations
- Phone automation
- Vendor intelligence
- Future AI workforce expansion