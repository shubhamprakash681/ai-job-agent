# PROJECT: AI Job Search & Application Agent for India

## 0. ROLE

You are a principal software architect, senior full-stack engineer, AI engineer, DevOps engineer, security engineer, QA engineer, and product engineer.

Your job is to design and IMPLEMENT a production-grade personal AI job-search and application platform from scratch.

Do not merely provide architecture diagrams, pseudocode, TODOs, mock implementations, or explanations.

You must progressively CREATE THE ACTUAL WORKING SOFTWARE.

The final product should be runnable locally, deployable to a personal server/VM, testable, observable, secure, and maintainable.

The system is intended for ONE USER initially: the candidate described below.

The system must prioritize:

1. India job market
2. Java + Spring Boot + React full-stack positions
3. Bangalore
4. Hyderabad
5. Pune
6. Mumbai
7. Remote India
8. Adjacent Java backend/microservices roles

LinkedIn scraping MUST NOT be implemented.

Do not bypass CAPTCHAs, anti-bot systems, authentication controls, robots restrictions, rate limits, or website protections.

Where a source does not provide a legitimate automation mechanism, implement a safe/manual fallback rather than trying to circumvent restrictions.

---

# 1. CANDIDATE PROFILE

The candidate is:

Name:
Shubham Prakash

Current location:
Mumbai, India

Portfolio:
https://shubhamprakash681.in/

Primary target:
Java + React Full Stack Developer / Software Engineer

Experience:
3 years + 3 months

Current employer:
Accenture

Current role:
Packaged App Development Analyst

Current employment:
April 2026 – Present

Previous employer:
Tata Consultancy Services (TCS Digital)

Previous role:
Software Developer

June 2023 – April 2026

Previous internship:
Sylvr — Software Engineer Intern
March 2023 – June 2023

Education:
B.Tech Electronics and Communication Engineering
Cochin University of Science and Technology
CGPA: 8.91/10

Primary technical profile:

Backend:

* Java
* Spring Boot
* Spring MVC
* Spring Security
* Spring Cloud
* Microservices
* REST APIs
* Node.js

Frontend:

* React
* Next.js
* TypeScript
* JavaScript
* HTML
* CSS

Distributed systems:

* Kafka
* RabbitMQ
* Redis
* WebSockets
* API Gateway
* Eureka

Databases:

* PostgreSQL
* MongoDB
* JPA
* Hibernate
* Prisma
* Mongoose

Cloud / DevOps:

* Docker
* AWS EC2
* Nginx
* Linux
* CI/CD
* Git
* Postman

Security:

* JWT
* OAuth2
* Auth0
* RBAC

Computer science:

* System Design
* HLD
* LLD
* DSA
* OOP

Important demonstrated experience:

* Enterprise applications using Java, Spring Boot Microservices, React, TypeScript and Node.js
* ArcGIS authentication migration from frontend to backend
* JWT / OAuth2 / Auth0 SSO
* Authentication across 3 enterprise applications
* Spring Cloud Eureka
* Spring Cloud Gateway
* Caching
* Data structures
* Session management
* 10,000+ concurrent users
* Up to 80% faster load times
* Real-time Chart.js dashboards
* Up to 90% engagement improvement

Project:

TradeX

Realtime paper-trading platform.

Technologies include:

* Spring Boot microservices
* API Gateway
* Eureka Service Discovery
* Authentication
* Market service
* Portfolio service
* Kafka
* WebSockets
* Redis
* PostgreSQL
* Indian stocks/ETFs
* 10 years of OHLCV data

Project:

VideoShare

Video-sharing platform.

Technologies include:

* REST APIs
* Authentication
* Video streaming
* Likes
* Comments
* Subscriptions
* Playlists
* MongoDB Atlas
* Fuzzy search
* NSFW classification pipeline
* Docker
* AWS EC2
* Nginx

Additional project/portfolio information may be obtained from:

https://shubhamprakash681.in/

But NEVER invent information that is not supported by the resume or verified portfolio.

The uploaded resume is the primary factual source.

---

# 2. CORE PRODUCT OBJECTIVE

Build a personal AI-powered system that performs:

JOB DISCOVERY
↓
JOB INGESTION
↓
NORMALIZATION
↓
DEDUPLICATION
↓
JOB QUALITY CHECK
↓
CANDIDATE MATCHING
↓
JOB SCORING
↓
JOB RANKING
↓
JD ANALYSIS
↓
RESUME TAILORING
↓
RESUME VALIDATION
↓
COVER LETTER GENERATION
↓
APPLICATION QUESTION PREPARATION
↓
APPLICATION FORM FILLING
↓
HUMAN REVIEW
↓
APPLICATION SUBMISSION
↓
APPLICATION TRACKING
↓
FOLLOW-UP
↓
ANALYTICS

The system should become a personal "job operating system" rather than merely a scraper.

---

# 3. VERY IMPORTANT: ZERO EXTRA SPEND

The user already has:

* Gemini Pro subscription
* access to Gemini ecosystem
* access to Groq
* access to other free AI tools

The system must NOT require paid APIs or paid SaaS.

Do not assume that a Gemini consumer subscription automatically gives unlimited Gemini API access.

Architect the system so that API access is configurable.

