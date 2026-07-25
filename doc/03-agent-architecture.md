# VenAI Agent Architecture Document

Version: 1.0  
Project: VenAI  
Architecture Type: Multi-Agent AI System  
Status: Development Planning

---

# 1. Overview

VenAI is built around a multi-agent architecture where specialized AI agents collaborate to complete real-world procurement tasks.

Instead of using one general-purpose AI model, VenAI separates responsibilities into specialized agents.

Each agent has:

- A defined role
- Specific responsibilities
- Available tools
- Input requirements
- Output format
- Memory access rules
- Decision boundaries

The agent system should behave like a digital procurement team.

---

# 2. Agent Architecture Principles

## 2.1 Specialized Intelligence

Each agent should focus on a specific business function.

Example:

A research agent should not negotiate.

A calling agent should not rank suppliers.

An analysis agent should not discover vendors.

Each responsibility should have clear ownership.

---

## 2.2 Agent Collaboration

Agents communicate through structured data rather than uncontrolled conversations.

Example:

Research Agent output:

```json
{
  "vendors": [
    {
      "name": "ABC Furniture",
      "phone": "+234XXXXXXXX",
      "location": "Abuja",
      "category": "Office Furniture"
    }
  ]
}
```

The next agent consumes this structured output.

---

## 2.3 Human Approval

VenAI should support human intervention.

The system should request approval before:

- Purchasing products
- Accepting contracts
- Making financial commitments
- Sharing sensitive information

---

# 3. Agent System Overview

```
                    User Request

                         |

                  Supervisor Agent

                         |

        ----------------------------------

        |              |                |

 Research Agent   Calling Agent   Analysis Agent

        |              |                |

        ----------------------------------

                         |

                  Report Agent

                         |

                    User Output
```

---

# 4. Supervisor Agent

## Role

The Supervisor Agent is the central coordinator of VenAI.

It manages the complete procurement workflow.

---

## Responsibilities

The Supervisor Agent must:

- Understand user objectives
- Break tasks into smaller operations
- Assign tasks to specialized agents
- Track workflow progress
- Handle failures
- Request clarification when needed
- Decide when the workflow is complete

---

## Input

Example:

```
Find suppliers for 500 office chairs.

Location:
Abuja

Budget:
₦10 million
```

---

## Output

Creates an execution plan:

```json
{
  "objective": "Find office chair suppliers",
  "tasks": [
    "discover vendors",
    "contact vendors",
    "compare offers",
    "generate recommendation"
  ]
}
```

---

## Tools

The Supervisor Agent can access:

- Agent execution tools
- Workflow memory
- User information
- Procurement history

---

# 5. Research Agent

## Role

The Research Agent discovers and evaluates potential vendors.

---

## Responsibilities

The Research Agent must:

- Search for vendors
- Collect business information
- Validate available information
- Identify contact channels
- Prepare vendor profiles

---

## Inputs

Receives:

- Product requirement
- Location
- Quantity
- Budget
- Business category

---

## Outputs

Returns:

```json
{
  "vendor_candidates": [
    {
      "company": "Example Vendor",
      "phone": "+234XXXXXXXX",
      "website": "example.com",
      "location": "Lagos",
      "confidence": 0.85
    }
  ]
}
```

---

## Tools

Possible tools:

- Search APIs
- Business directories
- Internal vendor database
- Web extraction tools

---

# 6. Calling Agent

## Role

The Calling Agent manages real-world phone conversations using CALL-E.

---

## Responsibilities

The Calling Agent must:

- Prepare conversation objectives
- Generate call scripts dynamically
- Start phone calls
- Ask relevant questions
- Handle unexpected responses
- Capture vendor information
- Summarize conversations

---

## Conversation Goals

The agent should collect:

- Product availability
- Price
- Delivery time
- Warranty
- Payment terms
- Minimum order quantity
- Negotiation opportunities

---

## Example Call Objective

```
Contact vendor.

Ask:
1. Do you supply office chairs?
2. What is your price for 500 units?
3. How soon can you deliver?
4. Are discounts available?
```

---

## Outputs

```json
{
  "vendor": "Example Company",
  "available": true,
  "price": "₦8,500,000",
  "delivery": "14 days",
  "warranty": "3 years",
  "notes": "Vendor willing to negotiate"
}
```

---

# 7. Analysis Agent

## Role

The Analysis Agent evaluates collected vendor information.

---

## Responsibilities

The Analysis Agent must:

- Compare vendor responses
- Analyze pricing
- Evaluate reliability
- Rank suppliers
- Explain recommendations

---

## Evaluation Factors

The agent considers:

- Price
- Quality
- Delivery speed
- Warranty
- Location
- Vendor confidence
- Previous history

---

## Output Example

```json
{
  "recommendation": {
    "vendor": "Example Company",
    "score": 92,
    "reason": [
      "Best price",
      "Fast delivery",
      "Strong warranty"
    ]
  }
}
```

---

# 8. Report Agent

## Role

The Report Agent converts AI results into useful business reports.

---

## Responsibilities

The Report Agent creates:

- Procurement summaries
- Vendor comparison tables
- Recommendation explanations
- Executive summaries

---

## Example Output

```
Procurement Recommendation

Recommended Supplier:
ABC Furniture

Total Cost:
₦8.5 million

Advantages:
- Lowest price
- 14-day delivery
- 3-year warranty

Alternative:
XYZ Furniture
```

---

# 9. Agent Memory System

VenAI agents should have access to controlled memory.

---

## Short-Term Memory

Used during active workflows.

Examples:

- Current procurement request
- Current vendor conversation
- Current task state

---

## Long-Term Memory

Stored knowledge:

- Previous vendors
- Previous prices
- Successful negotiations
- User preferences

---

## Memory Rules

Agents must:

- Store useful information
- Avoid storing unnecessary personal data
- Retrieve relevant historical information only

---

# 10. AI Model Requirements

## Primary Model

Google Gemini API Free Tier

---

## Requirements

The AI layer must:

- Support model abstraction
- Allow future provider changes
- Reduce unnecessary requests
- Cache repeated responses
- Use structured outputs where possible

---

# 11. Agent Error Handling

Agents must handle:

## Missing Information

Example:

User:

"Find suppliers."

Agent:

"Which product category should I search for?"

---

## Failed Calls

Possible actions:

- Retry call
- Contact another vendor
- Mark vendor unavailable

---

## Incorrect Data

Agents must:

- Flag uncertainty
- Avoid inventing information
- Request verification

---

# 12. Future Agent Expansion

VenAI architecture should allow additional agents.

Future agents:

## Sales Agent

Handles outbound sales.

---

## Customer Support Agent

Handles customer conversations.

---

## Market Intelligence Agent

Collects business intelligence.

---

## Verification Agent

Validates businesses and suppliers.

---

# 13. Final Agent Architecture Goal

VenAI should operate as an autonomous AI business workforce.

The long-term vision:

```
                 VenAI Intelligence Layer

                         |

 ------------------------------------------------

 Procurement     Sales     Research     Support

 ------------------------------------------------

                         |

                 Real World Execution

                         |

              Phone / Email / Messaging
```

The system should move beyond answering questions and become capable of completing real business operations.

