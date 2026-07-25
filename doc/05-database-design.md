# VenAI Database Design Document

Version: 1.0  
Project: VenAI  
Database Type: Relational + Vector Memory Database  
Primary Database: PostgreSQL  
Status: Development Planning

---

# 1. Database Overview

The VenAI database is responsible for storing all application data required for:

- User management
- Organizations
- Procurement workflows
- Vendor intelligence
- AI agent execution
- Phone conversations
- Recommendations
- Historical business knowledge

The database must support both traditional application data and AI memory.

---

# 2. Database Design Principles

## 2.1 Data Separation

Business data and AI execution data should be logically separated.

Examples:

Business Data:

- Vendors
- Products
- Procurement requests
- Organizations

AI Data:

- Agent tasks
- Agent states
- Memories
- Reasoning metadata

---

## 2.2 Multi-Tenant Architecture

VenAI is a B2B SaaS platform.

The database must support multiple organizations.

Every organization-owned resource must include:

```
organization_id
```

Example:

A vendor saved by Company A should not be visible to Company B.

---

## 2.3 Data Integrity

Requirements:

- Foreign key relationships
- Database constraints
- Proper indexing
- Validation before storage

---

# 3. Core Database Entities

Main entities:

```
Users

Organizations

Organization Members

Procurement Requests

Vendors

Vendor Contacts

Calls

Call Transcripts

Offers

Agent Tasks

Agent Memories

Recommendations

Notifications
```

---

# 4. Users Table

Purpose:

Stores application users.

Table:

```
users
```

Fields:

```
id
uuid
email
name
avatar_url
authentication_provider
created_at
updated_at
```

---

Relationships:

One user can belong to multiple organizations.

---

# 5. Organizations Table

Purpose:

Represents businesses using VenAI.

Table:

```
organizations
```

Fields:

```
id
uuid

name

industry

company_size

country

created_at

updated_at
```

---

Examples:

```
ABC Construction Ltd

Industry:
Construction

Size:
50 employees
```

---

# 6. Organization Members Table

Purpose:

Connects users to organizations.

Table:

```
organization_members
```

Fields:

```
id

organization_id

user_id

role

created_at
```

Roles:

```
owner

admin

member

viewer
```

---

# 7. Procurement Requests Table

Purpose:

Stores user procurement requirements.

Table:

```
procurement_requests
```

Fields:

```
id

organization_id

created_by

title

description

category

product_name

quantity

budget

currency

location

requirements

status

created_at

updated_at
```

---

Example:

```
title:
Office Furniture Procurement

product_name:
Office Chairs

quantity:
500

budget:
10000000

currency:
NGN

location:
Abuja
```

---

Status values:

```
draft

searching

calling

analyzing

completed

cancelled
```

---

# 8. Vendors Table

Purpose:

Stores discovered and verified vendors.

Table:

```
vendors
```

Fields:

```
id

organization_id

company_name

industry

description

website

email

phone

country

state

city

address

source

verification_status

created_at

updated_at
```

---

Source examples:

```
search_api

user_input

directory

previous_call
```

---

Verification status:

```
unknown

verified

unverified

rejected
```

---

# 9. Vendor Contacts Table

Purpose:

Stores vendor contact persons.

Table:

```
vendor_contacts
```

Fields:

```
id

vendor_id

name

position

phone

email

created_at
```

---

# 10. Vendor History Table

Purpose:

Stores historical interactions with vendors.

Table:

```
vendor_history
```

Fields:

```
id

vendor_id

interaction_type

summary

rating

created_at
```

---

Examples:

```
interaction_type:

phone_call

previous_purchase

verification
```

---

# 11. Agent Tasks Table

Purpose:

Tracks AI agent operations.

Table:

```
agent_tasks
```

Fields:

```
id

organization_id

procurement_request_id

agent_type

status

input_data

output_data

started_at

completed_at

created_at
```

---

Agent types:

```
supervisor

research

calling

analysis

report
```

---

Status:

```
pending

running

completed

failed

waiting_approval
```

---

# 12. Agent Execution Logs Table

Purpose:

Stores AI workflow history.

Table:

```
agent_logs
```

Fields:

```
id

agent_task_id

agent_name

action

input

output

execution_time

created_at
```

---

Purpose:

Allows:

- Debugging
- Monitoring
- Improving prompts

---

# 13. Calls Table

Purpose:

Stores CALL-E phone call information.

Table:

```
calls
```

Fields:

```
id

organization_id

vendor_id

agent_task_id

call_provider

external_call_id

status

phone_number

duration

started_at

ended_at

created_at
```

---

Status:

```
queued

ringing

connected

completed

failed

cancelled
```

---

# 14. Call Transcripts Table

Purpose:

Stores phone conversation data.

Table:

```
call_transcripts
```

Fields:

```
id

call_id

transcript

summary

sentiment

language

created_at
```

---

Example:

```
Vendor confirmed availability.

Price:
₦8,500,000

Delivery:
14 days
```

---

# 15. Vendor Offers Table

Purpose:

Stores structured vendor responses.

Table:

```
vendor_offers
```

Fields:

```
id

vendor_id

procurement_request_id

call_id

price

currency

delivery_time

warranty

payment_terms

availability

notes

confidence_score

created_at
```

---

# 16. Recommendations Table

Purpose:

Stores AI-generated decisions.

Table:

```
recommendations
```

Fields:

```
id

procurement_request_id

recommended_vendor_id

score

reasoning

summary

created_at
```

---

Example:

```
score:

92

reasoning:

Best price and fastest delivery.
```

---

# 17. Agent Memory Table

Purpose:

Stores long-term AI knowledge.

Uses:

PostgreSQL + pgvector.

Table:

```
agent_memories
```

Fields:

```
id

organization_id

memory_type

content

embedding

importance_score

created_at
```

---

Memory types:

```
vendor_information

conversation_summary

user_preference

business_pattern
```

---

# 18. Notifications Table

Purpose:

Stores user alerts.

Table:

```
notifications
```

Fields:

```
id

user_id

type

title

message

read_status

created_at
```

---

Examples:

```
Vendor call completed.

New recommendation available.
```

---

# 19. Database Relationships

```
Organization

    |

    |--- Users

    |

    |--- Procurement Requests

              |

              |--- Agent Tasks

              |

              |--- Vendors

                      |

                      |--- Calls

                      |

                      |--- Offers


Calls

    |

    |--- Transcripts


Procurement Request

    |

    |--- Recommendations
```

---

# 20. Indexing Requirements

Important indexes:

## Vendors

```
industry

location

company_name

phone
```

---

## Procurement Requests

```
organization_id

status

created_at
```

---

## Calls

```
vendor_id

status

created_at
```

---

## Agent Tasks

```
status

agent_type

created_at
```

---

# 21. Data Security Requirements

The database must:

- Encrypt sensitive information
- Restrict organization data access
- Avoid storing unnecessary personal information
- Maintain audit history
- Protect API-related data

---

# 22. Migration Requirements

Database changes must use migrations.

Recommended:

```
Alembic
```

Rules:

- No manual production database changes
- Every schema update requires migration
- Migration files must be version controlled

---

# 23. Future Database Expansion

Future entities may include:

```
Supplier Contracts

Purchase Orders

Invoices

Payments

CRM Records

Communication Channels

Business Intelligence Reports
```

---

# 24. Final Database Goal

The VenAI database must provide a reliable foundation for an autonomous AI procurement workforce.

It must store:

- Business knowledge
- Human interactions
- AI decisions
- Vendor intelligence
- Workflow history

while remaining secure, scalable, and extensible.