Possible AI providers:

1. Gemini
2. Groq
3. Local/open-source models
4. Other compatible providers

The AI layer must use a provider abstraction:

LLMProvider
├── GeminiProvider
├── GroqProvider
├── LocalProvider
└── MockProvider

Never hard-code the application to one model.

---

# 4. RECOMMENDED AI MODEL STRATEGY

Do NOT use an expensive/large model for every operation.

Use deterministic code whenever possible.

### Tier 0 — Deterministic code

Use normal code for:

* URL normalization
* deduplication
* date parsing
* location normalization
* experience calculations
* skill synonym matching
* job status
* application status
* file naming
* resume versioning
* database operations
* validation
* required-field checking
* application tracking
* scheduling
* rate limiting
* retries
* security
* audit logs

Never waste LLM calls on these.

---

### Tier 1 — Fast/cheap/free LLM

Use Groq or another free model for:

* JD extraction
* skill extraction
* classification
* basic summarization
* duplicate semantic comparison
* job categorization
* initial job scoring
* application question classification

---

### Tier 2 — High-quality reasoning

Use Gemini for:

* final JD analysis
* difficult job matching
* resume tailoring
* cover letters
* application-answer drafting
* final resume QA
* hallucination detection
* semantic comparison

---

### Tier 3 — Human

Require human confirmation for:

* final application submission
* salary answers
* notice period
* relocation
* work authorization
* demographic questions
* legal declarations
* ambiguous questions
* CAPTCHA
* assessments
* anything the system cannot confidently answer

---

# 5. NON-NEGOTIABLE ANTI-HALLUCINATION RULE

The agent must NEVER invent:

* employment
* employer
* job title
* years of experience
* technology
* certification
* degree
* project
* responsibility
* achievement
* metric
* salary
* notice period
* location
* visa/work authorization
* production experience
* client
* company
* team size

The master candidate profile is immutable factual data.

AI may:

* reorder information
* shorten information
* emphasize information
* rewrite wording
* select relevant bullets
* use terminology from a JD when it truthfully maps to an existing skill

AI may NOT manufacture evidence.

Every generated resume must be traceable back to candidate facts.

---

# 6. MASTER CANDIDATE KNOWLEDGE BASE

Create:

/candidate/

candidate.yaml

resume-master.docx
resume-master.pdf
resume-master.md

achievements.yaml

projects.yaml

experience.yaml

skills.yaml

preferences.yaml

application-profile.yaml

portfolio-snapshot.json

candidate-facts.json

candidate-evidence.json

The candidate knowledge base should contain atomic factual claims.

Example:

{
"id": "experience.tcs.auth.001",
"claim": "Implemented JWT, OAuth2 and Auth0 SSO across 3 enterprise applications",
"source": "resume",
"verified": true,
"allowed_for_resume": true,
"allowed_for_application": true
}

Every resume bullet should reference one or more evidence IDs.

---

# 7. RESUME VARIANTS

The system must support four primary resume strategies.

## Variant A — Java + React Full Stack

Priority:

Java
Spring Boot
Microservices
REST
React
TypeScript
Spring Security
Spring Cloud
Kafka
Redis
PostgreSQL
Docker

Use this as the DEFAULT.

---

## Variant B — Java Backend / Spring Boot

Prioritize:

Java
Spring Boot
Spring Security
Spring Cloud
Microservices
REST APIs
Kafka
Redis
PostgreSQL
JPA/Hibernate
Distributed systems
System design

Reduce frontend emphasis but do not remove React entirely.

---

## Variant C — Full Stack Engineer

Prioritize:

Java
Spring Boot
React
TypeScript
Node.js
REST APIs
PostgreSQL
MongoDB
Docker
AWS
authentication
distributed systems

---

## Variant D — Backend / Distributed Systems

Prioritize:

Java
Spring Boot
Microservices
Kafka
Redis
RabbitMQ
WebSockets
Spring Cloud
API Gateway
Eureka
PostgreSQL
distributed systems
system design

---

# 8. RESUME TAILORING ENGINE

Input:

* Master resume
* Candidate evidence database
* Job description
* Job requirements
* Target role

Output:

1. Tailored resume
2. Resume JSON
3. Keyword mapping
4. Evidence mapping
5. Change diff
6. Confidence score
7. Unsupported claims
8. Missing skills
9. ATS compatibility report

Example:

{
"job_id": "...",
"variant": "java-react-fullstack",
"matched_keywords": [],
"missing_keywords": [],
"emphasized_evidence": [],
"changed_sections": [],
"unsupported_claims": [],
"confidence": 0.94
}

If unsupported_claims is not empty:

DO NOT allow automatic submission.

---

# 9. ATS RESUME RULES

Generated resumes must:

* remain one page where practical
* use standard section headings
* avoid tables where they harm ATS parsing
* avoid excessive graphics
* avoid icons as semantic substitutes
* avoid text embedded in images
* use standard fonts
* use consistent dates
* maintain readable hierarchy
* preserve factual content
* use JD terminology where truthful
* avoid keyword stuffing

Generate both:

PDF
DOCX

Store source:

Markdown/JSON → DOCX → PDF

Never make PDF the canonical source.

---

# 10. JOB SOURCE STRATEGY

