--
-- PostgreSQL database dump
--

\restrict irpkRizAKBr8gB0D52a4aO2DhavOAejWaWixDVcD3X1b44E1qpEx3MmmZeMfaQY

-- Dumped from database version 16.15
-- Dumped by pg_dump version 16.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: application_events; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.application_events (
    id integer NOT NULL,
    application_id integer NOT NULL,
    event_type character varying NOT NULL,
    event_data text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_events OWNER TO jobagent;

--
-- Name: application_events_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.application_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.application_events_id_seq OWNER TO jobagent;

--
-- Name: application_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.application_events_id_seq OWNED BY public.application_events.id;


--
-- Name: application_questions; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.application_questions (
    id integer NOT NULL,
    application_id integer NOT NULL,
    question character varying NOT NULL,
    proposed_answer text,
    final_answer text,
    answer_source character varying,
    confidence double precision NOT NULL,
    requires_human boolean NOT NULL,
    approved boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.application_questions OWNER TO jobagent;

--
-- Name: application_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.application_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.application_questions_id_seq OWNER TO jobagent;

--
-- Name: application_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.application_questions_id_seq OWNED BY public.application_questions.id;


--
-- Name: applications; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.applications (
    id integer NOT NULL,
    job_id integer NOT NULL,
    candidate_id integer NOT NULL,
    status character varying NOT NULL,
    resume_version_id integer,
    cover_letter text,
    application_url character varying,
    applied_at timestamp with time zone,
    job_score integer,
    notes text,
    screenshot_path character varying,
    submission_evidence text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.applications OWNER TO jobagent;

--
-- Name: applications_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.applications_id_seq OWNER TO jobagent;

--
-- Name: applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.applications_id_seq OWNED BY public.applications.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying NOT NULL,
    entity_type character varying,
    entity_id integer,
    details text,
    ip_address character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO jobagent;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO jobagent;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: candidate_evidence; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.candidate_evidence (
    id integer NOT NULL,
    candidate_id integer NOT NULL,
    fact_id integer NOT NULL,
    evidence_type character varying NOT NULL,
    description character varying NOT NULL,
    source_reference character varying,
    confidence double precision NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.candidate_evidence OWNER TO jobagent;

--
-- Name: candidate_evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.candidate_evidence_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_evidence_id_seq OWNER TO jobagent;

--
-- Name: candidate_evidence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.candidate_evidence_id_seq OWNED BY public.candidate_evidence.id;


--
-- Name: candidate_facts; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.candidate_facts (
    id integer NOT NULL,
    candidate_id integer NOT NULL,
    fact_id character varying NOT NULL,
    claim character varying NOT NULL,
    category character varying NOT NULL,
    source character varying NOT NULL,
    verified boolean NOT NULL,
    allowed_for_resume boolean NOT NULL,
    allowed_for_application boolean NOT NULL,
    metadata_json text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.candidate_facts OWNER TO jobagent;

--
-- Name: candidate_facts_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.candidate_facts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_facts_id_seq OWNER TO jobagent;

--
-- Name: candidate_facts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.candidate_facts_id_seq OWNED BY public.candidate_facts.id;


--
-- Name: candidate_profiles; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.candidate_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    full_name character varying NOT NULL,
    email character varying,
    phone character varying,
    location character varying,
    portfolio_url character varying,
    github_url character varying,
    linkedin_url character varying,
    current_company character varying,
    "current_role" character varying,
    total_experience_months integer,
    notice_period_days integer,
    current_ctc character varying,
    expected_ctc character varying,
    preferred_locations text,
    remote_preference character varying,
    target_roles text,
    profile_data text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.candidate_profiles OWNER TO jobagent;

--
-- Name: candidate_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.candidate_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_profiles_id_seq OWNER TO jobagent;

--
-- Name: candidate_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.candidate_profiles_id_seq OWNED BY public.candidate_profiles.id;


--
-- Name: job_scores; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.job_scores (
    id integer NOT NULL,
    job_id integer NOT NULL,
    total_score integer NOT NULL,
    role_relevance integer NOT NULL,
    core_skills integer NOT NULL,
    distributed_systems integer NOT NULL,
    experience_fit integer NOT NULL,
    location_score integer NOT NULL,
    job_quality integer NOT NULL,
    llm_score integer,
    fit_category character varying,
    strengths text,
    gaps text,
    risks text,
    recommended_variant character varying,
    reasoning text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.job_scores OWNER TO jobagent;

--
-- Name: job_scores_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.job_scores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.job_scores_id_seq OWNER TO jobagent;

--
-- Name: job_scores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.job_scores_id_seq OWNED BY public.job_scores.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    source character varying NOT NULL,
    source_job_id character varying,
    url character varying,
    canonical_url character varying,
    title character varying NOT NULL,
    company character varying,
    locations text,
    remote boolean NOT NULL,
    experience_min double precision,
    experience_max double precision,
    employment_type character varying,
    salary_min integer,
    salary_max integer,
    currency character varying NOT NULL,
    description text,
    skills text,
    required_skills text,
    preferred_skills text,
    posted_at timestamp with time zone,
    deadline timestamp with time zone,
    application_url character varying,
    source_type character varying,
    raw_content_hash character varying,
    status character varying NOT NULL,
    fraud_risk character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.jobs OWNER TO jobagent;

--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO jobagent;

--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: llm_requests; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.llm_requests (
    id integer NOT NULL,
    provider character varying NOT NULL,
    model character varying NOT NULL,
    operation character varying NOT NULL,
    prompt_version character varying,
    input_tokens integer,
    output_tokens integer,
    estimated_cost double precision NOT NULL,
    duration_ms integer,
    status character varying NOT NULL,
    error_message character varying,
    job_id integer,
    application_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.llm_requests OWNER TO jobagent;

--
-- Name: llm_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.llm_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.llm_requests_id_seq OWNER TO jobagent;

--
-- Name: llm_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.llm_requests_id_seq OWNED BY public.llm_requests.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    type character varying NOT NULL,
    title character varying NOT NULL,
    message character varying NOT NULL,
    read boolean NOT NULL,
    action_url character varying,
    data text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO jobagent;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO jobagent;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: resume_variants; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.resume_variants (
    id integer NOT NULL,
    name character varying NOT NULL,
    display_name character varying NOT NULL,
    description character varying,
    priority_skills text,
    is_default boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.resume_variants OWNER TO jobagent;

--
-- Name: resume_variants_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.resume_variants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resume_variants_id_seq OWNER TO jobagent;

--
-- Name: resume_variants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.resume_variants_id_seq OWNED BY public.resume_variants.id;


--
-- Name: resume_versions; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.resume_versions (
    id integer NOT NULL,
    variant_id integer NOT NULL,
    job_id integer,
    version_number integer NOT NULL,
    content_markdown text,
    content_json text,
    file_path_docx character varying,
    file_path_pdf character varying,
    keyword_mapping text,
    evidence_mapping text,
    change_diff text,
    confidence_score double precision,
    unsupported_claims text,
    missing_skills text,
    validation_status character varying,
    validation_report text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.resume_versions OWNER TO jobagent;

--
-- Name: resume_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.resume_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resume_versions_id_seq OWNER TO jobagent;

--
-- Name: resume_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.resume_versions_id_seq OWNED BY public.resume_versions.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: jobagent
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying NOT NULL,
    full_name character varying NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO jobagent;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: jobagent
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO jobagent;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jobagent
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: application_events id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_events ALTER COLUMN id SET DEFAULT nextval('public.application_events_id_seq'::regclass);


--
-- Name: application_questions id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_questions ALTER COLUMN id SET DEFAULT nextval('public.application_questions_id_seq'::regclass);


--
-- Name: applications id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.applications ALTER COLUMN id SET DEFAULT nextval('public.applications_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: candidate_evidence id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_evidence ALTER COLUMN id SET DEFAULT nextval('public.candidate_evidence_id_seq'::regclass);


--
-- Name: candidate_facts id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_facts ALTER COLUMN id SET DEFAULT nextval('public.candidate_facts_id_seq'::regclass);


--
-- Name: candidate_profiles id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_profiles ALTER COLUMN id SET DEFAULT nextval('public.candidate_profiles_id_seq'::regclass);


--
-- Name: job_scores id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.job_scores ALTER COLUMN id SET DEFAULT nextval('public.job_scores_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: llm_requests id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.llm_requests ALTER COLUMN id SET DEFAULT nextval('public.llm_requests_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: resume_variants id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_variants ALTER COLUMN id SET DEFAULT nextval('public.resume_variants_id_seq'::regclass);


--
-- Name: resume_versions id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_versions ALTER COLUMN id SET DEFAULT nextval('public.resume_versions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: application_events; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.application_events (id, application_id, event_type, event_data, created_at) FROM stdin;
1	1	STATUS_TRANSITION_AWAITING_APPROVAL	{"from_status": "RESUME_READY", "to_status": "AWAITING_APPROVAL", "user_approved": true, "notes": "Application packet bundled and queued for human approval.", "metadata": {}, "timestamp": "2026-09-22T22:38:59.725333+00:00"}	2026-09-22 22:38:59.726949+00
2	1	STATUS_TRANSITION_APPLYING	{"from_status": "AWAITING_APPROVAL", "to_status": "APPLYING", "user_approved": true, "notes": "Executing DRY-RUN submission", "metadata": {}, "timestamp": "2026-09-22T22:38:59.767926+00:00"}	2026-09-22 22:38:59.760482+00
3	1	STATUS_TRANSITION_APPLIED	{"from_status": "APPLYING", "to_status": "APPLIED", "user_approved": true, "notes": "[DRY RUN SUCCESS] Confirmation code: DRY-RUN-553C54AA", "metadata": {"confirmation_code": "DRY-RUN-553C54AA", "mode": "DRY_RUN"}, "timestamp": "2026-09-22T22:38:59.797253+00:00"}	2026-09-22 22:38:59.782377+00
4	1	INTERVIEW_SCHEDULED	{"from_status": "APPLIED", "to_status": "INTERVIEW", "timestamp": "2026-09-22 22:38:59 UTC", "reason": null, "interview": {"round": "System Design & Concurrency", "scheduled_date": "2026-09-22T22:38:59.832Z", "interviewer": "Priya Sharma (Engineering Director)", "meeting_link": "https://meet.google.com/swiggy-interview"}}	2026-09-22 22:38:59.86916+00
\.


--
-- Data for Name: application_questions; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.application_questions (id, application_id, question, proposed_answer, final_answer, answer_source, confidence, requires_human, approved, created_at, updated_at) FROM stdin;
1	1	How many years of relevant experience do you have in software engineering?	~3.2 years of professional software development experience (3 years at TCS Digital, currently at Accenture).	~3.2 years of professional software development experience (3 years at TCS Digital, currently at Accenture).	candidate_facts.experience.total	1	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
2	1	What is your notice period and earliest joining date?	30 days notice period	30 days notice period	candidate_facts.profile.notice_period	1	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
3	1	Are you comfortable working in ["Mumbai"] or Remote?	Yes, I have relevant hands-on engineering background and am prepared to discuss specific details during technical interviews.	Yes, I have relevant hands-on engineering background and am prepared to discuss specific details during technical interviews.	heuristic_default	0.6	t	f	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
4	1	Are you authorized to work in India?	Yes, I am an Indian citizen and legally authorized to work in India without sponsorship.	Yes, I am an Indian citizen and legally authorized to work in India without sponsorship.	candidate_facts.profile.citizenship	1	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
5	1	What is your experience with Java and Spring Boot microservices?	3.2 years of intensive production experience with Java 17, Spring Boot, microservices architecture, and REST API development across TCS Digital and Accenture.	3.2 years of intensive production experience with Java 17, Spring Boot, microservices architecture, and REST API development across TCS Digital and Accenture.	candidate_facts.experience.tcs_accenture	1	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
6	1	Do you have experience building web frontends with React?	2.5+ years of hands-on experience developing scalable frontend applications with React, TypeScript, and modern state management.	2.5+ years of hands-on experience developing scalable frontend applications with React, TypeScript, and modern state management.	candidate_facts.skills.react	0.95	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
7	1	Do you have experience with Kafka event streaming or message queues?	2+ years of distributed systems experience implementing Kafka event streams, Redis caching layers, and WebSockets (production and TradeX project).	2+ years of distributed systems experience implementing Kafka event streams, Redis caching layers, and WebSockets (production and TradeX project).	candidate_facts.projects.tradex	0.95	f	t	2026-09-22 22:38:59.711173+00	2026-09-22 22:38:59.711173+00
\.


--
-- Data for Name: applications; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.applications (id, job_id, candidate_id, status, resume_version_id, cover_letter, application_url, applied_at, job_score, notes, screenshot_path, submission_evidence, created_at, updated_at) FROM stdin;
1	1	1	INTERVIEW	1	I am writing to express my strong interest in the Senior Software Engineer (Java + React) opening at Swiggy India. With ~3.2 years of specialized experience in Java, Spring Boot microservices, and modern React full-stack engineering, I focus on building resilient, high-throughput backend services and clean web architectures.\n\nIn my production engineering roles at Accenture and TCS Digital, I engineered scalable microservices handling concurrent workloads of 10,000+ active users. At TCS Digital, I architected RESTful endpoints, optimized relational queries in PostgreSQL, and integrated Redis caching to dramatically reduce database overhead. I emphasize strict type safety, comprehensive unit testing, and maintainable domain-driven design.\n\nIn the distributed systems domain, I built TradeX, an event-driven stock trading platform powered by Spring Boot, Apache Kafka event streams, Redis caching, and WebSockets for real-time market data dissemination. On the frontend, my work with React and TypeScript ensures high performance, clean state management, and intuitive user experiences.\n\nGiven Swiggy India's focus on Java, Kafka, Microservices, React, I am confident in my ability to hit the ground running. I hold a 30-day notice period and look forward to discussing how my background can support your engineering initiatives.	\N	2026-09-22 22:38:59.797938+00	86	\n[2026-09-22 22:38] Application packet bundled and queued for human approval.\n[2026-09-22 22:38] Executing DRY-RUN submission\n[2026-09-22 22:38] [DRY RUN SUCCESS] Confirmation code: DRY-RUN-553C54AA	\N	{"status": "SUCCESS", "mode": "DRY_RUN", "confirmation_code": "DRY-RUN-553C54AA", "submitted_at": "2026-09-22T22:38:59.797166+00:00", "notes": "Simulated application submission completed with full packet validation.", "packet": {"application_id": 1, "job": {"id": 1, "title": "Senior Software Engineer (Java + React)", "company": "Swiggy India", "source": "manual", "application_url": null}, "candidate": {"full_name": "Shubham Prakash", "email": "shubhamprakash681@gmail.com", "phone": "+91-6299783192", "location": "Mumbai, India", "portfolio_url": "https://www.shubhamprakash681.in/", "current_company": "Accenture", "current_role": "Packaged App Development Analyst", "notice_period_days": 30}, "documents": {"resume_version_id": 1, "resume_version_number": 1, "resume_pdf_path": "documents/generated/Resume_Shubham_Prakash_1_v1.pdf", "resume_docx_path": "documents/generated/Resume_Shubham_Prakash_1_v1.docx", "cover_letter_present": true, "cover_letter_words": 190}, "screening_questions": [{"id": 1, "question": "How many years of relevant experience do you have in software engineering?", "answer": "~3.2 years of professional software development experience (3 years at TCS Digital, currently at Accenture).", "confidence": 1.0, "approved": true}, {"id": 2, "question": "What is your notice period and earliest joining date?", "answer": "30 days notice period", "confidence": 1.0, "approved": true}, {"id": 3, "question": "Are you comfortable working in [\\"Mumbai\\"] or Remote?", "answer": "Yes, I have relevant hands-on engineering background and am prepared to discuss specific details during technical interviews.", "confidence": 0.6, "approved": false}, {"id": 4, "question": "Are you authorized to work in India?", "answer": "Yes, I am an Indian citizen and legally authorized to work in India without sponsorship.", "confidence": 1.0, "approved": true}, {"id": 5, "question": "What is your experience with Java and Spring Boot microservices?", "answer": "3.2 years of intensive production experience with Java 17, Spring Boot, microservices architecture, and REST API development across TCS Digital and Accenture.", "confidence": 1.0, "approved": true}, {"id": 6, "question": "Do you have experience building web frontends with React?", "answer": "2.5+ years of hands-on experience developing scalable frontend applications with React, TypeScript, and modern state management.", "confidence": 0.95, "approved": true}, {"id": 7, "question": "Do you have experience with Kafka event streaming or message queues?", "answer": "2+ years of distributed systems experience implementing Kafka event streams, Redis caching layers, and WebSockets (production and TradeX project).", "confidence": 0.95, "approved": true}], "compiled_at": "2026-09-22T22:38:59.797003+00:00"}}	2026-09-22 22:38:59.698208+00	2026-09-22 22:38:59.851248+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.audit_logs (id, user_id, action, entity_type, entity_id, details, ip_address, created_at) FROM stdin;
1	\N	JOB_CLASSIFIED	job	1	{"role_category": "DISTRIBUTED_SYSTEMS", "fit_category": "HIGH_FIT", "fit_score": 90, "variant": "backend-distributed"}	\N	2026-09-22 22:38:53.344621+00
2	\N	RESUME_TAILORED	resume	1	{"job_id": 1, "variant": "java-react-fullstack", "version": 1, "validation_status": "passed", "confidence": 1.0}	\N	2026-09-22 22:38:53.378069+00
\.


--
-- Data for Name: candidate_evidence; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.candidate_evidence (id, candidate_id, fact_id, evidence_type, description, source_reference, confidence, created_at, updated_at) FROM stdin;
1	1	1	employment	Shubham Prakash has 3.2 years (39 months) of professional software engineering experience.	docs/ShubhamPrakash_Resume_Latest.pdf	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
2	1	2	employment	Currently working as Packaged App Development Analyst at Accenture in Mumbai, India.	docs/ShubhamPrakash_Resume_Latest.pdf	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
3	1	3	employment	Worked as Packaged App Development Analyst at Accenture from 2026-04 to Present.	Resume - Experience - Accenture	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
4	1	4	employment	Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards.	Resume - Accenture Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
5	1	5	employment	Worked as Software Developer at Tata Consultancy Services (TCS Digital) from 2023-06 to 2026-04.	Resume - Experience - Tata Consultancy Services (TCS Digital)	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
6	1	6	employment	Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js, following layered architecture and RESTful API principles.	Resume - Tata Consultancy Services (TCS Digital) Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
7	1	7	employment	Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO across 3 enterprise applications, resolving authentication and login issues.	Resume - Tata Consultancy Services (TCS Digital) Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
8	1	8	employment	Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing and service communication, improving scalability and maintainability.	Resume - Tata Consultancy Services (TCS Digital) Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
9	1	9	employment	Optimized caching, data structures, and session management, supporting 10,000+ concurrent users with zero data conflicts and achieving up to 80% faster load times; built real-time Chart.js dashboards improving engagement by up to 90%.	Resume - Tata Consultancy Services (TCS Digital) Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
10	1	10	employment	Worked as Software Engineer Intern at Sylvr from 2023-03 to 2023-06.	Resume - Experience - Sylvr	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
11	1	11	employment	Developed MERN stack applications for financial data visualization serving 50+ organizations, implementing REST APIs, OTP authentication, and role-based access control.	Resume - Sylvr Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
12	1	12	employment	Containerized applications using Docker and deployed on Linux servers with Nginx, achieving 98% uptime.	Resume - Sylvr Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
13	1	13	employment	Worked as Research Intern at IIT Patna from 2022-01 to 2022-05.	Resume - Experience - IIT Patna	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
14	1	14	employment	Worked on deep learning research involving emotion prediction, psychiatric disorder prediction from BCI signals, and audio classification.	Resume - IIT Patna Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
15	1	15	project	Built TradeX (Realtime Paper Trading Platform): Designed and built a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.	Portfolio / GitHub - TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
16	1	16	project	Designed a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.	Project TradeX - Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
17	1	17	project	Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence.	Project TradeX - Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
18	1	18	project	Built VideoShare (Video Sharing & Streaming Platform): Built a full-featured YouTube-like video sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.	Portfolio / GitHub - VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
19	1	19	project	Built a YouTube-like video-sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.	Project VideoShare - Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
20	1	20	project	Implemented MongoDB Atlas fuzzy search and an NSFW content classification pipeline for videos and thumbnails; deployed using Docker, AWS EC2, and Nginx with 99% uptime.	Project VideoShare - Bullet Point	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
21	1	21	skill	Proficient in Java (expert, ~3.2 years). Evidence: Accenture, TCS Digital, TradeX, CUSAT.	Accenture, TCS Digital, TradeX, CUSAT	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
22	1	22	skill	Proficient in Spring Boot (expert, ~3.0 years). Evidence: Accenture, TCS Digital, TradeX.	Accenture, TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
23	1	23	skill	Proficient in Spring MVC (advanced, ~2.5 years). Evidence: TCS Digital.	TCS Digital	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
24	1	24	skill	Proficient in Spring Security (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
25	1	25	skill	Proficient in Spring Cloud (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
26	1	26	skill	Proficient in Node.js (intermediate, ~2.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	TCS Digital, Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
27	1	27	skill	Proficient in REST APIs (expert, ~3.0 years). Evidence: Accenture, TCS Digital, Sylvr, TradeX, VideoShare.	Accenture, TCS Digital, Sylvr, TradeX, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
28	1	28	skill	Proficient in Microservices (advanced, ~2.5 years). Evidence: Accenture, TCS Digital, TradeX.	Accenture, TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
29	1	29	skill	Proficient in Kafka (intermediate, ~1.5 years). Evidence: TradeX.	TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
30	1	30	skill	Proficient in RabbitMQ (intermediate, ~1.0 years). Evidence: Resume Skills.	Resume Skills	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
31	1	31	skill	Proficient in Redis (advanced, ~2.0 years). Evidence: TradeX, TCS Digital (caching).	TradeX, TCS Digital (caching)	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
32	1	32	skill	Proficient in WebSockets (intermediate, ~1.5 years). Evidence: TradeX.	TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
33	1	33	skill	Proficient in API Gateway (advanced, ~2.0 years). Evidence: TCS Digital (Spring Cloud Gateway), TradeX.	TCS Digital (Spring Cloud Gateway), TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
34	1	34	skill	Proficient in Eureka (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
35	1	35	skill	Proficient in PostgreSQL (advanced, ~2.5 years). Evidence: TradeX, Production systems.	TradeX, Production systems	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
36	1	36	skill	Proficient in MongoDB (intermediate, ~2.0 years). Evidence: Sylvr, VideoShare.	Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
37	1	37	skill	Proficient in JPA / Hibernate (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
38	1	38	skill	Proficient in Prisma (intermediate, ~1.0 years). Evidence: Resume Skills.	Resume Skills	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
39	1	39	skill	Proficient in Mongoose (intermediate, ~1.5 years). Evidence: Sylvr, VideoShare.	Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
40	1	40	skill	Proficient in React (advanced, ~2.5 years). Evidence: TCS Digital, Sylvr, VideoShare.	TCS Digital, Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
41	1	41	skill	Proficient in Next.js (intermediate, ~1.5 years). Evidence: Portfolio, Projects.	Portfolio, Projects	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
42	1	42	skill	Proficient in TypeScript (advanced, ~2.5 years). Evidence: TCS Digital, Projects.	TCS Digital, Projects	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
43	1	43	skill	Proficient in JavaScript (advanced, ~3.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	TCS Digital, Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
44	1	44	skill	Proficient in HTML5 / CSS3 (advanced, ~3.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	TCS Digital, Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
45	1	45	skill	Proficient in Chart.js (intermediate, ~1.5 years). Evidence: TCS Digital.	TCS Digital	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
46	1	46	skill	Proficient in Docker (advanced, ~2.0 years). Evidence: Sylvr, VideoShare, TradeX.	Sylvr, VideoShare, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
47	1	47	skill	Proficient in AWS EC2 (intermediate, ~1.5 years). Evidence: VideoShare.	VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
48	1	48	skill	Proficient in Nginx (intermediate, ~1.5 years). Evidence: Sylvr, VideoShare.	Sylvr, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
49	1	49	skill	Proficient in Git / CI/CD (advanced, ~3.0 years). Evidence: TCS Digital, Accenture, Projects.	TCS Digital, Accenture, Projects	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
50	1	50	skill	Proficient in Linux (advanced, ~3.0 years). Evidence: Sylvr, VideoShare, Daily dev.	Sylvr, VideoShare, Daily dev	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
51	1	51	skill	Proficient in JWT (advanced, ~2.5 years). Evidence: TCS Digital, TradeX, VideoShare.	TCS Digital, TradeX, VideoShare	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
52	1	52	skill	Proficient in OAuth2 (advanced, ~2.0 years). Evidence: TCS Digital.	TCS Digital	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
53	1	53	skill	Proficient in Auth0 SSO (intermediate, ~1.5 years). Evidence: TCS Digital.	TCS Digital	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
54	1	54	skill	Proficient in RBAC (advanced, ~2.0 years). Evidence: Sylvr, TCS Digital.	Sylvr, TCS Digital	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
55	1	55	skill	Proficient in System Design (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
56	1	56	skill	Proficient in High-Level Design (HLD) (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
57	1	57	skill	Proficient in Low-Level Design (LLD) (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	TCS Digital, TradeX	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
58	1	58	skill	Proficient in Data Structures & Algorithms (DSA) (advanced, ~3.0 years). Evidence: CUSAT, Professional work.	CUSAT, Professional work	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
59	1	59	skill	Proficient in Object-Oriented Programming (OOP) (expert, ~3.2 years). Evidence: Java enterprise development.	Java enterprise development	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
60	1	60	education	Graduated with Bachelor of Technology (B.Tech) in Electronics and Communication Engineering from Cochin University of Science and Technology with CGPA of 8.91 / 10.	docs/ShubhamPrakash_Resume_Latest.pdf	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
61	1	61	education	Research Internship Certificate in Deep Learning issued by IIT Patna (2022-05): Deep learning research involving emotion prediction and BCI signal processing.	docs/ShubhamPrakash_Resume_Latest.pdf	1	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
\.


--
-- Data for Name: candidate_facts; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.candidate_facts (id, candidate_id, fact_id, claim, category, source, verified, allowed_for_resume, allowed_for_application, metadata_json, created_at, updated_at) FROM stdin;
1	1	fact.profile.experience_tenure	Shubham Prakash has 3.2 years (39 months) of professional software engineering experience.	experience	resume	t	t	t	{"keywords": ["experience", "years", "tenure", "software engineer"], "metrics": [], "evidence_type": "employment", "source_reference": "docs/ShubhamPrakash_Resume_Latest.pdf"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
2	1	fact.profile.current_role	Currently working as Packaged App Development Analyst at Accenture in Mumbai, India.	experience	resume	t	t	t	{"keywords": ["Accenture", "Packaged App Development Analyst", "current"], "metrics": [], "evidence_type": "employment", "source_reference": "docs/ShubhamPrakash_Resume_Latest.pdf"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
3	1	fact.exp.accenture.role	Worked as Packaged App Development Analyst at Accenture from 2026-04 to Present.	experience	resume	t	t	t	{"keywords": ["Accenture", "Packaged App Development Analyst", "Mumbai, India"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Experience - Accenture"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
4	1	fact.exp.accenture.enterprise_apps	Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards.	experience	resume	t	t	t	{"keywords": ["Java", "Spring Boot", "Microservices", "REST APIs", "Accenture"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Accenture Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
5	1	fact.exp.tata_consultancy_services_(tcs_digital).role	Worked as Software Developer at Tata Consultancy Services (TCS Digital) from 2023-06 to 2026-04.	experience	resume	t	t	t	{"keywords": ["Tata Consultancy Services (TCS Digital)", "Software Developer", "Mumbai, India"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Experience - Tata Consultancy Services (TCS Digital)"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
6	1	fact.exp.tcs.microservices	Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js, following layered architecture and RESTful API principles.	experience	resume	t	t	t	{"keywords": ["Java", "Spring Boot", "React", "TypeScript", "Node.js", "Microservices", "REST APIs", "Tata Consultancy Services (TCS Digital)"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Tata Consultancy Services (TCS Digital) Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
7	1	fact.exp.tcs.auth_migration	Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO across 3 enterprise applications, resolving authentication and login issues.	experience	resume	t	t	t	{"keywords": ["JWT", "OAuth2", "Auth0", "ArcGIS", "SSO", "Spring Security", "Tata Consultancy Services (TCS Digital)"], "metrics": [{"name": "enterprise_applications_count", "value": 3, "unit": null, "description": "3 enterprise applications secured with JWT, OAuth2, and Auth0 SSO"}], "evidence_type": "employment", "source_reference": "Resume - Tata Consultancy Services (TCS Digital) Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
8	1	fact.exp.tcs.spring_cloud	Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing and service communication, improving scalability and maintainability.	experience	resume	t	t	t	{"keywords": ["Spring Cloud", "Eureka", "Spring Cloud Gateway", "Microservices", "Routing", "Tata Consultancy Services (TCS Digital)"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Tata Consultancy Services (TCS Digital) Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
9	1	fact.exp.tcs.cache_optimization	Optimized caching, data structures, and session management, supporting 10,000+ concurrent users with zero data conflicts and achieving up to 80% faster load times; built real-time Chart.js dashboards improving engagement by up to 90%.	experience	resume	t	t	t	{"keywords": ["Caching", "Session Management", "Chart.js", "Performance Optimization", "Tata Consultancy Services (TCS Digital)"], "metrics": [{"name": "concurrent_users", "value": 10000, "unit": null, "description": "Supported 10,000+ concurrent users with zero data conflicts"}, {"name": "load_time_improvement", "value": 80, "unit": "percent", "description": "Up to 80% faster load times"}, {"name": "engagement_improvement", "value": 90, "unit": "percent", "description": "Improved user engagement by up to 90%"}], "evidence_type": "employment", "source_reference": "Resume - Tata Consultancy Services (TCS Digital) Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
10	1	fact.exp.sylvr.role	Worked as Software Engineer Intern at Sylvr from 2023-03 to 2023-06.	experience	resume	t	t	t	{"keywords": ["Sylvr", "Software Engineer Intern", "Remote, India"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Experience - Sylvr"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
11	1	fact.exp.sylvr.mern_financial	Developed MERN stack applications for financial data visualization serving 50+ organizations, implementing REST APIs, OTP authentication, and role-based access control.	experience	resume	t	t	t	{"keywords": ["React", "Node.js", "MongoDB", "Express", "REST APIs", "OTP Auth", "RBAC", "Sylvr"], "metrics": [{"name": "organizations_served", "value": 50, "unit": null, "description": "Served 50+ organizations"}], "evidence_type": "employment", "source_reference": "Resume - Sylvr Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
12	1	fact.exp.sylvr.docker_deployment	Containerized applications using Docker and deployed on Linux servers with Nginx, achieving 98% uptime.	experience	resume	t	t	t	{"keywords": ["Docker", "Nginx", "Linux", "Deployment", "Sylvr"], "metrics": [{"name": "uptime", "value": 98, "unit": "percent", "description": "98% uptime achieved"}], "evidence_type": "employment", "source_reference": "Resume - Sylvr Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
13	1	fact.exp.iit_patna.role	Worked as Research Intern at IIT Patna from 2022-01 to 2022-05.	experience	resume	t	t	t	{"keywords": ["IIT Patna", "Research Intern", "Remote, India"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - Experience - IIT Patna"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
14	1	fact.exp.iit_patna.deep_learning	Worked on deep learning research involving emotion prediction, psychiatric disorder prediction from BCI signals, and audio classification.	experience	resume	t	t	t	{"keywords": ["Python", "Deep Learning", "Signal Processing", "IIT Patna"], "metrics": [], "evidence_type": "employment", "source_reference": "Resume - IIT Patna Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
15	1	fact.proj.proj.tradex.overview	Built TradeX (Realtime Paper Trading Platform): Designed and built a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.	project	portfolio	t	t	t	{"keywords": ["TradeX", "Realtime Paper Trading Platform", "Java", "Spring Boot", "Spring Cloud", "Eureka", "API Gateway", "Kafka", "WebSockets", "Redis", "PostgreSQL", "Docker", "System Design"], "metrics": [{"name": "stocks_etfs_tracked", "value": 15, "unit": null, "description": "15 Indian stocks/ETFs price history generation"}, {"name": "historical_data_span", "value": 10, "unit": "years", "description": "10 years of OHLCV historical data"}], "evidence_type": "project", "source_reference": "Portfolio / GitHub - TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
36	1	fact.skill.databases.mongodb	Proficient in MongoDB (intermediate, ~2.0 years). Evidence: Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["MongoDB", "Databases & ORM", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
16	1	fact.proj.tradex.microservices	Designed a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.	project	portfolio	t	t	t	{"keywords": ["Spring Boot", "Microservices", "API Gateway", "Eureka", "System Design", "TradeX"], "metrics": [], "evidence_type": "project", "source_reference": "Project TradeX - Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
17	1	fact.proj.tradex.kafka_websockets	Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence.	project	portfolio	t	t	t	{"keywords": ["Kafka", "WebSockets", "Redis", "PostgreSQL", "Data Streaming", "Performance", "TradeX"], "metrics": [], "evidence_type": "project", "source_reference": "Project TradeX - Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
18	1	fact.proj.proj.videoshare.overview	Built VideoShare (Video Sharing & Streaming Platform): Built a full-featured YouTube-like video sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.	project	portfolio	t	t	t	{"keywords": ["VideoShare", "Video Sharing & Streaming Platform", "Node.js", "React", "MongoDB Atlas", "Express", "Docker", "AWS EC2", "Nginx", "REST APIs", "Authentication"], "metrics": [{"name": "uptime", "value": 99, "unit": "percent", "description": "99% uptime on AWS EC2 with Nginx"}], "evidence_type": "project", "source_reference": "Portfolio / GitHub - VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
19	1	fact.proj.videoshare.full_features	Built a YouTube-like video-sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.	project	portfolio	t	t	t	{"keywords": ["Node.js", "React", "REST APIs", "Streaming", "Full Stack", "VideoShare"], "metrics": [], "evidence_type": "project", "source_reference": "Project VideoShare - Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
20	1	fact.proj.videoshare.fuzzy_search_ml	Implemented MongoDB Atlas fuzzy search and an NSFW content classification pipeline for videos and thumbnails; deployed using Docker, AWS EC2, and Nginx with 99% uptime.	project	portfolio	t	t	t	{"keywords": ["MongoDB Atlas", "Fuzzy Search", "Machine Learning", "Docker", "AWS EC2", "Nginx", "VideoShare"], "metrics": [], "evidence_type": "project", "source_reference": "Project VideoShare - Bullet Point"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
21	1	fact.skill.backend.java	Proficient in Java (expert, ~3.2 years). Evidence: Accenture, TCS Digital, TradeX, CUSAT.	skill	resume	t	t	t	{"keywords": ["Java", "Backend Development", "expert"], "metrics": [], "evidence_type": "skill", "source_reference": "Accenture, TCS Digital, TradeX, CUSAT"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
22	1	fact.skill.backend.spring_boot	Proficient in Spring Boot (expert, ~3.0 years). Evidence: Accenture, TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Spring Boot", "Backend Development", "expert"], "metrics": [], "evidence_type": "skill", "source_reference": "Accenture, TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
23	1	fact.skill.backend.spring_mvc	Proficient in Spring MVC (advanced, ~2.5 years). Evidence: TCS Digital.	skill	resume	t	t	t	{"keywords": ["Spring MVC", "Backend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
24	1	fact.skill.backend.spring_security	Proficient in Spring Security (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Spring Security", "Backend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
25	1	fact.skill.backend.spring_cloud	Proficient in Spring Cloud (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Spring Cloud", "Backend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
26	1	fact.skill.backend.node.js	Proficient in Node.js (intermediate, ~2.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["Node.js", "Backend Development", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
27	1	fact.skill.backend.rest_apis	Proficient in REST APIs (expert, ~3.0 years). Evidence: Accenture, TCS Digital, Sylvr, TradeX, VideoShare.	skill	resume	t	t	t	{"keywords": ["REST APIs", "Backend Development", "expert"], "metrics": [], "evidence_type": "skill", "source_reference": "Accenture, TCS Digital, Sylvr, TradeX, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
28	1	fact.skill.backend.microservices	Proficient in Microservices (advanced, ~2.5 years). Evidence: Accenture, TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Microservices", "Backend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "Accenture, TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
29	1	fact.skill.distributed_systems.kafka	Proficient in Kafka (intermediate, ~1.5 years). Evidence: TradeX.	skill	resume	t	t	t	{"keywords": ["Kafka", "Distributed Systems & Messaging", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
30	1	fact.skill.distributed_systems.rabbitmq	Proficient in RabbitMQ (intermediate, ~1.0 years). Evidence: Resume Skills.	skill	resume	t	t	t	{"keywords": ["RabbitMQ", "Distributed Systems & Messaging", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Resume Skills"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
31	1	fact.skill.distributed_systems.redis	Proficient in Redis (advanced, ~2.0 years). Evidence: TradeX, TCS Digital (caching).	skill	resume	t	t	t	{"keywords": ["Redis", "Distributed Systems & Messaging", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TradeX, TCS Digital (caching)"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
32	1	fact.skill.distributed_systems.websockets	Proficient in WebSockets (intermediate, ~1.5 years). Evidence: TradeX.	skill	resume	t	t	t	{"keywords": ["WebSockets", "Distributed Systems & Messaging", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
33	1	fact.skill.distributed_systems.api_gateway	Proficient in API Gateway (advanced, ~2.0 years). Evidence: TCS Digital (Spring Cloud Gateway), TradeX.	skill	resume	t	t	t	{"keywords": ["API Gateway", "Distributed Systems & Messaging", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital (Spring Cloud Gateway), TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
34	1	fact.skill.distributed_systems.eureka	Proficient in Eureka (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Eureka", "Distributed Systems & Messaging", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
35	1	fact.skill.databases.postgresql	Proficient in PostgreSQL (advanced, ~2.5 years). Evidence: TradeX, Production systems.	skill	resume	t	t	t	{"keywords": ["PostgreSQL", "Databases & ORM", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TradeX, Production systems"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
37	1	fact.skill.databases.jpa___hibernate	Proficient in JPA / Hibernate (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["JPA / Hibernate", "Databases & ORM", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
38	1	fact.skill.databases.prisma	Proficient in Prisma (intermediate, ~1.0 years). Evidence: Resume Skills.	skill	resume	t	t	t	{"keywords": ["Prisma", "Databases & ORM", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Resume Skills"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
39	1	fact.skill.databases.mongoose	Proficient in Mongoose (intermediate, ~1.5 years). Evidence: Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["Mongoose", "Databases & ORM", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
40	1	fact.skill.frontend.react	Proficient in React (advanced, ~2.5 years). Evidence: TCS Digital, Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["React", "Frontend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
41	1	fact.skill.frontend.next.js	Proficient in Next.js (intermediate, ~1.5 years). Evidence: Portfolio, Projects.	skill	resume	t	t	t	{"keywords": ["Next.js", "Frontend Development", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Portfolio, Projects"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
42	1	fact.skill.frontend.typescript	Proficient in TypeScript (advanced, ~2.5 years). Evidence: TCS Digital, Projects.	skill	resume	t	t	t	{"keywords": ["TypeScript", "Frontend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Projects"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
43	1	fact.skill.frontend.javascript	Proficient in JavaScript (advanced, ~3.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["JavaScript", "Frontend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
44	1	fact.skill.frontend.html5___css3	Proficient in HTML5 / CSS3 (advanced, ~3.0 years). Evidence: TCS Digital, Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["HTML5 / CSS3", "Frontend Development", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
45	1	fact.skill.frontend.chart.js	Proficient in Chart.js (intermediate, ~1.5 years). Evidence: TCS Digital.	skill	resume	t	t	t	{"keywords": ["Chart.js", "Frontend Development", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
46	1	fact.skill.devops.docker	Proficient in Docker (advanced, ~2.0 years). Evidence: Sylvr, VideoShare, TradeX.	skill	resume	t	t	t	{"keywords": ["Docker", "DevOps & Cloud", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, VideoShare, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
47	1	fact.skill.devops.aws_ec2	Proficient in AWS EC2 (intermediate, ~1.5 years). Evidence: VideoShare.	skill	resume	t	t	t	{"keywords": ["AWS EC2", "DevOps & Cloud", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
48	1	fact.skill.devops.nginx	Proficient in Nginx (intermediate, ~1.5 years). Evidence: Sylvr, VideoShare.	skill	resume	t	t	t	{"keywords": ["Nginx", "DevOps & Cloud", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
49	1	fact.skill.devops.git___ci_cd	Proficient in Git / CI/CD (advanced, ~3.0 years). Evidence: TCS Digital, Accenture, Projects.	skill	resume	t	t	t	{"keywords": ["Git / CI/CD", "DevOps & Cloud", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, Accenture, Projects"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
50	1	fact.skill.devops.linux	Proficient in Linux (advanced, ~3.0 years). Evidence: Sylvr, VideoShare, Daily dev.	skill	resume	t	t	t	{"keywords": ["Linux", "DevOps & Cloud", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, VideoShare, Daily dev"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
51	1	fact.skill.security.jwt	Proficient in JWT (advanced, ~2.5 years). Evidence: TCS Digital, TradeX, VideoShare.	skill	resume	t	t	t	{"keywords": ["JWT", "Security & Auth", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX, VideoShare"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
52	1	fact.skill.security.oauth2	Proficient in OAuth2 (advanced, ~2.0 years). Evidence: TCS Digital.	skill	resume	t	t	t	{"keywords": ["OAuth2", "Security & Auth", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
53	1	fact.skill.security.auth0_sso	Proficient in Auth0 SSO (intermediate, ~1.5 years). Evidence: TCS Digital.	skill	resume	t	t	t	{"keywords": ["Auth0 SSO", "Security & Auth", "intermediate"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
54	1	fact.skill.security.rbac	Proficient in RBAC (advanced, ~2.0 years). Evidence: Sylvr, TCS Digital.	skill	resume	t	t	t	{"keywords": ["RBAC", "Security & Auth", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "Sylvr, TCS Digital"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
55	1	fact.skill.core_engineering.system_design	Proficient in System Design (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["System Design", "Core Engineering Fundamentals", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
56	1	fact.skill.core_engineering.high-level_design_(hld)	Proficient in High-Level Design (HLD) (advanced, ~2.0 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["High-Level Design (HLD)", "Core Engineering Fundamentals", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
57	1	fact.skill.core_engineering.low-level_design_(lld)	Proficient in Low-Level Design (LLD) (advanced, ~2.5 years). Evidence: TCS Digital, TradeX.	skill	resume	t	t	t	{"keywords": ["Low-Level Design (LLD)", "Core Engineering Fundamentals", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "TCS Digital, TradeX"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
58	1	fact.skill.core_engineering.data_structures_&_algorithms_(dsa)	Proficient in Data Structures & Algorithms (DSA) (advanced, ~3.0 years). Evidence: CUSAT, Professional work.	skill	resume	t	t	t	{"keywords": ["Data Structures & Algorithms (DSA)", "Core Engineering Fundamentals", "advanced"], "metrics": [], "evidence_type": "skill", "source_reference": "CUSAT, Professional work"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
59	1	fact.skill.core_engineering.object-oriented_programming_(oop)	Proficient in Object-Oriented Programming (OOP) (expert, ~3.2 years). Evidence: Java enterprise development.	skill	resume	t	t	t	{"keywords": ["Object-Oriented Programming (OOP)", "Core Engineering Fundamentals", "expert"], "metrics": [], "evidence_type": "skill", "source_reference": "Java enterprise development"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
60	1	fact.edu.edu.cusat	Graduated with Bachelor of Technology (B.Tech) in Electronics and Communication Engineering from Cochin University of Science and Technology with CGPA of 8.91 / 10.	education	resume	t	t	t	{"keywords": ["Cochin University of Science and Technology", "Bachelor of Technology (B.Tech)", "Electronics and Communication Engineering", "CGPA", "8.91"], "metrics": [], "evidence_type": "education", "source_reference": "docs/ShubhamPrakash_Resume_Latest.pdf"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
61	1	fact.cert.cert.iit_patna	Research Internship Certificate in Deep Learning issued by IIT Patna (2022-05): Deep learning research involving emotion prediction and BCI signal processing.	education	resume	t	t	t	{"keywords": ["Research Internship Certificate in Deep Learning", "IIT Patna"], "metrics": [], "evidence_type": "education", "source_reference": "docs/ShubhamPrakash_Resume_Latest.pdf"}	2026-09-22 22:38:29.171194+00	2026-09-22 22:38:29.171194+00
\.


--
-- Data for Name: candidate_profiles; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.candidate_profiles (id, user_id, full_name, email, phone, location, portfolio_url, github_url, linkedin_url, current_company, "current_role", total_experience_months, notice_period_days, current_ctc, expected_ctc, preferred_locations, remote_preference, target_roles, profile_data, created_at, updated_at) FROM stdin;
1	1	Shubham Prakash	shubhamprakash681@gmail.com	+91-6299783192	Mumbai, India	https://www.shubhamprakash681.in/	https://github.com/shubhamprakash681	https://www.linkedin.com/in/shubham-prakash	Accenture	Packaged App Development Analyst	39	30	Confidential / Discuss during interview	Competitive market rate	["Mumbai", "Bengaluru", "Hyderabad", "Pune", "Remote"]	hybrid_or_remote	["Senior Software Engineer", "Software Engineer - Backend", "Full Stack Engineer (Java + React)", "Spring Boot Developer", "Distributed Systems Engineer"]	{"profile": {"full_name": "Shubham Prakash", "first_name": "Shubham", "last_name": "Prakash", "title": "Software Engineer | Java & Spring Boot Full Stack", "email": "shubhamprakash681@gmail.com", "phone": "+91-6299783192", "location": "Mumbai, India", "citizenship": "India", "work_authorization": "India (Citizen)", "links": {"portfolio": "https://www.shubhamprakash681.in/", "github": "https://github.com/shubhamprakash681", "linkedin": "https://www.linkedin.com/in/shubham-prakash"}, "summary": "Software Engineer with 3+ years of experience building scalable applications using Java, Spring Boot, Spring Cloud, Microservices, React, and Node.js. Strong in System Design, DSA, REST APIs, distributed systems, authentication, and cloud-native development, with production experience in Kafka, Redis, PostgreSQL, Docker, AWS, JWT, and OAuth2.\\n", "current_employment": {"company": "Accenture", "role": "Packaged App Development Analyst", "start_date": "2026-04", "is_current": true, "location": "Mumbai, India"}, "preferences": {"total_experience_years": 3.2, "total_experience_months": 39, "notice_period_days": 30, "current_ctc": "Confidential / Discuss during interview", "expected_ctc": "Competitive market rate", "target_roles": ["Senior Software Engineer", "Software Engineer - Backend", "Full Stack Engineer (Java + React)", "Spring Boot Developer", "Distributed Systems Engineer"], "preferred_locations": ["Mumbai", "Bengaluru", "Hyderabad", "Pune", "Remote"], "remote_preference": "hybrid_or_remote", "willing_to_relocate": true}}, "experiences": [{"id": "exp.accenture", "company": "Accenture", "role": "Packaged App Development Analyst", "location": "Mumbai, India", "start_date": "2026-04", "end_date": null, "is_current": true, "employment_type": "full_time", "summary": "Building enterprise applications and microservices using Java and modern cloud architecture.", "technologies": ["Java", "Spring Boot", "Microservices", "REST APIs", "Enterprise Applications"], "bullet_points": [{"id": "exp.accenture.bp1", "fact_id": "fact.exp.accenture.enterprise_apps", "text": "Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards.", "metrics": [], "skills": ["Java", "Spring Boot", "Microservices", "REST APIs"], "verified": true}]}, {"id": "exp.tcs", "company": "Tata Consultancy Services (TCS Digital)", "role": "Software Developer", "location": "Mumbai, India", "start_date": "2023-06", "end_date": "2026-04", "is_current": false, "employment_type": "full_time", "summary": "Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js.", "technologies": ["Java", "Spring Boot", "Spring Cloud", "Eureka", "Spring Cloud Gateway", "React", "TypeScript", "Node.js", "JWT", "OAuth2", "Auth0", "Chart.js", "ArcGIS", "RESTful APIs"], "bullet_points": [{"id": "exp.tcs.bp1", "fact_id": "fact.exp.tcs.microservices", "text": "Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js, following layered architecture and RESTful API principles.", "metrics": [], "skills": ["Java", "Spring Boot", "React", "TypeScript", "Node.js", "Microservices", "REST APIs"], "verified": true}, {"id": "exp.tcs.bp2", "fact_id": "fact.exp.tcs.auth_migration", "text": "Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO across 3 enterprise applications, resolving authentication and login issues.", "metrics": [{"name": "enterprise_applications_count", "value": 3, "unit": null, "description": "3 enterprise applications secured with JWT, OAuth2, and Auth0 SSO"}], "skills": ["JWT", "OAuth2", "Auth0", "ArcGIS", "SSO", "Spring Security"], "verified": true}, {"id": "exp.tcs.bp3", "fact_id": "fact.exp.tcs.spring_cloud", "text": "Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing and service communication, improving scalability and maintainability.", "metrics": [], "skills": ["Spring Cloud", "Eureka", "Spring Cloud Gateway", "Microservices", "Routing"], "verified": true}, {"id": "exp.tcs.bp4", "fact_id": "fact.exp.tcs.cache_optimization", "text": "Optimized caching, data structures, and session management, supporting 10,000+ concurrent users with zero data conflicts and achieving up to 80% faster load times; built real-time Chart.js dashboards improving engagement by up to 90%.", "metrics": [{"name": "concurrent_users", "value": 10000, "unit": null, "description": "Supported 10,000+ concurrent users with zero data conflicts"}, {"name": "load_time_improvement", "value": 80, "unit": "percent", "description": "Up to 80% faster load times"}, {"name": "engagement_improvement", "value": 90, "unit": "percent", "description": "Improved user engagement by up to 90%"}], "skills": ["Caching", "Session Management", "Chart.js", "Performance Optimization"], "verified": true}]}, {"id": "exp.sylvr", "company": "Sylvr", "role": "Software Engineer Intern", "location": "Remote, India", "start_date": "2023-03", "end_date": "2023-06", "is_current": false, "employment_type": "internship", "summary": "Developed MERN stack applications for financial data visualization serving 50+ organizations.", "technologies": ["React", "Node.js", "MongoDB", "Express", "Docker", "Nginx", "Linux", "REST APIs", "RBAC"], "bullet_points": [{"id": "exp.sylvr.bp1", "fact_id": "fact.exp.sylvr.mern_financial", "text": "Developed MERN stack applications for financial data visualization serving 50+ organizations, implementing REST APIs, OTP authentication, and role-based access control.", "metrics": [{"name": "organizations_served", "value": 50, "unit": null, "description": "Served 50+ organizations"}], "skills": ["React", "Node.js", "MongoDB", "Express", "REST APIs", "OTP Auth", "RBAC"], "verified": true}, {"id": "exp.sylvr.bp2", "fact_id": "fact.exp.sylvr.docker_deployment", "text": "Containerized applications using Docker and deployed on Linux servers with Nginx, achieving 98% uptime.", "metrics": [{"name": "uptime", "value": 98, "unit": "percent", "description": "98% uptime achieved"}], "skills": ["Docker", "Nginx", "Linux", "Deployment"], "verified": true}]}, {"id": "exp.iit_patna", "company": "IIT Patna", "role": "Research Intern", "location": "Remote, India", "start_date": "2022-01", "end_date": "2022-05", "is_current": false, "employment_type": "internship", "summary": "Deep learning research involving emotion prediction and psychiatric disorder prediction from BCI signals.", "technologies": ["Python", "Deep Learning", "BCI Signals", "Audio Classification"], "bullet_points": [{"id": "exp.iit_patna.bp1", "fact_id": "fact.exp.iit_patna.deep_learning", "text": "Worked on deep learning research involving emotion prediction, psychiatric disorder prediction from BCI signals, and audio classification.", "metrics": [], "skills": ["Python", "Deep Learning", "Signal Processing"], "verified": true}]}], "projects": [{"id": "proj.tradex", "name": "TradeX", "title": "Realtime Paper Trading Platform", "start_date": "2026-06", "end_date": null, "is_ongoing": true, "status": "active", "badges": ["Live", "Swagger", "API", "UI"], "summary": "Designed and built a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.\\n", "architecture": {"style": "Microservices", "components": ["API Gateway (routing, rate limiting)", "Eureka Service Discovery", "Authentication Service", "Market Data Service", "Portfolio Management Service"]}, "features": ["Self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data", "Real-time price streaming using Kafka and WebSockets", "Sub-millisecond caching with Redis and persistence with PostgreSQL"], "technologies": ["Java", "Spring Boot", "Spring Cloud", "Eureka", "API Gateway", "Kafka", "WebSockets", "Redis", "PostgreSQL", "Docker", "System Design"], "metrics": [{"name": "stocks_etfs_tracked", "value": 15, "unit": null, "description": "15 Indian stocks/ETFs price history generation"}, {"name": "historical_data_span", "value": 10, "unit": "years", "description": "10 years of OHLCV historical data"}], "bullet_points": [{"id": "proj.tradex.bp1", "fact_id": "fact.proj.tradex.microservices", "text": "Designed a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.", "skills": ["Spring Boot", "Microservices", "API Gateway", "Eureka", "System Design"], "verified": true}, {"id": "proj.tradex.bp2", "fact_id": "fact.proj.tradex.kafka_websockets", "text": "Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence.", "skills": ["Kafka", "WebSockets", "Redis", "PostgreSQL", "Data Streaming", "Performance"], "verified": true}]}, {"id": "proj.videoshare", "name": "VideoShare", "title": "Video Sharing & Streaming Platform", "start_date": "2024-12", "end_date": "2025-04", "is_ongoing": false, "status": "completed", "badges": ["Live", "API", "UI"], "summary": "Built a full-featured YouTube-like video sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.\\n", "architecture": {}, "features": ["Video streaming with adaptive playback and chunked uploads", "MongoDB Atlas fuzzy search for instant video and creator discovery", "NSFW content classification pipeline for videos and thumbnail screening", "Containerized deployment on AWS EC2 behind Nginx reverse proxy with 99% uptime"], "technologies": ["Node.js", "React", "MongoDB Atlas", "Express", "Docker", "AWS EC2", "Nginx", "REST APIs", "Authentication"], "metrics": [{"name": "uptime", "value": 99, "unit": "percent", "description": "99% uptime on AWS EC2 with Nginx"}], "bullet_points": [{"id": "proj.videoshare.bp1", "fact_id": "fact.proj.videoshare.full_features", "text": "Built a YouTube-like video-sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.", "skills": ["Node.js", "React", "REST APIs", "Streaming", "Full Stack"], "verified": true}, {"id": "proj.videoshare.bp2", "fact_id": "fact.proj.videoshare.fuzzy_search_ml", "text": "Implemented MongoDB Atlas fuzzy search and an NSFW content classification pipeline for videos and thumbnails; deployed using Docker, AWS EC2, and Nginx with 99% uptime.", "skills": ["MongoDB Atlas", "Fuzzy Search", "Machine Learning", "Docker", "AWS EC2", "Nginx"], "verified": true}]}], "skill_categories": [{"id": "backend", "name": "Backend Development", "skills": [{"name": "Java", "proficiency": "expert", "years_experience": 3.2, "verified": true, "evidence_source": "Accenture, TCS Digital, TradeX, CUSAT", "primary": true}, {"name": "Spring Boot", "proficiency": "expert", "years_experience": 3.0, "verified": true, "evidence_source": "Accenture, TCS Digital, TradeX", "primary": true}, {"name": "Spring MVC", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital", "primary": false}, {"name": "Spring Security", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "Spring Cloud", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "Node.js", "proficiency": "intermediate", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital, Sylvr, VideoShare", "primary": false}, {"name": "REST APIs", "proficiency": "expert", "years_experience": 3.0, "verified": true, "evidence_source": "Accenture, TCS Digital, Sylvr, TradeX, VideoShare", "primary": true}, {"name": "Microservices", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "Accenture, TCS Digital, TradeX", "primary": true}]}, {"id": "distributed_systems", "name": "Distributed Systems & Messaging", "skills": [{"name": "Kafka", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "TradeX", "primary": true}, {"name": "RabbitMQ", "proficiency": "intermediate", "years_experience": 1.0, "verified": true, "evidence_source": "Resume Skills", "primary": false}, {"name": "Redis", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TradeX, TCS Digital (caching)", "primary": true}, {"name": "WebSockets", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "TradeX", "primary": false}, {"name": "API Gateway", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital (Spring Cloud Gateway), TradeX", "primary": true}, {"name": "Eureka", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": false}]}, {"id": "databases", "name": "Databases & ORM", "skills": [{"name": "PostgreSQL", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TradeX, Production systems", "primary": true}, {"name": "MongoDB", "proficiency": "intermediate", "years_experience": 2.0, "verified": true, "evidence_source": "Sylvr, VideoShare", "primary": false}, {"name": "JPA / Hibernate", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "Prisma", "proficiency": "intermediate", "years_experience": 1.0, "verified": true, "evidence_source": "Resume Skills", "primary": false}, {"name": "Mongoose", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "Sylvr, VideoShare", "primary": false}]}, {"id": "frontend", "name": "Frontend Development", "skills": [{"name": "React", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, Sylvr, VideoShare", "primary": true}, {"name": "Next.js", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "Portfolio, Projects", "primary": false}, {"name": "TypeScript", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, Projects", "primary": true}, {"name": "JavaScript", "proficiency": "advanced", "years_experience": 3.0, "verified": true, "evidence_source": "TCS Digital, Sylvr, VideoShare", "primary": false}, {"name": "HTML5 / CSS3", "proficiency": "advanced", "years_experience": 3.0, "verified": true, "evidence_source": "TCS Digital, Sylvr, VideoShare", "primary": false}, {"name": "Chart.js", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "TCS Digital", "primary": false}]}, {"id": "devops", "name": "DevOps & Cloud", "skills": [{"name": "Docker", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "Sylvr, VideoShare, TradeX", "primary": true}, {"name": "AWS EC2", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "VideoShare", "primary": true}, {"name": "Nginx", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "Sylvr, VideoShare", "primary": false}, {"name": "Git / CI/CD", "proficiency": "advanced", "years_experience": 3.0, "verified": true, "evidence_source": "TCS Digital, Accenture, Projects", "primary": false}, {"name": "Linux", "proficiency": "advanced", "years_experience": 3.0, "verified": true, "evidence_source": "Sylvr, VideoShare, Daily dev", "primary": false}]}, {"id": "security", "name": "Security & Auth", "skills": [{"name": "JWT", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, TradeX, VideoShare", "primary": true}, {"name": "OAuth2", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital", "primary": true}, {"name": "Auth0 SSO", "proficiency": "intermediate", "years_experience": 1.5, "verified": true, "evidence_source": "TCS Digital", "primary": false}, {"name": "RBAC", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "Sylvr, TCS Digital", "primary": false}]}, {"id": "core_engineering", "name": "Core Engineering Fundamentals", "skills": [{"name": "System Design", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "High-Level Design (HLD)", "proficiency": "advanced", "years_experience": 2.0, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "Low-Level Design (LLD)", "proficiency": "advanced", "years_experience": 2.5, "verified": true, "evidence_source": "TCS Digital, TradeX", "primary": true}, {"name": "Data Structures & Algorithms (DSA)", "proficiency": "advanced", "years_experience": 3.0, "verified": true, "evidence_source": "CUSAT, Professional work", "primary": true}, {"name": "Object-Oriented Programming (OOP)", "proficiency": "expert", "years_experience": 3.2, "verified": true, "evidence_source": "Java enterprise development", "primary": true}]}], "education": [{"id": "edu.cusat", "institution": "Cochin University of Science and Technology", "degree": "Bachelor of Technology (B.Tech)", "field_of_study": "Electronics and Communication Engineering", "start_date": "2019-06", "end_date": "2023-03", "is_completed": true, "gpa": {"score": 8.91, "scale": 10.0, "display": "8.91 / 10"}, "location": "Kochi, Kerala, India", "highlights": ["Strong foundation in Computer Science fundamentals, DSA, and digital signal processing", "Graduated with First Class with Distinction"]}], "certifications": [{"id": "cert.iit_patna", "name": "Research Internship Certificate in Deep Learning", "issuer": "IIT Patna", "issue_date": "2022-05", "description": "Deep learning research involving emotion prediction and BCI signal processing."}], "variants": [{"id": "java-react-fullstack", "name": "Java + React Full Stack", "is_default": true, "target_roles": ["Full Stack Developer", "Java Full Stack Engineer", "Full Stack Software Engineer"], "tagline": "Full Stack Engineer | Java, Spring Boot & React Ecosystem", "summary_emphasis": "Balanced full-stack delivery with Java/Spring Boot microservices on the backend and React/TypeScript on the frontend.", "priority_skills": ["Java", "Spring Boot", "React", "TypeScript", "REST APIs", "Microservices", "PostgreSQL", "Docker"], "bullet_point_ordering": ["exp.tcs.bp1", "exp.tcs.bp4", "exp.tcs.bp2", "exp.tcs.bp3", "exp.accenture.bp1", "proj.tradex.bp1", "proj.videoshare.bp1"], "primary_project": "proj.tradex", "secondary_project": "proj.videoshare"}, {"id": "java-backend", "name": "Java Backend / Spring Boot", "is_default": false, "target_roles": ["Backend Engineer", "Java Backend Developer", "Spring Boot Developer", "API Engineer"], "tagline": "Backend Software Engineer | Java, Spring Boot & Microservices", "summary_emphasis": "Deep backend engineering focusing on Spring Boot microservices, high-throughput REST APIs, SQL optimization, and clean architecture.", "priority_skills": ["Java", "Spring Boot", "Spring Cloud", "Microservices", "PostgreSQL", "JPA / Hibernate", "Redis", "REST APIs", "JWT / OAuth2"], "bullet_point_ordering": ["exp.tcs.bp3", "exp.tcs.bp2", "exp.tcs.bp4", "exp.accenture.bp1", "proj.tradex.bp1", "proj.tradex.bp2"], "primary_project": "proj.tradex", "secondary_project": "proj.videoshare"}, {"id": "fullstack-engineer", "name": "Full Stack Engineer", "is_default": false, "target_roles": ["Full Stack Software Engineer", "Software Engineer - Full Stack", "Product Engineer"], "tagline": "Full Stack Software Engineer | Modern Web Architecture & Cloud", "summary_emphasis": "End-to-end product development across React, Next.js, Node.js, and Java, containerization with Docker, and cloud deployments.", "priority_skills": ["React", "Next.js", "TypeScript", "Node.js", "Java", "MongoDB", "PostgreSQL", "Docker", "AWS EC2"], "bullet_point_ordering": ["exp.tcs.bp1", "proj.videoshare.bp1", "proj.videoshare.bp2", "exp.sylvr.bp1", "exp.sylvr.bp2", "proj.tradex.bp1"], "primary_project": "proj.videoshare", "secondary_project": "proj.tradex"}, {"id": "backend-distributed", "name": "Backend / Distributed Systems", "is_default": false, "target_roles": ["Distributed Systems Engineer", "Platform Engineer", "High Scale Backend Engineer"], "tagline": "Distributed Systems & Backend Engineer | Kafka, Redis & Microservices", "summary_emphasis": "Distributed backend architecture, event streaming with Kafka, real-time WebSockets, sub-millisecond Redis caching, and fault-tolerant microservices.", "priority_skills": ["Java", "Kafka", "Redis", "WebSockets", "Spring Cloud", "Microservices", "System Design", "PostgreSQL", "Docker"], "bullet_point_ordering": ["proj.tradex.bp2", "proj.tradex.bp1", "exp.tcs.bp4", "exp.tcs.bp3", "exp.tcs.bp2"], "primary_project": "proj.tradex", "secondary_project": "proj.videoshare"}]}	2026-09-22 22:38:29.088919+00	2026-09-22 22:38:29.088919+00
\.


--
-- Data for Name: job_scores; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.job_scores (id, job_id, total_score, role_relevance, core_skills, distributed_systems, experience_fit, location_score, job_quality, llm_score, fit_category, strengths, gaps, risks, recommended_variant, reasoning, created_at, updated_at) FROM stdin;
1	1	86	24	22	11	15	10	4	90	AUTO_PREPARE	["Java", "Spring Boot", "REST / Microservices", "React", "Kafka", "Redis", "Distributed Architecture", "Freshly posted (< 3 days)", "Microservices", "PostgreSQL"]	["PostgreSQL"]	[]	java-react-fullstack	Strong role alignment (24/25) with Shubham's background. High tech stack overlap (22/25) on Java, Spring Boot, REST / Microservices. Distributed systems requirements (11/15) align with TradeX Kafka/Redis experience. Candidate's ~3.2 years matches the target seniority sweet spot. Ideal location fit (Mumbai or preferred tech hub). AI Notes: Strong match with candidate's TradeX distributed systems & Kafka experience.	2026-09-22 22:38:53.344621+00	2026-09-22 22:38:53.344621+00
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.jobs (id, source, source_job_id, url, canonical_url, title, company, locations, remote, experience_min, experience_max, employment_type, salary_min, salary_max, currency, description, skills, required_skills, preferred_skills, posted_at, deadline, application_url, source_type, raw_content_hash, status, fraud_risk, created_at, updated_at) FROM stdin;
1	manual	\N	\N	\N	Senior Software Engineer (Java + React)	Swiggy India	["Mumbai"]	f	3	6	full_time	\N	\N	INR	We are hiring a Senior Software Engineer with strong expertise in Java 17, Spring Boot, Microservices, and React. Experience with high throughput distributed systems, Kafka, and Redis is highly desired. 3+ years experience required.	["Java", "Kafka", "Microservices", "React", "Redis", "Spring Boot"]	["Java", "Kafka", "Microservices", "React", "Redis", "Spring Boot"]	[]	2026-09-22 22:38:36.956392+00	\N	\N	MANUAL	cd474198c264d9659ff94f77d784ad5ebb04a7f5b8c93e71083caee6a71f73f6	active	none	2026-09-22 22:38:36.95556+00	2026-09-22 22:38:36.95556+00
\.


--
-- Data for Name: llm_requests; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.llm_requests (id, provider, model, operation, prompt_version, input_tokens, output_tokens, estimated_cost, duration_ms, status, error_message, job_id, application_id, created_at) FROM stdin;
1	heuristic	rule-based-classifier	classify_job	v1.0	113	140	0	5	success	\N	1	\N	2026-09-22 22:38:37.009497+00
2	heuristic	rule-based-classifier	cover_letter	v1.0	181	140	0	5	success	\N	1	\N	2026-09-22 22:38:53.498156+00
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.notifications (id, user_id, type, title, message, read, action_url, data, created_at) FROM stdin;
1	1	interview_scheduled	Interview Scheduled: System Design & Concurrency	Application #1 moved to Interview stage.	f	/applications?id=1	{"round": "System Design & Concurrency", "scheduled_date": "2026-09-22T22:38:59.832Z", "interviewer": "Priya Sharma (Engineering Director)", "meeting_link": "https://meet.google.com/swiggy-interview"}	2026-09-22 22:38:59.851248+00
\.


--
-- Data for Name: resume_variants; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.resume_variants (id, name, display_name, description, priority_skills, is_default, created_at, updated_at) FROM stdin;
1	java-react-fullstack	Java + React Full Stack	Full stack role with Java backend and React frontend.	\N	t	2026-09-22 01:49:57.750043+00	2026-09-22 01:49:57.750043+00
2	java-backend	Java Backend / Spring Boot	Backend focused role using Java and Spring Boot ecosystem.	\N	f	2026-09-22 01:49:57.750043+00	2026-09-22 01:49:57.750043+00
3	fullstack-engineer	Full Stack Engineer	Generic full stack engineering role.	\N	f	2026-09-22 01:49:57.750043+00	2026-09-22 01:49:57.750043+00
4	backend-distributed	Backend / Distributed Systems	Backend engineering focused on distributed systems and scalability.	\N	f	2026-09-22 01:49:57.750043+00	2026-09-22 01:49:57.750043+00
\.


--
-- Data for Name: resume_versions; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.resume_versions (id, variant_id, job_id, version_number, content_markdown, content_json, file_path_docx, file_path_pdf, keyword_mapping, evidence_mapping, change_diff, confidence_score, unsupported_claims, missing_skills, validation_status, validation_report, created_at, updated_at) FROM stdin;
1	1	1	1	# Shubham Prakash\nMumbai, India | +91-6299783192 | [shubhamprakash681@gmail.com](mailto:shubhamprakash681@gmail.com) | [Portfolio](https://www.shubhamprakash681.in/) | [LinkedIn](https://www.linkedin.com/in/shubham-prakash) | [GitHub](https://github.com/shubhamprakash681)\n\n## Professional Summary\nFull Stack Engineer | Java, Spring Boot & React Ecosystem. ~3.2 years of professional software development experience. Balanced full-stack delivery with Java/Spring Boot microservices on the backend and React/TypeScript on the frontend.\n\n## Technical Skills\n- **Priority Core Focus**: Java, Spring Boot, React, TypeScript, REST APIs, Microservices, PostgreSQL, Docker\n- **Backend Development**: Java, Spring Boot, Spring MVC, Spring Security, Spring Cloud, Node.js, REST APIs, Microservices\n- **Distributed Systems & Messaging**: Kafka, RabbitMQ, Redis, WebSockets, API Gateway, Eureka\n- **Databases & ORM**: PostgreSQL, MongoDB, JPA / Hibernate, Prisma, Mongoose\n- **Frontend Development**: React, Next.js, TypeScript, JavaScript, HTML5 / CSS3, Chart.js\n- **DevOps & Cloud**: Docker, AWS EC2, Nginx, Git / CI/CD, Linux\n- **Security & Auth**: JWT, OAuth2, Auth0 SSO, RBAC\n- **Core Engineering Fundamentals**: System Design, High-Level Design (HLD), Low-Level Design (LLD), Data Structures & Algorithms (DSA), Object-Oriented Programming (OOP)\n\n## Professional Experience\n### Packaged App Development Analyst — **Accenture**\n*Mumbai, India | 2026-04 – Present*\n- Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards. <!-- evidence:fact.exp.accenture.enterprise_apps -->\n\n### Software Developer — **Tata Consultancy Services (TCS Digital)**\n*Mumbai, India | 2023-06 – 2026-04*\n- Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js, following layered architecture and RESTful API principles. <!-- evidence:fact.exp.tcs.microservices -->\n- Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing and service communication, improving scalability and maintainability. <!-- evidence:fact.exp.tcs.spring_cloud -->\n- Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO across 3 enterprise applications, resolving authentication and login issues. <!-- evidence:fact.exp.tcs.auth_migration -->\n- Optimized caching, data structures, and session management, supporting 10,000+ concurrent users with zero data conflicts and achieving up to 80% faster load times; built real-time Chart.js dashboards improving engagement by up to 90%. <!-- evidence:fact.exp.tcs.cache_optimization -->\n\n### Software Engineer Intern — **Sylvr**\n*Remote, India | 2023-03 – 2023-06*\n- Developed MERN stack applications for financial data visualization serving 50+ organizations, implementing REST APIs, OTP authentication, and role-based access control. <!-- evidence:fact.exp.sylvr.mern_financial -->\n- Containerized applications using Docker and deployed on Linux servers with Nginx, achieving 98% uptime. <!-- evidence:fact.exp.sylvr.docker_deployment -->\n\n### Research Intern — **IIT Patna**\n*Remote, India | 2022-01 – 2022-05*\n- Worked on deep learning research involving emotion prediction, psychiatric disorder prediction from BCI signals, and audio classification. <!-- evidence:fact.exp.iit_patna.deep_learning -->\n\n## Key Projects\n### TradeX — *Realtime Paper Trading Platform*\n**Technologies**: Java, Spring Boot, Spring Cloud, Eureka, API Gateway, Kafka, WebSockets, Redis, PostgreSQL, Docker, System Design\n- Designed a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services. <!-- evidence:fact.proj.tradex.microservices -->\n- Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence. <!-- evidence:fact.proj.tradex.kafka_websockets -->\n\n### VideoShare — *Video Sharing & Streaming Platform*\n**Technologies**: Node.js, React, MongoDB Atlas, Express, Docker, AWS EC2, Nginx, REST APIs, Authentication\n- Built a YouTube-like video-sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs. <!-- evidence:fact.proj.videoshare.full_features -->\n- Implemented MongoDB Atlas fuzzy search and an NSFW content classification pipeline for videos and thumbnails; deployed using Docker, AWS EC2, and Nginx with 99% uptime. <!-- evidence:fact.proj.videoshare.fuzzy_search_ml -->\n\n## Education\n### Bachelor of Technology (B.Tech) in Electronics and Communication Engineering\n*Cochin University of Science and Technology, Kochi, Kerala, India | 2019 – 2023 | CGPA: 8.91/10*	{"candidate_name":"Shubham Prakash","location":"Mumbai, India","email":"shubhamprakash681@gmail.com","phone":"+91-6299783192","portfolio_url":"https://www.shubhamprakash681.in/","linkedin_url":"https://www.linkedin.com/in/shubham-prakash","github_url":"https://github.com/shubhamprakash681","variant_id":"java-react-fullstack","variant_name":"Java + React Full Stack","tagline":"Full Stack Engineer | Java, Spring Boot & React Ecosystem","summary":"Full Stack Engineer | Java, Spring Boot & React Ecosystem. ~3.2 years of professional software development experience. Balanced full-stack delivery with Java/Spring Boot microservices on the backend and React/TypeScript on the frontend.","priority_skills":["Java","Spring Boot","React","TypeScript","REST APIs","Microservices","PostgreSQL","Docker"],"categorized_skills":{"Backend Development":["Java","Spring Boot","Spring MVC","Spring Security","Spring Cloud","Node.js","REST APIs","Microservices"],"Distributed Systems & Messaging":["Kafka","RabbitMQ","Redis","WebSockets","API Gateway","Eureka"],"Databases & ORM":["PostgreSQL","MongoDB","JPA / Hibernate","Prisma","Mongoose"],"Frontend Development":["React","Next.js","TypeScript","JavaScript","HTML5 / CSS3","Chart.js"],"DevOps & Cloud":["Docker","AWS EC2","Nginx","Git / CI/CD","Linux"],"Security & Auth":["JWT","OAuth2","Auth0 SSO","RBAC"],"Core Engineering Fundamentals":["System Design","High-Level Design (HLD)","Low-Level Design (LLD)","Data Structures & Algorithms (DSA)","Object-Oriented Programming (OOP)"]},"experiences":[{"id":"exp.accenture","company":"Accenture","role":"Packaged App Development Analyst","location":"Mumbai, India","period":"2026-04 – Present","bullets":[{"id":"exp.accenture.bp1","fact_id":"fact.exp.accenture.enterprise_apps","text":"Developing scalable enterprise applications using Java, Spring Boot microservices, and modern API standards.","skills":["Java","Spring Boot","Microservices","REST APIs"],"relevance_score":3.0}]},{"id":"exp.tcs","company":"Tata Consultancy Services (TCS Digital)","role":"Software Developer","location":"Mumbai, India","period":"2023-06 – 2026-04","bullets":[{"id":"exp.tcs.bp1","fact_id":"fact.exp.tcs.microservices","text":"Developed enterprise applications using Java, Spring Boot Microservices, React, TypeScript, and Node.js, following layered architecture and RESTful API principles.","skills":["Java","Spring Boot","React","TypeScript","Node.js","Microservices","REST APIs"],"relevance_score":4.0},{"id":"exp.tcs.bp3","fact_id":"fact.exp.tcs.spring_cloud","text":"Integrated Spring Cloud Eureka Service Discovery and Spring Cloud Gateway for centralized routing and service communication, improving scalability and maintainability.","skills":["Spring Cloud","Eureka","Spring Cloud Gateway","Microservices","Routing"],"relevance_score":1.0},{"id":"exp.tcs.bp2","fact_id":"fact.exp.tcs.auth_migration","text":"Migrated ArcGIS authentication from frontend to backend and implemented JWT, OAuth2, and Auth0 SSO across 3 enterprise applications, resolving authentication and login issues.","skills":["JWT","OAuth2","Auth0","ArcGIS","SSO","Spring Security"],"relevance_score":0.0},{"id":"exp.tcs.bp4","fact_id":"fact.exp.tcs.cache_optimization","text":"Optimized caching, data structures, and session management, supporting 10,000+ concurrent users with zero data conflicts and achieving up to 80% faster load times; built real-time Chart.js dashboards improving engagement by up to 90%.","skills":["Caching","Session Management","Chart.js","Performance Optimization"],"relevance_score":0.0}]},{"id":"exp.sylvr","company":"Sylvr","role":"Software Engineer Intern","location":"Remote, India","period":"2023-03 – 2023-06","bullets":[{"id":"exp.sylvr.bp1","fact_id":"fact.exp.sylvr.mern_financial","text":"Developed MERN stack applications for financial data visualization serving 50+ organizations, implementing REST APIs, OTP authentication, and role-based access control.","skills":["React","Node.js","MongoDB","Express","REST APIs","OTP Auth","RBAC"],"relevance_score":1.0},{"id":"exp.sylvr.bp2","fact_id":"fact.exp.sylvr.docker_deployment","text":"Containerized applications using Docker and deployed on Linux servers with Nginx, achieving 98% uptime.","skills":["Docker","Nginx","Linux","Deployment"],"relevance_score":0.0}]},{"id":"exp.iit_patna","company":"IIT Patna","role":"Research Intern","location":"Remote, India","period":"2022-01 – 2022-05","bullets":[{"id":"exp.iit_patna.bp1","fact_id":"fact.exp.iit_patna.deep_learning","text":"Worked on deep learning research involving emotion prediction, psychiatric disorder prediction from BCI signals, and audio classification.","skills":["Python","Deep Learning","Signal Processing"],"relevance_score":0.0}]}],"projects":[{"id":"proj.tradex","name":"TradeX","title":"Realtime Paper Trading Platform","summary":"Designed and built a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.","technologies":["Java","Spring Boot","Spring Cloud","Eureka","API Gateway","Kafka","WebSockets","Redis","PostgreSQL","Docker","System Design"],"bullets":[{"id":"proj.tradex.bp1","fact_id":"fact.proj.tradex.microservices","text":"Designed a scalable stock trading platform using Spring Boot microservices with API Gateway, Eureka Service Discovery, authentication, market, and portfolio services.","skills":["Spring Boot","Microservices","API Gateway","Eureka","System Design"],"relevance_score":2.0},{"id":"proj.tradex.bp2","fact_id":"fact.proj.tradex.kafka_websockets","text":"Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence.","skills":["Kafka","WebSockets","Redis","PostgreSQL","Data Streaming","Performance"],"relevance_score":2.0}]},{"id":"proj.videoshare","name":"VideoShare","title":"Video Sharing & Streaming Platform","summary":"Built a full-featured YouTube-like video sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.","technologies":["Node.js","React","MongoDB Atlas","Express","Docker","AWS EC2","Nginx","REST APIs","Authentication"],"bullets":[{"id":"proj.videoshare.bp1","fact_id":"fact.proj.videoshare.full_features","text":"Built a YouTube-like video-sharing platform with authentication, video streaming, likes, comments, subscriptions, playlists, and REST APIs.","skills":["Node.js","React","REST APIs","Streaming","Full Stack"],"relevance_score":1.0},{"id":"proj.videoshare.bp2","fact_id":"fact.proj.videoshare.fuzzy_search_ml","text":"Implemented MongoDB Atlas fuzzy search and an NSFW content classification pipeline for videos and thumbnails; deployed using Docker, AWS EC2, and Nginx with 99% uptime.","skills":["MongoDB Atlas","Fuzzy Search","Machine Learning","Docker","AWS EC2","Nginx"],"relevance_score":0.0}]}],"education":[{"degree":"Bachelor of Technology (B.Tech) in Electronics and Communication Engineering","institution":"Cochin University of Science and Technology, Kochi, Kerala, India","period":"2019 – 2023","grade":"CGPA: 8.91/10"}]}	documents/generated/Resume_Shubham_Prakash_1_v1.docx	documents/generated/Resume_Shubham_Prakash_1_v1.pdf	{"java": true, "spring boot": true, "kafka": true, "react": true, "redis": true, "microservices": true}	{"exp.accenture.bp1": {"fact_id": "fact.exp.accenture.enterprise_apps", "skills": ["Java", "Spring Boot", "Microservices", "REST APIs"], "evidence_ref": "candidate.evidence.exp.accenture.bp1"}, "exp.tcs.bp1": {"fact_id": "fact.exp.tcs.microservices", "skills": ["Java", "Spring Boot", "React", "TypeScript", "Node.js", "Microservices", "REST APIs"], "evidence_ref": "candidate.evidence.exp.tcs.bp1"}, "exp.tcs.bp3": {"fact_id": "fact.exp.tcs.spring_cloud", "skills": ["Spring Cloud", "Eureka", "Spring Cloud Gateway", "Microservices", "Routing"], "evidence_ref": "candidate.evidence.exp.tcs.bp3"}, "exp.tcs.bp2": {"fact_id": "fact.exp.tcs.auth_migration", "skills": ["JWT", "OAuth2", "Auth0", "ArcGIS", "SSO", "Spring Security"], "evidence_ref": "candidate.evidence.exp.tcs.bp2"}, "exp.tcs.bp4": {"fact_id": "fact.exp.tcs.cache_optimization", "skills": ["Caching", "Session Management", "Chart.js", "Performance Optimization"], "evidence_ref": "candidate.evidence.exp.tcs.bp4"}, "exp.sylvr.bp1": {"fact_id": "fact.exp.sylvr.mern_financial", "skills": ["React", "Node.js", "MongoDB", "Express", "REST APIs", "OTP Auth", "RBAC"], "evidence_ref": "candidate.evidence.exp.sylvr.bp1"}, "exp.sylvr.bp2": {"fact_id": "fact.exp.sylvr.docker_deployment", "skills": ["Docker", "Nginx", "Linux", "Deployment"], "evidence_ref": "candidate.evidence.exp.sylvr.bp2"}, "exp.iit_patna.bp1": {"fact_id": "fact.exp.iit_patna.deep_learning", "skills": ["Python", "Deep Learning", "Signal Processing"], "evidence_ref": "candidate.evidence.exp.iit_patna.bp1"}, "proj.tradex.bp1": {"fact_id": "fact.proj.tradex.microservices", "skills": ["Spring Boot", "Microservices", "API Gateway", "Eureka", "System Design"], "evidence_ref": "candidate.evidence.proj.tradex.bp1"}, "proj.tradex.bp2": {"fact_id": "fact.proj.tradex.kafka_websockets", "skills": ["Kafka", "WebSockets", "Redis", "PostgreSQL", "Data Streaming", "Performance"], "evidence_ref": "candidate.evidence.proj.tradex.bp2"}, "proj.videoshare.bp1": {"fact_id": "fact.proj.videoshare.full_features", "skills": ["Node.js", "React", "REST APIs", "Streaming", "Full Stack"], "evidence_ref": "candidate.evidence.proj.videoshare.bp1"}, "proj.videoshare.bp2": {"fact_id": "fact.proj.videoshare.fuzzy_search_ml", "skills": ["MongoDB Atlas", "Fuzzy Search", "Machine Learning", "Docker", "AWS EC2", "Nginx"], "evidence_ref": "candidate.evidence.proj.videoshare.bp2"}}	{"target_company": "Swiggy India", "target_role": "Senior Software Engineer (Java + React)", "variant": "java-react-fullstack", "matched_keywords": ["java", "spring boot", "kafka", "react", "redis", "microservices"], "reordered_bullets_count": 4, "total_experiences": 4, "total_projects": 2, "validation_passed": true}	1	["Mumbai, India | +91-6299783192 | [shubhamprakash681@gmail.com](mailto:shubhamprakash681@gmail.com) | [Portfolio](https://www.shubhamprakash681.in/) | [LinkedIn](https://www.linkedin.com/in/shubham-prakash) | [GitHub](https://github.com/shubhamprakash681)", "Mumbai, India | 2026-04 \\u2013 Present*", "Mumbai, India | 2023-06 \\u2013 2026-04*", "Remote, India | 2023-03 \\u2013 2023-06*", "Remote, India | 2022-01 \\u2013 2022-05*", "Built a self-contained market-data system generating price history for 15 Indian stocks/ETFs across 10 years with OHLCV data; implemented real-time price streaming using Kafka and WebSockets with Redis caching and PostgreSQL persistence. <!-- evidence:fact.proj.tradex.kafka_websockets -->"]	[]	passed	Passed: True. Supported claims: 23, Unsupported: 6. Hallucinated skills: 0.	2026-09-22 22:38:53.378069+00	2026-09-22 22:38:53.378069+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: jobagent
--

COPY public.users (id, email, hashed_password, full_name, is_active, is_superuser, created_at, updated_at) FROM stdin;
1	shubham@example.com	$2b$12$Wnuco2N3FVwNS3DQLrpyDu4PSq9rbk8gkNrDYawo7t30DYsWrjQ4S	Shubham Prakash	t	f	2026-09-22 22:38:28.780107+00	2026-09-22 22:38:28.780107+00
\.


--
-- Name: application_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.application_events_id_seq', 4, true);


--
-- Name: application_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.application_questions_id_seq', 7, true);


--
-- Name: applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.applications_id_seq', 1, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 2, true);


--
-- Name: candidate_evidence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.candidate_evidence_id_seq', 61, true);


--
-- Name: candidate_facts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.candidate_facts_id_seq', 61, true);


--
-- Name: candidate_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.candidate_profiles_id_seq', 1, true);


--
-- Name: job_scores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.job_scores_id_seq', 1, true);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.jobs_id_seq', 1, true);


--
-- Name: llm_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.llm_requests_id_seq', 2, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, true);


--
-- Name: resume_variants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.resume_variants_id_seq', 4, true);


--
-- Name: resume_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.resume_versions_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: jobagent
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: application_events application_events_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_events
    ADD CONSTRAINT application_events_pkey PRIMARY KEY (id);


--
-- Name: application_questions application_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_questions
    ADD CONSTRAINT application_questions_pkey PRIMARY KEY (id);


--
-- Name: applications applications_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: candidate_evidence candidate_evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_evidence
    ADD CONSTRAINT candidate_evidence_pkey PRIMARY KEY (id);


--
-- Name: candidate_facts candidate_facts_fact_id_key; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_facts
    ADD CONSTRAINT candidate_facts_fact_id_key UNIQUE (fact_id);


--
-- Name: candidate_facts candidate_facts_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_facts
    ADD CONSTRAINT candidate_facts_pkey PRIMARY KEY (id);


--
-- Name: candidate_profiles candidate_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_profiles
    ADD CONSTRAINT candidate_profiles_pkey PRIMARY KEY (id);


--
-- Name: candidate_profiles candidate_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_profiles
    ADD CONSTRAINT candidate_profiles_user_id_key UNIQUE (user_id);


--
-- Name: job_scores job_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.job_scores
    ADD CONSTRAINT job_scores_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: llm_requests llm_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.llm_requests
    ADD CONSTRAINT llm_requests_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: resume_variants resume_variants_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_variants
    ADD CONSTRAINT resume_variants_pkey PRIMARY KEY (id);


--
-- Name: resume_versions resume_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_entity; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE INDEX ix_audit_logs_entity ON public.audit_logs USING btree (entity_type, entity_id);


--
-- Name: ix_jobs_company_title; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE INDEX ix_jobs_company_title ON public.jobs USING btree (company, title);


--
-- Name: ix_jobs_source; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE INDEX ix_jobs_source ON public.jobs USING btree (source);


--
-- Name: ix_jobs_status; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE INDEX ix_jobs_status ON public.jobs USING btree (status);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: jobagent
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: application_events application_events_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_events
    ADD CONSTRAINT application_events_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.applications(id);


--
-- Name: application_questions application_questions_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.application_questions
    ADD CONSTRAINT application_questions_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.applications(id);


--
-- Name: applications applications_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidate_profiles(id);


--
-- Name: applications applications_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: applications applications_resume_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.applications
    ADD CONSTRAINT applications_resume_version_id_fkey FOREIGN KEY (resume_version_id) REFERENCES public.resume_versions(id);


--
-- Name: candidate_evidence candidate_evidence_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_evidence
    ADD CONSTRAINT candidate_evidence_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidate_profiles(id);


--
-- Name: candidate_evidence candidate_evidence_fact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_evidence
    ADD CONSTRAINT candidate_evidence_fact_id_fkey FOREIGN KEY (fact_id) REFERENCES public.candidate_facts(id);


--
-- Name: candidate_facts candidate_facts_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_facts
    ADD CONSTRAINT candidate_facts_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidate_profiles(id);


--
-- Name: candidate_profiles candidate_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.candidate_profiles
    ADD CONSTRAINT candidate_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: job_scores job_scores_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.job_scores
    ADD CONSTRAINT job_scores_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: resume_versions resume_versions_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id);


--
-- Name: resume_versions resume_versions_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jobagent
--

ALTER TABLE ONLY public.resume_versions
    ADD CONSTRAINT resume_versions_variant_id_fkey FOREIGN KEY (variant_id) REFERENCES public.resume_variants(id);


--
-- PostgreSQL database dump complete
--

\unrestrict irpkRizAKBr8gB0D52a4aO2DhavOAejWaWixDVcD3X1b44E1qpEx3MmmZeMfaQY

