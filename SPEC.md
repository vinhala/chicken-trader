# Software Specification Document

**Project:** AI-Powered Daily Investment Opportunity Web Application  
**Version:** 1.0.0  
**Status:** Draft  
**Date:** 2026-03-16

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Stakeholders and User Roles](#3-stakeholders-and-user-roles)
4. [Functional Requirements](#4-functional-requirements)
   - 4.1 [News Ingestion](#41-news-ingestion)
   - 4.2 [AI-Based Opportunity Detection](#42-ai-based-opportunity-detection)
   - 4.3 [AI-Generated Investment Reports](#43-ai-generated-investment-reports)
   - 4.4 [Security Detail Lookup](#44-security-detail-lookup)
   - 4.5 [Following an Investment Thesis](#45-following-an-investment-thesis)
   - 4.6 [Thesis Monitoring System](#46-thesis-monitoring-system)
   - 4.7 [AI Thesis Reevaluation](#47-ai-thesis-reevaluation)
   - 4.8 [User Notifications](#48-user-notifications)
5. [User Interface Requirements](#5-user-interface-requirements)
   - 5.1 [Daily Opportunities Dashboard](#51-daily-opportunities-dashboard)
   - 5.2 [Opportunity Detail Page](#52-opportunity-detail-page)
   - 5.3 [Followed Ideas Dashboard](#53-followed-ideas-dashboard)
   - 5.4 [Notifications Centre](#54-notifications-centre)
   - 5.5 [Watchlist](#55-watchlist)
   - 5.6 [Security Detail View](#56-security-detail-view)
   - 5.7 [Landing Page](#57-landing-page)
6. [System Architecture](#6-system-architecture)
   - 6.1 [Frontend](#61-frontend)
   - 6.2 [Backend](#62-backend)
   - 6.3 [AI Layer](#63-ai-layer)
   - 6.4 [Data Sources](#64-data-sources)
7. [Data Models](#7-data-models)
8. [Non-Functional Requirements](#8-non-functional-requirements)
9. [Compliance and Legal Requirements](#9-compliance-and-legal-requirements)
10. [Out of Scope](#10-out-of-scope)
11. [Glossary](#11-glossary)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the functional and technical requirements for an AI-powered web application that delivers daily, news-driven investment insights. It is intended as the authoritative reference for development, testing, and product decisions.

### 1.2 Background

Global financial markets react continuously to macroeconomic and geopolitical events. Retail investors and analysts often lack the tooling to rapidly identify, interpret, and track such opportunities. This application bridges that gap by combining news ingestion, AI analysis, and lightweight trade-idea lifecycle management into a single interface.

### 1.3 Scope

The system encompasses:

- Automated ingestion and classification of global financial news.
- AI-generated, structured investment opportunity reports.
- User-initiated thesis-following and lifecycle tracking.
- Automated monitoring and notification when a thesis changes status.
- A Vue.js-based single-page application as the user interface.

### 1.4 Definitions and Abbreviations

| Term | Definition |
|---|---|
| Thesis | An AI-generated investment argument tied to a specific news event. |
| Opportunity | A news event identified by the system as having investment relevance. |
| Follow | A user action that activates thesis tracking for a specific opportunity. |
| Reevaluation | A periodic AI process that reassesses whether a thesis remains valid. |
| SPA | Single-Page Application. |
| ETF | Exchange-Traded Fund. |

---

## 2. System Overview

The system operates as two tightly coupled subsystems:

**Discovery subsystem** — continuously ingests news, filters events by market relevance, and generates structured AI investment reports for the most significant stories.

**Tracking subsystem** — when a user elects to follow an opportunity, creates a persistent thesis record, monitors related news and market signals over time, and notifies the user when the thesis status changes.

### 2.1 High-Level Flow

```
News APIs → Ingestion → Deduplication & Clustering → AI Relevance Filter
    → AI Report Generation → Opportunity Dashboard
        → User follows idea → Thesis Record created
            → Monitoring Loop (news + market signals)
                → AI Reevaluation → Status Update → User Notification
```

---

## 3. Stakeholders and User Roles

| Role | Description |
|---|---|
| Authenticated User | A registered user who can read reports, follow theses, and receive notifications. |
| Guest | An unauthenticated visitor. Access is limited to the public landing page; the application dashboard and all authenticated features require registration and login. |
| System (AI Agent) | The automated backend process responsible for ingestion, report generation, monitoring, and reevaluation. |
| Administrator | Internal operator with access to system configuration, ingestion pipeline controls, and AI prompt management. |

---

## 4. Functional Requirements

### 4.1 News Ingestion

**REQ-ING-001** The system shall periodically fetch articles from one or more external news APIs on a configurable schedule (minimum frequency: every 30 minutes).

**REQ-ING-002** The ingestion pipeline shall cover at minimum the following news categories:

- Financial markets and equities
- Macroeconomics and central bank policy
- Geopolitics and international relations
- Corporate events (mergers, acquisitions, earnings)
- Commodities and energy
- Technology and industrial supply chains
- Regulatory and legislative changes

**REQ-ING-003** The system shall deduplicate ingested articles using content hashing or semantic similarity before further processing.

**REQ-ING-004** The system shall cluster related articles into a single event record when they refer to the same underlying story.

**REQ-ING-005** Each event cluster shall be assigned a market relevance rank by the AI model prior to report generation.

**REQ-ING-006** Raw ingested articles shall be stored with a reference to their source URL, publication timestamp, and source provider name to ensure traceability.

**REQ-ING-007** The news ingestion pipeline shall fetch articles from the following NewsAPI categories: `business`, `general`, and `technology`.

---

### 4.2 AI-Based Opportunity Detection

**REQ-DET-001** An AI model shall evaluate each event cluster and determine whether it warrants the generation of an investment report.

**REQ-DET-002** The AI classifier shall assess events against the following dimensions:

- Expected market impact (low / medium / high)
- Time sensitivity (immediate / short-term / medium-term)
- Affected sectors and asset classes
- Geographic relevance
- Tradability of related securities

**REQ-DET-003** Only events classified as having medium or high expected market impact shall proceed to report generation.

**REQ-DET-004** Classification output shall be stored alongside the event record for audit and display purposes.

**REQ-DET-005** Event records surfaced to the opportunity dashboard shall be sorted in descending order of expected market impact: High → Medium → Low.

---

### 4.3 AI-Generated Investment Reports

**REQ-RPT-001** For each qualifying event, the system shall generate a structured investment report.

**REQ-RPT-002** Each report shall contain the following fields:

| Field | Description |
|---|---|
| Headline | A concise, plain-language description of the triggering event. |
| Event Summary | 2–4 sentences explaining what occurred. |
| Market Interpretation | An explanation of why the event is relevant to financial markets. |
| Historical or Analytical Context | Reference to similar past events or established analyst reasoning patterns, where applicable. |
| Suggested Securities | A mini-portfolio of 3–5 tradable instruments (see REQ-RPT-003). |
| Risk Considerations | Specific reasons the thesis could fail or be invalidated. |
| AI Confidence Indicator | A qualitative rating (e.g., Low / Medium / High) or numeric score (0–100). |
| Thesis Conditions | A set of conditions that would indicate the thesis has played out or been invalidated. |
| Suggested Time Horizon | One of: Short-term / Medium-term / Event-driven. |

**REQ-RPT-003** Each entry in the Suggested Securities list shall include:

- Ticker symbol
- Company or asset name
- Asset type (Stock, ETF, Index, Commodity, etc.)
- Relationship to the event
- Expected directional impact (Long / Short / Neutral)
- Brief justification (1–2 sentences)

**REQ-RPT-004** AI output shall be structured as a JSON object conforming to the schema defined in Section 7.2.

**REQ-RPT-005** Each report shall maintain a reference to the source event cluster and its constituent articles.

---

### 4.4 Security Detail Lookup

**REQ-SDL-001** The system shall expose an API endpoint that, given a ticker symbol, returns enriched security metadata sourced from an external market data provider.

**REQ-SDL-002** The security metadata response shall include:

- Full legal name of the security
- List of exchanges on which the security is tradable
- Security type (e.g., Common Stock, ETF, Index, Commodity, etc.)
- Previous close price

---

### 4.5 Following an Investment Thesis

**REQ-FOL-001** An authenticated user shall be able to follow any active investment opportunity from its detail page.

**REQ-FOL-002** The system shall create a thesis tracking record upon a user following an opportunity. The record shall store:

- User ID
- Event ID
- Report ID (snapshot of the report at follow time)
- List of recommended securities included in the thesis
- Timestamp of the follow action
- AI thesis summary (captured at follow time)
- Suggested time horizon
- Thesis conditions (captured at follow time)
- Current thesis status (Active / Warning / Close Suggested / Closed)

**REQ-FOL-003** A user shall be able to follow the same opportunity only once. Attempting to follow an already-followed opportunity shall surface the existing tracking record.

**REQ-FOL-004** A user shall be able to manually mark a followed thesis as closed at any time.

**REQ-FOL-005** A user shall be able to unfollow an investment idea at any time. Unfollowing shall permanently remove the thesis tracking record from the user's followed ideas list.

**REQ-FOL-006** The thesis tracking record shall store the headline of the original investment report, captured at follow time, as the canonical display name for the followed idea.

**REQ-FOL-007** The thesis tracking record shall maintain a persistent reference to the original investment report, ensuring it remains accessible to the user regardless of whether the opportunity is still listed on the dashboard.

---

### 4.6 Thesis Monitoring System

**REQ-MON-001** The backend shall operate a continuous monitoring loop for all thesis records with status Active or Warning.

**REQ-MON-002** The monitoring system shall perform the following checks on a configurable schedule (minimum frequency: every 12 hours):

**News Monitoring:**

- Detect follow-up articles related to the same event cluster.
- Identify articles containing contradictory developments.
- Identify articles confirming the original thesis.

**Market Monitoring (where data is available):**

- Track price movement of each security in the thesis.
- Monitor relevant sector indices.
- Monitor related commodity or macroeconomic indicators.

**REQ-MON-003** All monitoring checks shall produce a structured result that is passed as context to the AI Reevaluation process (REQ-REV).

---

### 4.7 AI Thesis Reevaluation

**REQ-REV-001** The AI reevaluation process shall be triggered automatically after each monitoring cycle for each active thesis.

**REQ-REV-002** The reevaluation process shall consider the monitoring results alongside the original thesis conditions and report.

**REQ-REV-003** The reevaluation shall produce one of the following status outcomes:

| Status | Description |
|---|---|
| Active | The thesis conditions remain intact; no action required. |
| Warning | New information partially challenges the thesis; the user should review. |
| Close Suggested | The thesis has played out, been invalidated, or the opportunity window has likely passed. |

**REQ-REV-004** The reevaluation shall produce a structured explanation of the status change for inclusion in user notifications.

**REQ-REV-005** Thesis status changes shall be persisted to the tracking record with a timestamp and the reevaluation rationale.

---

### 4.8 User Notifications

**REQ-NOT-001** The system shall generate a notification whenever a thesis status changes to Warning or Close Suggested.

**REQ-NOT-002** Each notification shall contain:

- Event name and original headline
- Original thesis summary
- New thesis status
- Plain-language explanation of the reason for the change
- List of affected securities
- Suggested action (e.g., "Review position" or "Consider closing")

**REQ-NOT-003** Notifications shall be delivered via the following channels:

- In-app notification centre (required)
- Email (required)
- Browser push notification (optional, user opt-in)

**REQ-NOT-004** Users shall be able to configure notification channel preferences per channel independently.

**REQ-NOT-005** All notifications shall be stored in the user's notification history, accessible from the Notifications Centre view.

---

## 5. User Interface Requirements

The frontend shall be a single-page application built with Vue.js and Vite. All views shall be responsive and support both desktop and mobile viewports.

### 5.1 Daily Opportunities Dashboard

**REQ-UI-DASH-001** The dashboard shall be the default landing view after authentication.

**REQ-UI-DASH-002** The dashboard shall display a list of AI-detected investment opportunities for the current day.

**REQ-UI-DASH-003** Each opportunity card shall display:

- Headline
- Short summary (truncated to ~2 lines)
- Affected sector(s)
- AI confidence indicator
- Expected market impact (High / Medium / Low)
- Creation time (date and time the report was generated)
- A link or button to open the full report

**REQ-UI-DASH-004** The dashboard shall support filtering by sector, time horizon, and confidence level.

**REQ-UI-DASH-005** Opportunities on the dashboard shall be ordered by expected market impact in descending order (High first, then Medium, then Low).

**REQ-UI-DASH-006** The dashboard shall display a prominent disclaimer that all content is AI-generated and informational only.

---

### 5.2 Opportunity Detail Page

**REQ-UI-DET-001** The detail page shall render the full investment report for a selected opportunity.

**REQ-UI-DET-002** The detail page shall include all report fields specified in REQ-RPT-002, as well as the creation timestamp of the report (date and time the report was generated).

**REQ-UI-DET-003** Each suggested security entry shall be displayed in a structured format (card or table row) including all fields specified in REQ-RPT-003.

**REQ-UI-DET-004** The page shall display a "Follow Investment Idea" call-to-action, visible to authenticated users.

**REQ-UI-DET-005** If the user has already followed the idea, the call-to-action shall be replaced with a link to their active thesis tracking record.

**REQ-UI-DET-006** Source articles shall be accessible via reference links at the bottom of the report.

**REQ-UI-DET-007** Each suggested security entry shall be interactive. Clicking or tapping a security entry shall open a detail view (e.g., a modal or slide-over panel) displaying the enriched security metadata specified in REQ-SDL-002.

---

### 5.3 Followed Ideas Dashboard

**REQ-UI-FOL-001** Authenticated users shall have access to a view listing all investment theses they are actively following.

**REQ-UI-FOL-002** Each entry in the list shall display:

- Event title and headline
- Securities involved (ticker list)
- Date the user followed the idea
- Current thesis status with a visual indicator (Active / Warning / Close Suggested)
- Date of last status update
- A link to the full report

**REQ-UI-FOL-003** The view shall support filtering by thesis status.

**REQ-UI-FOL-004** Users shall be able to manually close a thesis from this view.

**REQ-UI-FOL-005** Users shall be able to unfollow an investment idea from the Followed Ideas Dashboard. An unfollow action shall prompt the user for confirmation before removing the record.

**REQ-UI-FOL-006** Each followed idea shall be identified in the Followed Ideas Dashboard by the headline of the original investment report, as captured at follow time (see REQ-FOL-006).

**REQ-UI-FOL-007** Users shall be able to navigate to the full original investment report from each followed idea entry in the Followed Ideas Dashboard.

---

### 5.4 Notifications Centre

**REQ-UI-NOT-001** The notifications centre shall display all thesis update notifications for the authenticated user.

**REQ-UI-NOT-002** Notifications shall be displayed in reverse-chronological order.

**REQ-UI-NOT-003** Each notification entry shall surface all fields specified in REQ-NOT-002.

**REQ-UI-NOT-004** Unread notifications shall be visually distinguished from read ones.

**REQ-UI-NOT-005** A notification badge shall be displayed on the navigation element linking to this view when unread notifications exist.

---

### 5.5 Watchlist

**REQ-UI-WL-001** Users shall be able to bookmark individual securities independently of any investment thesis.

**REQ-UI-WL-002** The watchlist view shall display each bookmarked security with its ticker, name, and asset type.

**REQ-UI-WL-003** Users shall be able to add and remove securities from the watchlist from the opportunity detail page or directly from the watchlist view.

---

### 5.6 Security Detail View

**REQ-UI-SDL-001** The security detail view shall display the following fields sourced from the market data provider:

- Full legal name of the security
- List of exchanges where the security is tradable
- Security type (e.g., Common Stock, ETF, Index, Commodity)
- Previous close price

**REQ-UI-SDL-002** The detail view shall be dismissible without navigating away from the current page.

**REQ-UI-SDL-003** If market data is unavailable for a given security, the detail view shall display a graceful fallback message rather than an error state.

---

### 5.7 Landing Page

**REQ-UI-LP-001** Unauthenticated visitors shall be presented with a dedicated landing page instead of the application dashboard.

**REQ-UI-LP-002** The landing page shall display a navigation bar with a "Log In" button in the top-right corner that navigates the user to the login view.

**REQ-UI-LP-003** The landing page shall open with a full-width hero section containing:

- The application name ("Chicken Trader")
- The slogan: *"Don't be a chicken, break some eggs!"*

**REQ-UI-LP-004** Below the hero, the landing page shall include a brief prose description of the application's purpose followed by a structured list of key features, covering at minimum:

- AI-driven daily investment opportunity discovery
- News ingestion and event clustering
- Structured investment reports with suggested securities
- Thesis following and lifecycle tracking (Active → Warning → Close Suggested)
- Automated AI reevaluation and user notifications

**REQ-UI-LP-005** The landing page shall conclude with a prominent "Register" call-to-action button that navigates the user to the registration view.

---

## 6. System Architecture

### 6.1 Frontend

| Concern | Technology |
|---|---|
| Framework | Vue.js 3 |
| Build tooling | Vite |
| State management | Pinia |
| Routing | Vue Router |
| Component model | Composition API, component-based architecture |

The frontend communicates with the backend exclusively via a versioned REST API (or GraphQL, to be confirmed during technical design).

---

### 6.2 Backend

| Concern | Technology |
|---|---|
| Runtime | Node.js |
| Framework | Express or NestJS |
| Primary database | PostgreSQL |
| Caching / queuing | Redis |
| Background processing | Job queue (e.g., BullMQ) with background workers |

**Backend responsibilities:**

- Expose authenticated API endpoints to the frontend.
- Run the news ingestion pipeline on a schedule.
- Coordinate AI report generation.
- Persist and update thesis tracking records.
- Run the thesis monitoring loop.
- Trigger AI reevaluation and persist results.
- Dispatch notifications via configured channels.

---

### 6.3 AI Layer

The AI layer is responsible for:

- Summarising news event clusters.
- Evaluating market implications and classifying relevance.
- Generating structured investment reports.
- Identifying relevant securities for each thesis.
- Reevaluating active theses against new monitoring data.

All AI outputs shall be returned as structured JSON. The canonical report JSON schema is:

```json
{
  "event_summary": "string",
  "market_impact": "string",
  "historical_context": "string",
  "suggested_assets": [
    {
      "ticker": "string",
      "name": "string",
      "asset_type": "string",
      "event_relationship": "string",
      "directional_impact": "Long | Short | Neutral",
      "justification": "string"
    }
  ],
  "thesis_conditions": ["string"],
  "risk_factors": ["string"],
  "confidence_score": "Low | Medium | High",
  "time_horizon": "Short-term | Medium-term | Event-driven"
}
```

The reevaluation output schema shall include:

```json
{
  "status": "Active | Warning | Close Suggested",
  "rationale": "string",
  "affected_securities": ["string"],
  "suggested_action": "string"
}
```

---

### 6.4 Data Sources

The following external integrations are required or recommended:

| Category | Purpose | Integration Type |
|---|---|---|
| News APIs | Article ingestion | REST API (e.g., NewsAPI, Bloomberg, Refinitiv) |
| Market data APIs | Price monitoring for thesis tracking | REST API (e.g., Yahoo Finance, Polygon.io, Alpha Vantage) |
| Sector classification data | Tagging events and securities by sector | Reference dataset (e.g., GICS) |

---

## 7. Data Models

### 7.1 Core Entities

| Entity | Key Attributes |
|---|---|
| `User` | id, email, password_hash, notification_preferences, created_at |
| `NewsArticle` | id, source_url, headline, body, published_at, source_provider, event_cluster_id |
| `EventCluster` | id, articles[], relevance_rank, created_at |
| `InvestmentReport` | id, event_cluster_id, headline, fields (see REQ-RPT-002), created_at |
| `ThesisRecord` | id, user_id, report_id, event_id, securities[], follow_timestamp, time_horizon, thesis_conditions, status, status_updated_at |
| `ReevaluationResult` | id, thesis_record_id, status, rationale, affected_securities, suggested_action, evaluated_at |
| `Notification` | id, user_id, thesis_record_id, reevaluation_result_id, read, created_at |
| `WatchlistEntry` | id, user_id, ticker, name, asset_type |

---

### 7.2 AI Report JSON Schema

Defined in Section 6.3.

---

## 8. Non-Functional Requirements

### 8.1 Performance

**REQ-NFR-PERF-001** The Daily Opportunities Dashboard shall load within 2 seconds on a standard broadband connection (≥ 10 Mbps) for up to 20 opportunity cards.

**REQ-NFR-PERF-002** API endpoints shall return responses within 500 ms at the 95th percentile under normal load.

### 8.2 Scalability

**REQ-NFR-SCALE-001** The backend architecture shall support horizontal scaling of stateless services.

**REQ-NFR-SCALE-002** The job queue shall be capable of processing at least 500 events per day without performance degradation.

### 8.3 Availability

**REQ-NFR-AVAIL-001** The application shall target 99.5% uptime, excluding scheduled maintenance windows.

### 8.4 Security

**REQ-NFR-SEC-001** All API endpoints that access user data shall require authentication (e.g., JWT or session-based).

**REQ-NFR-SEC-002** All data in transit shall be encrypted using TLS 1.2 or higher.

**REQ-NFR-SEC-003** User passwords shall be stored as salted hashes using a current best-practice algorithm (e.g., bcrypt or Argon2).

**REQ-NFR-SEC-004** AI API keys and data source credentials shall be stored in environment variables or a secrets manager, never in source control.

### 8.5 Traceability

**REQ-NFR-TRACE-001** Every AI-generated investment report shall include visible references to the source articles from which it was derived.

**REQ-NFR-TRACE-002** All AI-generated content shall be clearly labelled as such in the user interface.

### 8.6 Maintainability

**REQ-NFR-MAINT-001** The system shall use a modular architecture that allows the AI provider and news source integrations to be updated or replaced independently.

**REQ-NFR-MAINT-002** AI prompts shall be stored in a configurable location (e.g., a database table or dedicated configuration file) to allow updates without a code deployment.

---

## 9. Compliance and Legal Requirements

**REQ-COMP-001** The application shall display a persistent disclaimer on all pages containing AI-generated investment content. The disclaimer shall state, at minimum:

> "The content on this platform is generated by artificial intelligence and is provided for informational purposes only. It does not constitute financial advice. You are solely responsible for your own investment decisions."

**REQ-COMP-002** The disclaimer shall be readable without user interaction (i.e., not hidden behind a modal or requiring scroll).

**REQ-COMP-003** The platform shall not represent AI-generated insights as the opinion or advice of a licensed financial adviser.

**REQ-COMP-004** The system shall comply with applicable data protection regulations (e.g., GDPR for EU/EEA users) with respect to storage and processing of personal data.

**REQ-COMP-005** The platform shall respect the terms of service of all integrated news and market data APIs, including any restrictions on data redistribution or display.

---

## 10. Out of Scope

The following items are explicitly excluded from version 1.0:

- Direct brokerage integration for order execution.
- Real-time streaming market data.
- Portfolio tracking or position management.
- Social or community features (sharing, comments, following other users).
- Mobile native applications (iOS / Android).
- Multi-language or localisation support.
- Backtesting of AI-generated theses against historical data.

---

## 11. Glossary

| Term | Definition |
|---|---|
| AI Confidence Indicator | A qualitative or numeric rating produced by the AI indicating its confidence in a given investment thesis. |
| Event Cluster | A group of news articles determined by the system to relate to the same underlying market event. |
| Follow | A user action that registers a thesis for ongoing monitoring and notification. |
| Unfollow | A user action that permanently removes a thesis tracking record from the user's followed ideas list. |
| Opportunity | A news-driven market event for which the system has generated an investment report. |
| Reevaluation | The process by which the AI reassesses whether an active thesis remains valid, triggered periodically by the monitoring loop. |
| Thesis | The structured AI investment argument associated with a specific event, including suggested securities, conditions, and risk factors. |
| Thesis Conditions | A set of logical conditions defined at report generation time that, when met or contradicted, indicate the thesis status should change. |
| Time Horizon | The expected duration over which a thesis investment idea is relevant: Short-term (days to weeks), Medium-term (weeks to months), or Event-driven (until a specific event outcome). |