DO NOT SCRAPE LINKEDIN.

Primary India sources:

1. Naukri
2. Indeed India
3. Foundit
4. Cutshort
5. Instahyre
6. Hirist
7. TimesJobs
8. Shine
9. Wellfound
10. iimjobs when technically relevant
11. Company career pages
12. Greenhouse
13. Lever
14. Workday
15. SmartRecruiters
16. Ashby
17. other legitimate ATS platforms

Prioritize:

* official APIs
* RSS
* email alerts
* public search endpoints
* official ATS interfaces
* structured job feeds
* search-engine indexed pages
* browser-assisted workflows where permitted

Do NOT attempt to bypass:

* CAPTCHA
* login restrictions
* anti-bot controls
* rate limits
* robots restrictions
* authentication
* access controls

If automation isn't appropriate:

source → manual review queue

---

# 11. JOB SOURCE ADAPTER ARCHITECTURE

Create:

src/job_sources/

base.py

naukri.py
indeed.py
foundit.py
cutshort.py
instahyre.py
hirist.py
timesjobs.py
shine.py
wellfound.py

ats/

greenhouse.py
lever.py
workday.py
smartrecruiters.py
ashby.py

company/

generic_company_page.py

Each adapter must implement:

discover_jobs()
fetch_job()
normalize_job()
get_application_url()
get_source_metadata()

Each adapter must declare:

automation_level:

* API
* FEED
* PUBLIC_PAGE
* BROWSER_ASSISTED
* MANUAL

risk_level:

* LOW
* MEDIUM
* HIGH

enabled:
true/false

The system must allow disabling any source through configuration.

---

# 12. INDIA-SPECIFIC SEARCH QUERIES

Create a configurable search matrix.

### Bangalore

Java Spring Boot React
Java React Full Stack
Java Spring Boot Microservices
Full Stack Java React
Java Backend Microservices
Software Engineer Java
Backend Engineer Java

### Hyderabad

Same matrix.

### Pune

Same matrix.

### Mumbai

Same matrix.

### Remote India

Same matrix.

Also generate variations:

Java 17
Java 21
Spring Boot
Spring Cloud
Microservices
Kafka
React TypeScript
Full Stack Engineer
Software Engineer
Backend Engineer
SDE
SDE-1
SDE-2

Do not blindly search every keyword combination.

Use an adaptive search strategy based on observed job yield.

---

# 13. JOB NORMALIZATION

Create canonical Job schema:

{
"id": "...",
"source": "...",
"source_job_id": "...",
"url": "...",
"canonical_url": "...",
"title": "...",
"company": "...",
"locations": [],
"remote": false,
"experience_min": null,
"experience_max": null,
"employment_type": "...",
"salary_min": null,
"salary_max": null,
"currency": "INR",
"description": "...",
"skills": [],
"required_skills": [],
"preferred_skills": [],
"posted_at": null,
"deadline": null,
"application_url": "...",
"source_type": "...",
"raw_content_hash": "...",
"created_at": "...",
"updated_at": "..."
}

---

# 14. JOB DEDUPLICATION

The same job may appear on:

Naukri
Indeed
Google
company website
Cutshort

Create multi-level deduplication:

Level 1:
canonical URL

Level 2:
source job ID

Level 3:
company + normalized title + location

Level 4:
description similarity

Level 5:
LLM semantic duplicate check

Prefer the original company ATS application URL.

---

# 15. CANDIDATE JOB SCORING

Create deterministic scoring first.

Suggested maximum:

100 points.

### Role relevance — 25

Java + React full stack:
25

Java backend:
22

Spring Boot backend:
20

React frontend:
12

Node backend:
10

Unrelated:
0

---

### Core skills — 25

Java
Spring Boot
Spring Security
Spring Cloud
Microservices
REST
React
TypeScript

Weight each based on importance.

---

### Distributed systems — 15

Kafka
Redis
RabbitMQ
WebSockets
API Gateway
Eureka

---

### Experience fit — 15

Ideal:

2.5–5 years

Strong penalty for:

8+ years

Lead
Principal
Staff
Architect

unless explicitly considered.

---

### Location — 10

Bangalore:
10

Hyderabad:
10

Pune:
10

Mumbai:
8

Remote India:
8

Other India:
4

Outside India:
0

---

### Job quality — 10

Recent
clear JD
known company
direct ATS
salary available
clear responsibilities

---

# 16. HARD FILTERS

Reject automatically if:

* unrelated technology
* primarily .NET
* Python-only
* frontend-only when backend is required
* senior/staff/principal requiring substantially more experience
* location incompatible
* internship
* unpaid
* suspicious job
* missing company information
* duplicate application
* closed position
* obvious recruitment scam

---

# 17. LLM MATCHING

LLM should NOT replace deterministic scoring.

It should supplement it.

Output:

{
"overall_score": 87,
"fit": "STRONG",
"strengths": [],
"gaps": [],
"risks": [],
"reasoning": [],
"recommended_resume_variant": "java-react-fullstack"
}

Categories:

90–100:
AUTO-PREPARE

80–89:
HIGH PRIORITY

70–79:
GOOD

60–69:
OPTIONAL

<60:
IGNORE

However:

AUTO-PREPARE does NOT mean auto-submit.

---

# 18. APPLICATION AUTOMATION

Application levels:

LEVEL 0:
Discovery only

LEVEL 1:
Prepare application

LEVEL 2:
Open browser and prefill

LEVEL 3:
Prefill + human confirmation

LEVEL 4:
Fully automated submission

Default:

LEVEL 3

The user must approve before final submission.

---

# 19. NEVER AUTOMATICALLY ANSWER THESE WITHOUT VERIFIED DATA

* Current CTC
* Expected CTC
* Notice period
* Current employment status
* Work authorization
* Visa
* Sponsorship
* Relocation
* Willingness to travel
* Gender
* Disability
* veteran status
* demographic questions
* legal declarations
* criminal/background questions
* certifications
* years of experience in a specific technology

The system should retrieve these from:

candidate/application-profile.yaml

If unavailable:

ASK USER.

---

# 20. APPLICATION PROFILE

Create:

application-profile.yaml

Example:

personal:
name:
email:
phone:
location:

professional:
current_company:
current_role:
total_experience:
notice_period:
current_ctc:
expected_ctc:

preferences:
cities:
remote:
target_roles:
minimum_score:

The system must NEVER guess these values.

---

# 21. PLAYWRIGHT

Use Playwright rather than Selenium unless there is a specific reason.

Create:

src/browser/

browser_manager.py

session_manager.py

form_detector.py

form_filler.py

application_detector.py

captcha_detector.py

confirmation_detector.py

screenshot_manager.py

Each application session must:

1. create isolated context
2. open application URL
3. detect page
4. identify fields
5. map fields to candidate data
6. fill safe fields
7. flag uncertain fields
8. upload tailored resume
9. prepare answers
10. pause before final submission
11. capture screenshot
12. wait for user confirmation
13. submit
14. verify confirmation
15. store result

---

# 22. CAPTCHA

If CAPTCHA is detected:

STOP.

Do not solve automatically.

Set:

application_status = CAPTCHA_REQUIRED

Notify user.

---

# 23. APPLICATION QUESTION ENGINE

Create:

Question
AnswerStrategy
Confidence
Evidence
RequiresHuman

Example:

Question:
"How many years of Java experience do you have?"

Answer:
Derived deterministically from employment dates and candidate evidence.

Question:
"Do you have experience with Kubernetes?"

If no evidence:

DO NOT answer "Yes."

Answer:
"No verified experience in candidate knowledge base."

The UI should show:

QUESTION
PROPOSED ANSWER
SOURCE
CONFIDENCE
APPROVE / EDIT / REJECT

---

# 24. APPLICATION TRACKING

Statuses:

DISCOVERED
SHORTLISTED
ANALYZING
RESUME_READY
READY_TO_APPLY
AWAITING_APPROVAL
APPLYING
APPLIED
FAILED
CAPTCHA_REQUIRED
MANUAL_REQUIRED
REJECTED
INTERVIEW
OFFER
WITHDRAWN

Store:

timestamps
resume version
cover letter version
application URL
source
job score
questions
answers
submission evidence
screenshots
notes

---

# 25. DATABASE

Use PostgreSQL as production database.

Use SQLite for local development if helpful.

Recommended:

PostgreSQL
SQLAlchemy
Alembic

Tables:

users
candidate_profiles
candidate_facts
candidate_evidence
experience
education
projects
skills
job_sources
jobs
job_requirements
job_scores
resume_variants
resume_versions
resume_evidence
cover_letters
applications
application_questions
application_answers
application_events
browser_sessions
notifications
audit_logs
llm_requests
llm_responses

Every major operation must have an audit record.

---

# 26. BACKEND

Recommended stack:

Python
FastAPI
Pydantic
SQLAlchemy
Alembic
PostgreSQL

Why Python:

* AI ecosystem
* browser automation
* document processing
* PDF/DOCX
* data processing
* scheduling
* easy LLM integration

Use async where appropriate.

---

# 27. FRONTEND

Use:

Next.js
TypeScript
React
Tailwind CSS

Dashboard pages:

/dashboard

/jobs

/jobs/:id

/applications

/applications/:id

/resumes

/resumes/:id

/candidate

/sources

/settings

/analytics

/review

/automation

---

# 28. MAIN DASHBOARD

Display:

Jobs discovered today
New relevant jobs
High-priority jobs
Applications pending approval
Applications submitted
Interview rate
Response rate
Top companies
Top cities
Top skills requested
Resume variants generated
Failed applications

---

# 29. JOB CARD

Each job should show:

Company
Role
Location
Experience
Salary
Source
Posted date
Match score
Skill match
Missing skills
Resume variant
Application method

Buttons:

VIEW
ANALYZE
GENERATE RESUME
GENERATE COVER LETTER
PREPARE APPLICATION
OPEN APPLICATION
APPLY
SKIP

---

# 30. RESUME REVIEW UI

Show:

Original
Tailored

side by side.

Highlight:

ADDED
REMOVED
REORDERED
REWRITTEN

For every changed bullet show:

Evidence ID

Example:

Changed:
"Developed scalable microservices..."

Evidence:
experience.tcs.microservices.001

This is critical.

---

# 31. COVER LETTER ENGINE

Generate short, targeted letters.

Never produce generic:

"I am excited to apply..."

Use:

* role
* company
* relevant experience
* 1–2 specific matching achievements
* concise closing

Maximum approximately 250–350 words unless configured otherwise.

---

# 32. AI PROMPT ENGINE

Do not scatter prompts throughout the source code.

Create:

prompts/

job_extract.yaml
job_match.yaml
resume_tailor.yaml
resume_validate.yaml
cover_letter.yaml
application_question.yaml
application_qa.yaml

Prompts must be versioned.

Example:

resume_tailor_v1

resume_tailor_v2

Store prompt version with every LLM output.

---

# 33. STRUCTURED OUTPUT

Every LLM request should preferably use JSON schema / structured output.

Never parse fragile natural-language responses if structured output is possible.

Example:

{
"matched_skills": [],
"missing_skills": [],
"evidence_ids": [],
"recommended_changes": [],
"risk_flags": []
}

Validate all LLM responses with Pydantic.

If invalid:

retry once.

If still invalid:

fail safely.

---

# 34. LLM ROUTER

Create:

LLMRouter

Methods:

extract()
classify()
rank()
reason()
generate_resume()
generate_cover_letter()
answer_application_question()
validate()

Example routing:

extract → Groq

classify → Groq

initial_match → Groq

complex_match → Gemini

resume_generation → Gemini

resume_validation → Gemini

cover_letter → Groq or Gemini

final QA → Gemini

The router must support fallback.

Example:

Gemini failure
→ Groq

Groq failure
→ local model

If no provider available:

continue without AI where possible.

---

# 35. GEMINI

Create a configurable Gemini provider.

Do not assume consumer Gemini subscription equals API entitlement.

Configuration:

GEMINI_API_KEY
GEMINI_MODEL
GEMINI_ENABLED

The UI should display:

Provider
Model
Status
Quota/error state

Never hard-code a model name.

---

# 36. GROQ

Create:

GROQ_API_KEY
GROQ_MODEL

Support model configuration.

Do not hard-code assumptions about free-tier limits.

When rate-limited:

exponential backoff.

---

# 37. LOCAL MODEL FALLBACK

Make the architecture compatible with:

Ollama

or another local OpenAI-compatible server.

Example:

LOCAL_LLM_BASE_URL
LOCAL_LLM_MODEL

This makes the system usable even when cloud free tiers are exhausted.

---

# 38. DOCUMENT GENERATION

Canonical format:

JSON / Markdown

Generate:

DOCX
PDF

Libraries:

python-docx
ReportLab or HTML-to-PDF pipeline

The generated resume must be visually checked.

Create automated checks:

* page count
* missing sections
* overflow
* empty bullets
* broken characters
* excessive whitespace
* contact information
* dates
* filename

---

# 39. EMAIL APPLICATION

Use Gmail API if enabled.

Do NOT store Gmail passwords.

Use OAuth.

Support:

draft email

send after approval

attachment

resume

cover letter

application tracking

Never send bulk spam.

---

# 40. NOTIFICATIONS

Start with email notifications.

Optional:

Telegram

Discord

Slack

Do not make these mandatory.

Notifications:

New high-score job
Resume ready
Application requires approval
CAPTCHA
Application failure
Interview follow-up
Daily summary

---

# 41. SCHEDULER

Use:

APScheduler

or cron.

Tasks:

job discovery
job refresh
resume generation
application follow-up
daily report

Default:

Discovery:
2–4 times/day

Resume generation:
on demand

Application:
human-triggered

Follow-up:
daily

Do not aggressively poll websites.

---

# 42. DAILY WORKFLOW

Example:

08:00

Discover jobs.

Normalize.

Deduplicate.

Filter.

Score.

↓

09:00

Generate candidate shortlist.

↓

User opens dashboard.

↓

Selects jobs.

↓

AI generates tailored resume.

↓

AI validates resume.

↓

User reviews.

↓

Application prepared.

↓

Browser opens.

↓

Fields filled.

↓

User confirms.

↓

Submit.

↓

Application recorded.

---

# 43. APPLICATION LIMITS

Do NOT create a "mass apply" feature.

Create:

daily_application_limit

default = 10

Allow configuration.

Before applying:

check duplicate.

check job still active.

check candidate fit.

check resume generated.

check application hasn't already been submitted.

check user approval.

---

# 44. QUALITY OVER QUANTITY

The objective is NOT:

100 applications/day.

The objective is:

10–20 highly relevant applications/week/day depending on user preference.

Optimize for:

relevance
resume quality
application correctness
company quality
response probability

---

# 45. JOB FRAUD DETECTION

Create a basic fraud-risk engine.

Signals:

* suspicious domain
* generic email
* unrealistic salary
* payment request
* crypto/payment requirement
* WhatsApp-only recruiting
* missing company
* suspicious application URL
* duplicate job
* copied description
* request for sensitive information

Flag rather than automatically apply.

---

# 46. SECURITY

Secrets must NEVER be committed.

Use:

.env

.env.example

GitHub Secrets

or secure local secret store.

Never log:

API keys
OAuth tokens
passwords
full resume
private candidate data

Encrypt sensitive application data where practical.

---

# 47. AUDITABILITY

Every important action must be recorded.

Example:

2026-09-20 10:30
JOB_DISCOVERED

2026-09-20 10:31
JOB_SCORED

2026-09-20 10:32
RESUME_GENERATED

2026-09-20 10:33
RESUME_VALIDATED

2026-09-20 10:35
USER_APPROVED

2026-09-20 10:36
APPLICATION_SUBMITTED

This should make debugging possible.

---

# 48. OBSERVABILITY

Use structured logs.

Include:

request_id
job_id
application_id
provider
model
duration
status
error

Do not expose sensitive candidate data.

---

# 49. ERROR HANDLING

Every external operation must support:

timeout
retry
exponential backoff
circuit breaker where appropriate
structured error
dead-letter/manual queue

Never allow one failed job source to stop the entire system.

---

# 50. TESTING

Write real tests.

Unit tests:

job parser
normalizer
deduplicator
scoring
resume validation
candidate evidence
application question engine

Integration tests:

database
LLM providers
job adapters

Browser tests:

Use mock/demo forms.

Do NOT test automation against sites in a way that violates their restrictions.

Create local test pages representing:

Greenhouse-like form
Lever-like form
Workday-like form
generic application form

---

# 51. TEST DATA

Create:

tests/fixtures/

candidate.json
jobs/
java-react-1.json
java-backend-1.json
react-only.json
python-only.json
senior-java.json

applications/

greenhouse.html
lever.html
generic.html
captcha.html

---

# 52. DRY RUN MODE

This is mandatory.

Configuration:

DRY_RUN=true

When enabled:

* no applications submitted
* no emails sent
* no irreversible actions
* screenshots still captured
* generated resumes still produced
* forms still filled
* final action simulated

---

# 53. HUMAN APPROVAL MODE

Mandatory default:

HUMAN_APPROVAL_REQUIRED=true

Before submission show:

Company
Role
Job URL
Match score
Resume
Cover letter
Application answers
Missing information
Risk flags

Buttons:

APPROVE
EDIT
REJECT

Only APPROVE allows submission.

---

# 54. PRODUCTION MODE

Production configuration:

ENVIRONMENT=production

DRY_RUN=false

HUMAN_APPROVAL_REQUIRED=true

Never allow:

AUTO_SUBMIT=true

unless explicitly enabled by the user.

Even then, only low-risk forms with complete verified answers should qualify.

---

# 55. DOCKER

Create:

Dockerfile

docker-compose.yml

Services:

frontend
backend
postgres
redis

Optional:

worker

browser

Use Redis for:

queues
locks
caching

---

# 56. BACKGROUND JOBS

Use Celery/RQ/Arq or another appropriate Python task queue.

Queues:

job_discovery
job_processing
llm
resume_generation
browser_tasks
notifications

Prevent duplicate processing using distributed locks.

---

# 57. API DESIGN

REST API.

Examples:

GET /api/jobs

GET /api/jobs/{id}

POST /api/jobs/{id}/analyze

POST /api/jobs/{id}/tailor-resume

POST /api/jobs/{id}/prepare-application

POST /api/applications/{id}/approve

POST /api/applications/{id}/submit

GET /api/applications

GET /api/resumes

GET /api/candidate

GET /api/analytics

---

# 58. UI AUTHENTICATION

Because this is initially a single-user application:

Implement secure local authentication.

Do not expose the dashboard publicly without authentication.

If deployed behind a reverse proxy:

HTTPS required.

---

# 59. REPOSITORY STRUCTURE

Use:

job-agent/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── llm/
│   │   ├── job_sources/
│   │   ├── ats/
│   │   ├── browser/
│   │   ├── resume/
│   │   ├── applications/
│   │   ├── scoring/
│   │   ├── notifications/
│   │   └── workers/
│   └── tests/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   └── types/
│
├── candidate/
│
├── prompts/
│
├── documents/
│
├── scripts/
│
├── docker/
│
├── docs/
│
├── .github/
│   └── workflows/
│
├── docker-compose.yml
├── .env.example
├── README.md
└── GEMINI.md

---

# 60. GEMINI.md

Create a detailed GEMINI.md containing:

* project architecture
* coding conventions
* candidate facts
* forbidden assumptions
* AI provider strategy
* testing rules
* security rules
* job source rules
* application safety rules
* deployment instructions

Any coding agent reading the repository must understand the project without requiring this original prompt.

---

# 61. DEVELOPMENT PHASES

Do NOT attempt to build everything at once.

Build incrementally.

## PHASE 1

Foundation.

Implement:

repository
backend
frontend
database
Docker
configuration
candidate profile
authentication

Everything must run.

---

## PHASE 2

Candidate knowledge base.

Implement:

candidate facts
experience
skills
projects
evidence system

Import the actual resume.

Add portfolio verification.

Build immutable factual profile.

---

## PHASE 3

Job ingestion.

Implement:

one source first.

Then:

ATS/company sources.

Then additional sources.

Do not create 10 broken adapters simultaneously.

---

## PHASE 4

Job normalization.

Implement:

deduplication
classification
location parsing
experience parsing
skill extraction

---

## PHASE 5

Job scoring.

Implement deterministic score.

Then LLM enhancement.

---

## PHASE 6

Resume engine.

Implement:

master resume
four variants
tailoring
evidence mapping
diff
DOCX
PDF
validation

---

## PHASE 7

Application preparation.

Implement:

application profile
question engine
answer confidence
browser form detection
resume upload

---

## PHASE 8

Human approval.

Implement review UI.

No automatic submission yet.

---

## PHASE 9

Application submission.

Implement only after the previous phases are stable.

Start with:

safe generic forms
supported ATS forms

Then add additional adapters.

---

## PHASE 10

Analytics.

Implement:

application funnel
response rate
company performance
role performance
resume variant performance
city performance

---

# 62. FIRST MVP

The MVP should NOT attempt every website.

MVP should support:

1. Candidate profile
2. Resume ingestion
3. Job ingestion from a few legitimate sources
4. Job normalization
5. Deduplication
6. Java/React matching
7. Job scoring
8. Gemini/Groq integration
9. Tailored resume
10. Cover letter
11. Application preparation
12. Human approval
13. Application tracking
14. Dashboard
15. Docker deployment

Only after this works should more job sources be added.

---

# 63. DEFINITION OF DONE

The product is NOT finished because:

"the code compiles."

It is finished when:

* Docker starts successfully
* database migrations work
* frontend works
* backend works
* candidate profile loads
* jobs can be ingested
* jobs are deduplicated
* jobs are scored
* JD analysis works
* resume tailoring works
* generated resume is valid
* evidence mapping works
* cover letter works
* application questions are handled safely
* browser workflow works in dry-run mode
* human approval works
* application tracking works
* audit logs work
* tests pass
* error handling works
* documentation exists
* .env.example exists
* no secrets are committed

---

# 64. IMPORTANT: DO NOT FAKE COMPLETION

Never say:

"implemented"

when you only created a stub.

Never create:

pass
TODO
NotImplementedError

for core features unless explicitly marking a future extension.

If a feature cannot yet be implemented, clearly mark it:

MANUAL_FALLBACK

and provide a working fallback.

---

# 65. CODE QUALITY

Follow:

SOLID
DRY
KISS
12-factor principles where appropriate

Prefer:

small modules
dependency injection
interfaces
typed schemas
structured errors
testable services

Avoid:

giant files
global state
hard-coded credentials
hard-coded URLs
hard-coded selectors
LLM-dependent business logic
magic numbers

---

# 66. SOURCE ADAPTER DESIGN

Every source adapter must be independently testable.

Example:

class JobSource(ABC):

```
@abstractmethod
async def discover(self, query):
    pass

@abstractmethod
async def fetch(self, job):
    pass

@abstractmethod
def normalize(self, raw):
    pass
```

Do not assume all sources behave identically.

---

# 67. BROWSER AUTOMATION DESIGN

Never rely exclusively on CSS selectors.

Use hierarchy:

1. label
2. aria-label
3. name
4. id
5. placeholder
6. semantic relationship
7. CSS/XPath as last resort

Selectors must be configurable.

Do not hard-code one site's entire DOM structure into business logic.

---

# 68. APPLICATION FORM INTELLIGENCE

Create a generic field ontology:

FIRST_NAME
LAST_NAME
EMAIL
PHONE
LOCATION
RESUME
COVER_LETTER
CURRENT_COMPANY
CURRENT_TITLE
YEARS_EXPERIENCE
NOTICE_PERIOD
CURRENT_CTC
EXPECTED_CTC
LOCATION_PREFERENCE
RELOCATION
WORK_AUTHORIZATION
SPONSORSHIP
LINKEDIN
GITHUB
PORTFOLIO
SKILL
EDUCATION
CERTIFICATION
CUSTOM

Map form fields to ontology.

Unknown fields:

send to human review.

---

# 69. RESUME FACT VALIDATION

Before any application:

Run:

Candidate Evidence Validator

Checks:

Every resume statement has evidence.

No new employer.

No new technology.

No new metric.

No changed dates.

No changed title.

No changed degree.

No unsupported claim.

If failure:

BLOCK APPLICATION.

---

# 70. JOB DESCRIPTION PROMPT

Create a structured prompt like:

"You are a job-description extraction engine.

Extract ONLY information explicitly present in the job description.

Do not infer candidate suitability.

Return JSON containing:

title
company
location
experience
required_skills
preferred_skills
responsibilities
education
salary
employment_type
work_mode
application_method
red_flags

Do not hallucinate missing values."

---

# 71. MATCHING PROMPT

Use:

candidate evidence
job requirements
deterministic score

Ask:

Which requirements are directly supported?

Which are partially supported?

Which are unsupported?

Which are missing?

Which candidate evidence is strongest?

Never turn "preferred" into "required."

---

# 72. RESUME PROMPT

Use:

MASTER RESUME
CANDIDATE EVIDENCE
JOB DESCRIPTION
JOB SCORE
TARGET VARIANT

Instructions:

Tailor without inventing.

Preserve dates.

Preserve employers.

Preserve titles.

Preserve metrics.

Select relevant evidence.

Use exact job terminology only when supported.

Return structured JSON.

---

# 73. FINAL RESUME QA PROMPT

"You are a strict resume fact checker.

Compare the generated resume against the immutable candidate evidence.

Find:

unsupported claims
changed dates
changed metrics
new skills
new employers
new responsibilities
misleading wording
keyword stuffing

If any material issue exists, FAIL."

---

# 74. ANALYTICS

Track:

jobs discovered
jobs shortlisted
jobs rejected
applications prepared
applications submitted
interviews
rejections
offers

Calculate:

match → application rate
application → interview rate
interview → offer rate

Break down by:

city
company
role
source
resume variant
skill cluster

This will eventually tell the user which strategy actually works.

---

# 75. LEARNING LOOP

The system should learn from outcomes.

Example:

If Java + React roles generate more interviews:

increase their priority.

If a particular source generates poor jobs:

reduce source priority.

If resume variant B gets better results:

increase its use.

But:

DO NOT modify factual candidate information automatically.

Only learn:

ranking
source priority
resume variant preference
search queries

---

# 76. NO LINKEDIN SCRAPER

Explicitly prohibit:

LinkedIn crawling
LinkedIn profile scraping
LinkedIn job scraping
LinkedIn session automation
LinkedIn Easy Apply automation

LinkedIn may only be stored as a candidate profile URL.

---

# 77. NO ANTI-BOT EVASION

Do not implement:

stealth plugins
fingerprint spoofing
proxy rotation
CAPTCHA solving
browser fingerprint evasion
anti-bot bypass
fake user behavior

If blocked:

STOP.

Manual fallback.

---

# 78. COST CONTROL

Create usage tracking:

llm_usage

fields:

provider
model
operation
input_tokens
output_tokens
estimated_cost
timestamp

Even though the goal is zero additional spend, track usage.

Create daily limits.

---

# 79. PROVIDER FAILOVER

Example:

Gemini unavailable

→ Groq

Groq unavailable

→ local model

All unavailable

→ deterministic workflow/manual

Never make the entire system dependent on one AI provider.

---

# 80. PRODUCT PRINCIPLE

The system should follow this philosophy:

AUTOMATE DISCOVERY.

AUTOMATE ANALYSIS.

AUTOMATE PERSONALIZATION.

AUTOMATE FORM PREPARATION.

HUMAN APPROVES FINAL SUBMISSION.

This is preferable to a reckless "100% autonomous auto-apply bot."

---

# 81. FIRST TASK FOR THE CODING AGENT

Before writing significant code:

1. Inspect repository.
2. Inspect uploaded resume.
3. Inspect portfolio.
4. Produce implementation plan.
5. Identify assumptions.
6. Identify risks.
7. Define database schema.
8. Define API.
9. Define frontend routes.
10. Define module boundaries.

Then start implementing.

Do NOT ask me to repeat information already present in this prompt.

If something genuinely requires a personal value that is unknown, create a configuration placeholder and clearly identify it.

---

# 82. IMPORTANT USER CONFIGURATION VALUES

Create a setup wizard for values not known from the resume:

EMAIL
PHONE
CURRENT CTC
EXPECTED CTC
NOTICE PERIOD
PREFERRED LOCATIONS
REMOTE PREFERENCE
MINIMUM JOB SCORE
DAILY APPLICATION LIMIT
GEMINI API KEY
GROQ API KEY
GITHUB TOKEN if needed
GMAIL OAUTH
NOTIFICATION SETTINGS

Do not invent these values.

---

# 83. PRODUCTION DEPLOYMENT

The application should be deployable using:

Docker Compose

Target environments:

local Linux
personal VPS
OCI VM
other self-hosted Linux server

Avoid requiring AWS/GCP/Azure paid infrastructure.

The architecture should work on a modest VM.

---

# 84. BACKUP

Implement:

PostgreSQL backup

Candidate profile backup

Resume versions

Application history

Configuration backup excluding secrets

Provide:

backup.sh
restore.sh

---

# 85. DOCUMENTATION

Create:

README.md

ARCHITECTURE.md

DEVELOPMENT.md

DEPLOYMENT.md

SECURITY.md

JOB_SOURCES.md

AI_MODELS.md

RESUME_ENGINE.md

BROWSER_AUTOMATION.md

TROUBLESHOOTING.md

GEMINI.md

---

# 86. FINAL OUTPUT FROM YOU

When implementation reaches a stable milestone, report:

1. What was implemented
2. Files created
3. Files modified
4. Database migrations
5. Environment variables
6. How to run
7. How to test
8. What remains
9. Known limitations
10. Security concerns

Do not claim production readiness until tests and deployment checks pass.

---

# 87. MOST IMPORTANT PRODUCT REQUIREMENT

This is NOT a generic AI job scraper.

It is a personalized:

INDIA JOB SEARCH
+
JOB INTELLIGENCE
+
RESUME PERSONALIZATION
+
APPLICATION ASSISTANT
+
APPLICATION TRACKER

built specifically around:

SHUBHAM PRAKASH

Java
Spring Boot
Microservices
React
TypeScript
Node.js
Kafka
Redis
PostgreSQL
MongoDB
Docker
AWS
System Design

and approximately 3 years of professional experience.

The system should aggressively optimize for high-quality Java + React / Java Spring Boot opportunities while remaining truthful, compliant, maintainable, and safe.

Build the product accordingly.
