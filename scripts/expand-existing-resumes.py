# /// script
# dependencies = [
#     "faker>=30.0.0",
# ]
# ///

import argparse
import json
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from faker import Faker


ROOT = Path(__file__).resolve().parent
ASSIGNMENT_MANIFEST = ROOT / "resume_role_assignments.json"

ROLE_DISTRIBUTION = {
    "data_ai_alliance_exec": 42,
    "ai_builder_manager": 93,
    "ai_builder_senior_consultant": 175,
}

ROLE_LABELS = {
    "data_ai_alliance_exec": "Data & AI Alliance Executive",
    "ai_builder_manager": "AI Builder Manager",
    "ai_builder_senior_consultant": "AI Builder Senior Consultant",
}

ROLE_TITLES = {
    "data_ai_alliance_exec": [
        "Data & AI Alliance Lead",
        "Strategic Alliances Manager",
        "Cloud AI Partnership Executive",
        "Ecosystem Growth Lead",
        "AI Go-to-Market Manager",
    ],
    "ai_builder_manager": [
        "AI Delivery Manager",
        "Applied AI Manager",
        "AI Product Engineering Manager",
        "Data & AI Consulting Manager",
        "Generative AI Program Manager",
    ],
    "ai_builder_senior_consultant": [
        "AI Builder Senior Consultant",
        "Applied AI Consultant",
        "Machine Learning Engineer",
        "Data Science Consultant",
        "GenAI Solution Consultant",
    ],
}

ROLE_SUMMARY_FOCUS = {
    "data_ai_alliance_exec": "originating Data and AI revenue, managing partner plans, expanding pipeline with Microsoft, Databricks, Snowflake, and other ISVs, and converting opportunities through executive and partner engagement",
    "ai_builder_manager": "leading internal agentic AI initiatives from AI Lab prototyping through evaluations, productionization, change management, product ownership, demo readiness, governance, and reusable handoff kits",
    "ai_builder_senior_consultant": "building, testing, hardening, and maintaining production-grade agents, plugins, skills, tools, integrations, evaluations, and reusable assets for internal enterprise workflows",
}

ROLE_CATEGORY_WEIGHTS = {
    "data_ai_alliance_exec": {
        "alliance_strategy": 9,
        "partner_ecosystem": 9,
        "executive_stakeholder_management": 9,
        "go_to_market": 8,
        "pipeline_generation": 8,
        "cloud_alliances": 8,
        "hyperscaler_partnerships": 8,
        "commercial_negotiation": 7,
        "market_development": 7,
        "sales_enablement": 7,
        "account_planning": 7,
        "thought_leadership": 6,
        "data_ai_strategy": 6,
        "responsible_ai": 5,
        "industry_solutions": 5,
        "value_case_development": 5,
    },
    "ai_builder_manager": {
        "ai_solution_architecture": 9,
        "delivery_leadership": 9,
        "client_workshops": 8,
        "generative_ai": 8,
        "model_governance": 8,
        "cloud_ai_platforms": 8,
        "product_management": 7,
        "team_leadership": 7,
        "mlops": 7,
        "data_engineering": 7,
        "prompt_engineering": 6,
        "technical_pre_sales": 6,
        "business_case": 6,
        "risk_controls": 6,
        "agile_delivery": 6,
        "stakeholder_management": 6,
    },
    "ai_builder_senior_consultant": {
        "python": 9,
        "machine_learning": 9,
        "generative_ai": 9,
        "data_engineering": 8,
        "llm_applications": 8,
        "prompt_engineering": 8,
        "model_evaluation": 8,
        "apis_microservices": 7,
        "cloud_ai_platforms": 7,
        "sql_analytics": 7,
        "vector_search": 6,
        "mlops": 6,
        "automation": 6,
        "visualization": 5,
        "experimentation": 5,
        "client_workshops": 4,
    },
}

CATEGORIES = {
    "account_planning": {
        "label": "Account planning",
        "skills": ["account strategy", "territory planning", "relationship mapping", "opportunity qualification"],
        "evidence": [
            "Mapped target accounts by buying centre, AI maturity, and renewal timing.",
            "Created account plans connecting technical use cases to executive priorities.",
        ],
    },
    "agile_delivery": {
        "label": "Agile delivery",
        "skills": ["Scrum", "Kanban", "sprint planning", "backlog management"],
        "evidence": [
            "Ran sprint ceremonies and converted discovery notes into prioritized delivery backlogs.",
            "Coordinated analysts, engineers, and client owners through two-week delivery cycles.",
        ],
    },
    "ai_solution_architecture": {
        "label": "AI solution architecture",
        "skills": ["solution architecture", "reference architectures", "system integration", "technical design"],
        "evidence": [
            "Designed AI solution architectures spanning ingestion, model serving, monitoring, and user workflow integration.",
            "Translated ambiguous business needs into deployable technical patterns and delivery milestones.",
        ],
    },
    "alliance_strategy": {
        "label": "Alliance strategy",
        "skills": ["alliance strategy", "partner operating model", "joint business planning", "ecosystem planning"],
        "evidence": [
            "Built joint business plans with partner teams, including routes to market, capability gaps, and quarterly targets.",
            "Defined alliance scorecards covering sourced pipeline, influenced revenue, certification progress, and campaign performance.",
        ],
    },
    "apis_microservices": {
        "label": "APIs and microservices",
        "skills": ["REST APIs", "FastAPI", "microservices", "OpenAPI"],
        "evidence": [
            "Built API services for model inference, batch scoring, and human review queues.",
            "Packaged reusable services with typed contracts, validation, and deployment documentation.",
        ],
    },
    "automation": {
        "label": "Automation",
        "skills": ["workflow automation", "Python automation", "process mining", "RPA integration"],
        "evidence": [
            "Automated recurring data quality checks and exception routing for operations teams.",
            "Reduced manual review effort by codifying intake, enrichment, and approval workflows.",
        ],
    },
    "business_case": {
        "label": "Business case development",
        "skills": ["ROI modelling", "benefits tracking", "investment cases", "cost estimation"],
        "evidence": [
            "Built business cases that connected AI use cases to cost reduction, cycle-time gains, and risk reduction.",
            "Created benefits trackers to compare forecast savings against realized delivery outcomes.",
        ],
    },
    "change_management": {
        "label": "Change management",
        "skills": ["adoption planning", "training design", "communications", "operating model change"],
        "evidence": [
            "Prepared adoption plans, training decks, and change impact assessments for AI-enabled process changes.",
            "Partnered with business leads to define new controls, roles, and escalation paths.",
        ],
    },
    "cloud_ai_platforms": {
        "label": "Cloud AI platforms",
        "skills": ["Azure AI", "AWS", "Google Cloud", "Databricks", "Snowflake"],
        "evidence": [
            "Delivered AI workloads on cloud platforms using managed model endpoints, storage, and observability services.",
            "Compared cloud AI services against client security, latency, and cost constraints.",
        ],
    },
    "cloud_alliances": {
        "label": "Cloud alliances",
        "skills": ["cloud marketplace", "partner funding", "co-sell", "cloud programs"],
        "evidence": [
            "Coordinated partner funding requests, marketplace motions, and joint account pursuits.",
            "Aligned internal teams with cloud partner incentives and qualification requirements.",
        ],
    },
    "commercial_negotiation": {
        "label": "Commercial negotiation",
        "skills": ["commercial strategy", "pricing", "contracting", "deal governance"],
        "evidence": [
            "Supported commercial negotiations by clarifying scope, value drivers, dependencies, and success metrics.",
            "Prepared executive deal summaries covering pricing assumptions, delivery risk, and partner commitments.",
        ],
    },
    "compliance": {
        "label": "Compliance",
        "skills": ["privacy", "regulatory requirements", "audit readiness", "policy interpretation"],
        "evidence": [
            "Documented compliance requirements for data retention, consent, and auditability.",
            "Worked with legal and risk teams to align AI workflows with internal policy requirements.",
        ],
    },
    "client_workshops": {
        "label": "Client workshops",
        "skills": ["facilitation", "discovery workshops", "journey mapping", "executive demos"],
        "evidence": [
            "Facilitated client workshops to identify AI opportunities, feasibility constraints, and implementation paths.",
            "Converted stakeholder interviews into solution options, assumptions, and decision logs.",
        ],
    },
    "data_ai_strategy": {
        "label": "Data and AI strategy",
        "skills": ["AI strategy", "data strategy", "roadmapping", "capability assessment"],
        "evidence": [
            "Developed AI roadmaps that balanced quick-win use cases with platform, governance, and talent needs.",
            "Assessed data and AI maturity across operating model, tooling, controls, and delivery capability.",
        ],
    },
    "data_engineering": {
        "label": "Data engineering",
        "skills": ["ETL", "ELT", "Spark", "dbt", "Airflow", "data modelling"],
        "evidence": [
            "Built governed pipelines for structured and unstructured data used in analytics and AI workflows.",
            "Improved pipeline reliability through validation, lineage notes, and scheduled quality checks.",
        ],
    },
    "delivery_leadership": {
        "label": "Delivery leadership",
        "skills": ["program delivery", "delivery governance", "status reporting", "risk management"],
        "evidence": [
            "Led multi-stream AI delivery plans with milestones, dependencies, risk logs, and executive reporting.",
            "Unblocked delivery teams by clarifying scope, decision owners, and acceptance criteria.",
        ],
    },
    "enterprise_architecture": {
        "label": "Enterprise architecture",
        "skills": ["enterprise architecture", "integration patterns", "platform strategy", "technology roadmaps"],
        "evidence": [
            "Mapped AI solution options to enterprise architecture standards and existing integration patterns.",
            "Created transition roadmaps from prototype architecture to production-ready platforms.",
        ],
    },
    "executive_stakeholder_management": {
        "label": "Executive stakeholder management",
        "skills": ["executive briefings", "board materials", "stakeholder alignment", "decision facilitation"],
        "evidence": [
            "Prepared executive briefings that translated AI capabilities into strategic choices and investment decisions.",
            "Managed senior stakeholder expectations through clear decision points, risks, and value narratives.",
        ],
    },
    "experimentation": {
        "label": "Experimentation",
        "skills": ["A/B testing", "hypothesis design", "experiment tracking", "statistical analysis"],
        "evidence": [
            "Designed experiments to compare model variants, user prompts, and workflow interventions.",
            "Tracked experiment results and documented tradeoffs before production rollout.",
        ],
    },
    "generative_ai": {
        "label": "Generative AI",
        "skills": ["LLMs", "retrieval augmented generation", "agent workflows", "AI copilots"],
        "evidence": [
            "Built generative AI prototypes for knowledge search, summarization, intake triage, and analyst assistance.",
            "Evaluated generative AI use cases against data access, explainability, cost, and operational risk.",
        ],
    },
    "go_to_market": {
        "label": "Go-to-market",
        "skills": ["GTM strategy", "campaign planning", "solution packaging", "sales plays"],
        "evidence": [
            "Packaged AI offerings into sales plays with target personas, triggers, proof points, and demo assets.",
            "Coordinated campaigns across partner, sales, and delivery teams to generate qualified opportunities.",
        ],
    },
    "hyperscaler_partnerships": {
        "label": "Hyperscaler partnerships",
        "skills": ["Microsoft", "Google Cloud", "AWS", "partner field teams"],
        "evidence": [
            "Worked with hyperscaler field teams on joint pursuits, technical validation, and account mapping.",
            "Maintained partner relationships across sales, solution engineering, and marketplace teams.",
        ],
    },
    "industry_solutions": {
        "label": "Industry solutions",
        "skills": ["financial services", "public sector", "retail", "healthcare", "industry accelerators"],
        "evidence": [
            "Adapted AI solution patterns for industry-specific constraints, terminology, and value drivers.",
            "Created industry use-case maps connecting business problems to reusable technical accelerators.",
        ],
    },
    "llm_applications": {
        "label": "LLM applications",
        "skills": ["LangChain", "LlamaIndex", "tool calling", "document AI", "chat applications"],
        "evidence": [
            "Implemented LLM applications with retrieval, guardrails, evaluation data, and user feedback capture.",
            "Integrated language models into business workflows through APIs, queues, and review interfaces.",
        ],
    },
    "machine_learning": {
        "label": "Machine learning",
        "skills": ["scikit-learn", "classification", "forecasting", "feature engineering", "model training"],
        "evidence": [
            "Developed machine learning models for classification, forecasting, prioritization, and anomaly detection.",
            "Improved model performance through feature engineering, validation splits, and error analysis.",
        ],
    },
    "market_development": {
        "label": "Market development",
        "skills": ["market analysis", "competitive positioning", "offer development", "demand generation"],
        "evidence": [
            "Identified market demand themes and translated them into AI solution themes and partner campaigns.",
            "Created competitive positioning notes for AI offerings across platforms and industries.",
        ],
    },
    "mlops": {
        "label": "MLOps",
        "skills": ["model deployment", "CI/CD", "monitoring", "feature stores", "model registry"],
        "evidence": [
            "Implemented MLOps practices for versioning, deployment, monitoring, and retraining workflows.",
            "Defined operational checks for model drift, data freshness, latency, and incident response.",
        ],
    },
    "model_evaluation": {
        "label": "Model evaluation",
        "skills": ["evaluation datasets", "precision and recall", "LLM evaluation", "quality metrics"],
        "evidence": [
            "Built evaluation datasets and scorecards to compare model outputs against business acceptance criteria.",
            "Reviewed model failures and used findings to improve prompts, data retrieval, and guardrails.",
        ],
    },
    "model_governance": {
        "label": "Model governance",
        "skills": ["model risk management", "AI governance", "controls", "documentation"],
        "evidence": [
            "Created model documentation covering purpose, assumptions, limitations, owners, and monitoring controls.",
            "Designed governance checkpoints for use-case intake, validation, approval, and post-launch review.",
        ],
    },
    "partner_ecosystem": {
        "label": "Partner ecosystem",
        "skills": ["ecosystem management", "partner enablement", "channel strategy", "relationship management"],
        "evidence": [
            "Managed partner ecosystem activities across enablement, account planning, pipeline reviews, and campaign execution.",
            "Connected partner capabilities to client needs and internal delivery capacity.",
        ],
    },
    "pipeline_generation": {
        "label": "Pipeline generation",
        "skills": ["pipeline management", "CRM hygiene", "opportunity shaping", "revenue tracking"],
        "evidence": [
            "Built pipeline reports and follow-up cadences to convert AI interest into qualified pursuits.",
            "Tracked sourced and influenced opportunities by stage, partner, industry, and expected value.",
        ],
    },
    "product_management": {
        "label": "Product management",
        "skills": ["product strategy", "roadmaps", "user stories", "acceptance criteria"],
        "evidence": [
            "Owned product backlogs for AI-enabled tools, balancing user needs, risk controls, and delivery capacity.",
            "Defined MVP scope, acceptance criteria, and release plans for AI products.",
        ],
    },
    "prompt_engineering": {
        "label": "Prompt engineering",
        "skills": ["prompt design", "system prompts", "few-shot examples", "prompt evaluation"],
        "evidence": [
            "Designed prompt templates with examples, constraints, and evaluation checks for repeatable AI outputs.",
            "Reduced output variance through structured prompts, retrieval context, and failure-case testing.",
        ],
    },
    "python": {
        "label": "Python",
        "skills": ["Python", "pandas", "NumPy", "FastAPI", "pytest"],
        "evidence": [
            "Built Python services and notebooks for ingestion, modelling, evaluation, and reporting.",
            "Wrote tested Python utilities for data validation, feature generation, and API integration.",
        ],
    },
    "responsible_ai": {
        "label": "Responsible AI",
        "skills": ["responsible AI", "fairness", "transparency", "human oversight", "AI ethics"],
        "evidence": [
            "Assessed responsible AI considerations including fairness, explainability, privacy, and human oversight.",
            "Defined guardrails and review steps for higher-risk AI use cases.",
        ],
    },
    "risk_controls": {
        "label": "Risk controls",
        "skills": ["risk assessment", "controls design", "issue management", "quality assurance"],
        "evidence": [
            "Designed controls for data access, model approval, output review, and exception handling.",
            "Maintained risk registers and mitigation plans for AI delivery initiatives.",
        ],
    },
    "sales_enablement": {
        "label": "Sales enablement",
        "skills": ["sales enablement", "pitch decks", "battlecards", "demo scripts"],
        "evidence": [
            "Created enablement material including pitch decks, discovery questions, demo scripts, and objection handling notes.",
            "Trained client-facing teams on AI use cases, partner offers, and qualification criteria.",
        ],
    },
    "security": {
        "label": "Security",
        "skills": ["identity access management", "secure SDLC", "data protection", "threat modelling"],
        "evidence": [
            "Reviewed AI architecture for identity, access, logging, secrets management, and data protection needs.",
            "Worked with security teams to close architecture and deployment risks before launch.",
        ],
    },
    "sql_analytics": {
        "label": "SQL and analytics",
        "skills": ["SQL", "analytics engineering", "data profiling", "KPI design"],
        "evidence": [
            "Used SQL to profile source data, define metrics, and validate model input quality.",
            "Built analytics views that made AI outputs traceable to source records and business KPIs.",
        ],
    },
    "stakeholder_management": {
        "label": "Stakeholder management",
        "skills": ["stakeholder engagement", "status updates", "decision logs", "workshop follow-up"],
        "evidence": [
            "Kept client, product, data, and risk stakeholders aligned through status updates and decision logs.",
            "Resolved delivery ambiguity by documenting assumptions, owners, and next steps.",
        ],
    },
    "team_leadership": {
        "label": "Team leadership",
        "skills": ["coaching", "resource planning", "performance feedback", "technical leadership"],
        "evidence": [
            "Led mixed teams of consultants, engineers, and analysts through discovery, build, and rollout phases.",
            "Coached junior team members on consulting communication, solution design, and delivery discipline.",
        ],
    },
    "technical_pre_sales": {
        "label": "Technical pre-sales",
        "skills": ["solution demos", "technical discovery", "proposal support", "estimation"],
        "evidence": [
            "Supported technical discovery and proposal shaping with architecture options, assumptions, and effort estimates.",
            "Built demo narratives that connected AI capabilities to client processes and value drivers.",
        ],
    },
    "thought_leadership": {
        "label": "Thought leadership",
        "skills": ["white papers", "webinars", "executive narratives", "market insights"],
        "evidence": [
            "Authored thought-leadership material on AI adoption patterns, governance, and value realization.",
            "Presented market insights and practical AI adoption lessons to senior business audiences.",
        ],
    },
    "value_case_development": {
        "label": "Value case development",
        "skills": ["value cases", "benefits quantification", "KPI alignment", "measurement plans"],
        "evidence": [
            "Quantified AI value cases using baseline costs, expected adoption, quality impact, and time savings.",
            "Defined measurement plans to track whether AI initiatives delivered intended business outcomes.",
        ],
    },
    "vector_search": {
        "label": "Vector search",
        "skills": ["embeddings", "semantic search", "vector databases", "retrieval tuning"],
        "evidence": [
            "Built vector-search prototypes for policy, knowledge-base, and case-document retrieval.",
            "Tuned chunking, metadata filters, and ranking logic to improve retrieval precision.",
        ],
    },
    "visualization": {
        "label": "Visualization",
        "skills": ["Power BI", "Tableau", "dashboard design", "data storytelling"],
        "evidence": [
            "Created dashboards for adoption, model performance, pipeline health, and executive reporting.",
            "Presented analytical findings through concise visuals, narrative summaries, and recommended actions.",
        ],
    },
}

EXTRA_CATEGORY_WEIGHTS = {
    "data_ai_alliance_exec": {
        "change_management": 4,
        "compliance": 4,
        "security": 3,
        "enterprise_architecture": 3,
    },
    "ai_builder_manager": {
        "change_management": 5,
        "compliance": 5,
        "security": 5,
        "enterprise_architecture": 5,
        "visualization": 3,
    },
    "ai_builder_senior_consultant": {
        "security": 4,
        "compliance": 3,
        "enterprise_architecture": 3,
        "responsible_ai": 3,
    },
}

DEGREES = [
    "Bachelor of Computer Science",
    "Bachelor of Engineering",
    "Bachelor of Commerce",
    "Bachelor of Mathematics",
    "Master of Data Science",
    "Master of Business Administration",
    "Master of Information Systems",
    "Master of Applied Computing",
]

CERTIFICATIONS = [
    "Microsoft Certified: Azure AI Engineer Associate",
    "AWS Certified Machine Learning - Specialty",
    "Google Cloud Professional Machine Learning Engineer",
    "Databricks Machine Learning Associate",
    "Certified ScrumMaster",
    "Prosci Change Management Certification",
    "TOGAF Foundation",
    "IAPP Certified Information Privacy Professional",
    "Project Management Professional",
    "SnowPro Core Certification",
]

ROLE_POSTING_ANALYSIS = {
    "data_ai_alliance_exec": {
        "url": "https://careers.kpmg.ca/professionals/jobs/30989?lang=en-us",
        "requirement_groups": [
            "new business origination in Data and AI",
            "robust revenue pipeline creation and expansion",
            "Microsoft, Databricks, Snowflake, and ISV partner management",
            "partner plans and revenue origination strategies",
            "partner field sales, channel, and customer lead generation",
            "sales funnel qualification and opportunity nurturing",
            "cross-functional business plan execution",
            "KPMG Data and AI solution evangelism and value propositions",
            "partner customer-base adoption and revenue expansion",
            "preferred-vendor go-to-market positioning",
            "CRM analytics, pipeline metrics, forecasting, and senior reporting",
            "complex contract negotiation and legal liaison",
            "enterprise Data and AI platform technical acumen",
            "Canadian market knowledge",
            "global alliance and sales account management",
        ],
    },
    "ai_builder_manager": {
        "url": "https://careers.kpmg.ca/professionals/jobs/32544?lang=en-us",
        "requirement_groups": [
            "internal agentic AI initiative delivery leadership",
            "complex problem ownership from experimentation to validated outcomes",
            "production-grade agents, plugins, skills, and tools",
            "full build lifecycle ownership from AI Lab prototype to production",
            "evaluations, productionization, change management, and product ownership",
            "cloud platform and engineering partnership",
            "code quality, reliability, security, and scalability",
            "demo readiness, narrative, artifacts, and demo safety checks",
            "reusable demos, kits, and handoff materials",
            "risk, governance, trust, and responsible AI by design",
            "technical leadership and coaching for Consultants and Senior Consultants",
            "one-pagers, replication kits, and AI literacy artifacts",
            "enterprise fluency across operations, technology, and design",
            "workflow and operating-model redesign with human-AI collaboration",
            "ambiguity leadership, trade-off judgment, and scalable adoption",
        ],
    },
    "ai_builder_senior_consultant": {
        "url": "https://careers.kpmg.ca/professionals/jobs/32538?lang=en-us",
        "requirement_groups": [
            "hands-on agentic AI building for well-scoped internal problems",
            "rapid experimentation, prototyping, and AI Lab initiatives",
            "production-grade agents, plugins, skills, and tools",
            "build, test, harden, and maintain solutions",
            "full lifecycle ownership from prototype to Internal Transformation productionization",
            "production systems, evaluations, enterprise platform integrations, and data sources",
            "reusable skills, components, and tools contributed to a shared AI stack",
            "highest-leverage internal agent builds",
            "demos, reusable assets, and builder community contribution",
            "enterprise fluency and practical pain-point identification",
            "workflow design with human-AI handoffs and autonomy boundaries",
            "builder mindset across code, configuration, low-code, APIs, and orchestration",
            "ambiguity, assumptions, testing, learning, and iteration",
            "risk, governance, ethics, and trust as design constraints",
            "prototype portfolio and practical build-case readiness",
        ],
    },
}

FIT_TIER_LABELS = {
    "top_fit": "top 5-10 percent fit",
    "qualified_fit": "qualified fit",
    "adjacent_fit": "adjacent or transferable fit",
    "poor_fit": "poor fit",
}

ROLE_CORE_CATEGORIES = {
    "data_ai_alliance_exec": [
        "alliance_strategy",
        "partner_ecosystem",
        "executive_stakeholder_management",
        "go_to_market",
        "pipeline_generation",
        "cloud_alliances",
        "hyperscaler_partnerships",
        "sales_enablement",
        "account_planning",
        "market_development",
    ],
    "ai_builder_manager": [
        "ai_solution_architecture",
        "delivery_leadership",
        "client_workshops",
        "generative_ai",
        "model_governance",
        "cloud_ai_platforms",
        "product_management",
        "team_leadership",
        "mlops",
        "data_engineering",
    ],
    "ai_builder_senior_consultant": [
        "python",
        "machine_learning",
        "generative_ai",
        "data_engineering",
        "llm_applications",
        "prompt_engineering",
        "model_evaluation",
        "apis_microservices",
        "cloud_ai_platforms",
        "sql_analytics",
    ],
}

ROLE_ADJACENT_CATEGORIES = {
    "data_ai_alliance_exec": [
        "business_case",
        "stakeholder_management",
        "change_management",
        "product_management",
        "visualization",
        "industry_solutions",
        "data_ai_strategy",
        "technical_pre_sales",
        "value_case_development",
    ],
    "ai_builder_manager": [
        "stakeholder_management",
        "business_case",
        "change_management",
        "enterprise_architecture",
        "visualization",
        "technical_pre_sales",
        "risk_controls",
        "automation",
        "data_ai_strategy",
    ],
    "ai_builder_senior_consultant": [
        "automation",
        "visualization",
        "experimentation",
        "sql_analytics",
        "security",
        "compliance",
        "client_workshops",
        "responsible_ai",
        "business_case",
    ],
}

RELEVANT_DEGREES_BY_ROLE = {
    "data_ai_alliance_exec": [
        "Master of Business Administration, Technology Strategy",
        "Bachelor of Commerce, Information Systems",
        "Master of Management Analytics",
        "Bachelor of Business Administration, Digital Strategy",
    ],
    "ai_builder_manager": [
        "Master of Data Science",
        "Master of Business Administration, Analytics",
        "Bachelor of Engineering, Software Systems",
        "Master of Information Systems",
    ],
    "ai_builder_senior_consultant": [
        "Bachelor of Computer Science",
        "Bachelor of Engineering, Computer Engineering",
        "Master of Applied Computing",
        "Master of Data Science",
    ],
}

ADJACENT_DEGREES = [
    "Bachelor of Business Administration",
    "Bachelor of Economics",
    "Bachelor of Mathematics",
    "Bachelor of Science, Statistics",
    "Diploma in Business Analytics",
    "Graduate Certificate in Project Management",
]

POOR_FIT_BACKGROUNDS = [
    {
        "domain": "retail_operations",
        "summary": "retail operations and store team coordination",
        "titles": ["Store Manager", "Retail Supervisor", "Inventory Coordinator", "Customer Experience Lead"],
        "skills": ["staff scheduling", "inventory counts", "point-of-sale systems", "customer service", "merchandising", "cash handling"],
        "duties": [
            "Scheduled store associates, handled opening and closing tasks, and resolved customer escalations.",
            "Monitored inventory accuracy and coordinated seasonal merchandising changes.",
            "Prepared daily sales summaries and coached associates on service standards.",
        ],
        "degrees": ["Diploma in Retail Management", "Bachelor of Arts, Communications", "Certificate in Customer Service"],
    },
    {
        "domain": "general_accounting",
        "summary": "bookkeeping, month-end support, and finance administration",
        "titles": ["Accounting Coordinator", "Bookkeeper", "Accounts Payable Specialist", "Payroll Assistant"],
        "skills": ["QuickBooks", "invoice processing", "bank reconciliation", "Excel", "expense reports", "payroll support"],
        "duties": [
            "Processed vendor invoices, reconciled bank statements, and prepared month-end support schedules.",
            "Maintained accounts payable records and followed up on missing approvals.",
            "Created spreadsheet trackers for expense exceptions and payroll adjustments.",
        ],
        "degrees": ["Diploma in Accounting", "Bachelor of Commerce, Accounting", "Certificate in Payroll Administration"],
    },
    {
        "domain": "human_resources",
        "summary": "human resources coordination and employee program administration",
        "titles": ["HR Coordinator", "Recruiting Assistant", "Learning Coordinator", "People Operations Associate"],
        "skills": ["employee onboarding", "ATS administration", "training logistics", "policy updates", "HRIS data entry"],
        "duties": [
            "Coordinated onboarding tasks, interview schedules, and employee training logistics.",
            "Updated employee records and prepared recurring HR operations reports.",
            "Supported policy communication and maintained learning attendance records.",
        ],
        "degrees": ["Bachelor of Human Resources Management", "Diploma in Office Administration", "Certificate in Workplace Learning"],
    },
    {
        "domain": "events_marketing",
        "summary": "event logistics, campaign coordination, and brand support",
        "titles": ["Event Coordinator", "Marketing Assistant", "Community Outreach Coordinator", "Brand Coordinator"],
        "skills": ["event logistics", "vendor coordination", "social media calendars", "Canva", "email campaigns", "budget tracking"],
        "duties": [
            "Coordinated vendors, run sheets, registration lists, and post-event feedback summaries.",
            "Prepared campaign calendars and social media assets for local programs.",
            "Tracked event budgets, invoices, and attendee communications.",
        ],
        "degrees": ["Bachelor of Arts, Marketing", "Diploma in Event Management", "Certificate in Digital Media"],
    },
    {
        "domain": "customer_support",
        "summary": "front-line support operations and service quality tracking",
        "titles": ["Customer Support Specialist", "Call Centre Team Lead", "Service Desk Coordinator", "Client Care Representative"],
        "skills": ["Zendesk", "case triage", "service scripts", "quality monitoring", "customer escalation", "knowledge base updates"],
        "duties": [
            "Handled customer cases, escalated billing issues, and documented recurring service questions.",
            "Maintained knowledge-base articles and reviewed sample interactions for quality coaching.",
            "Prepared weekly ticket summaries for service managers.",
        ],
        "degrees": ["Diploma in Business Administration", "Bachelor of Arts, Sociology", "Certificate in Service Excellence"],
    },
]

ADJACENT_TITLES = {
    "data_ai_alliance_exec": ["Business Development Manager", "Partner Program Manager", "Account Strategy Lead"],
    "ai_builder_manager": ["Technology Project Manager", "Analytics Delivery Lead", "Product Owner"],
    "ai_builder_senior_consultant": ["Business Analyst", "Analytics Consultant", "Automation Specialist"],
}

POSTING_SPECIFIC_CATEGORIES = {
    "agentic_ai_delivery": {
        "label": "Agentic AI delivery",
        "skills": ["agentic AI", "autonomous agents", "agent workflows", "multi-agent systems"],
        "evidence": [
            "Designed and delivered agentic AI workflows that moved beyond experimentation into daily business operations.",
            "Built agent patterns that combined planning, tool use, memory, human review, and escalation boundaries.",
        ],
    },
    "internal_ai_lab": {
        "label": "AI Lab experimentation",
        "skills": ["AI Lab prototyping", "rapid experimentation", "frontier models", "applied research"],
        "evidence": [
            "Used secure AI Lab environments to test frontier-model use cases before broader internal release.",
            "Turned applied research ideas into working demos, validation notes, and production handoff plans.",
        ],
    },
    "agent_plugins_skills_tools": {
        "label": "Agents, plugins, skills, and tools",
        "skills": ["agent tools", "plugin design", "skills", "tool calling", "orchestration"],
        "evidence": [
            "Built agents, plugins, skills, and tools that automated internal workflow steps with clear ownership boundaries.",
            "Packaged reusable agent capabilities so later builds could start from tested components.",
        ],
    },
    "approved_ai_stack": {
        "label": "Approved AI and engineering stack",
        "skills": ["approved AI stack", "engineering standards", "secure platforms", "platform constraints"],
        "evidence": [
            "Delivered AI builds inside approved enterprise technology stacks and platform guardrails.",
            "Aligned prototypes with engineering standards so validated concepts could move into production paths.",
        ],
    },
    "full_build_lifecycle": {
        "label": "Full AI build lifecycle",
        "skills": ["prototype lifecycle", "production handoff", "lifecycle ownership", "solution maintenance"],
        "evidence": [
            "Owned the build lifecycle from problem framing and lab prototype through productionization and maintenance planning.",
            "Connected discovery, build, evaluation, deployment, adoption, and continuous improvement into one delivery plan.",
        ],
    },
    "validated_outcomes": {
        "label": "Validated outcomes",
        "skills": ["outcome validation", "success metrics", "benefit measurement", "adoption metrics"],
        "evidence": [
            "Defined validation metrics before build work started and used them to decide whether prototypes should scale.",
            "Tracked adoption, quality, cycle time, and user feedback to prove whether an agentic workflow worked.",
        ],
    },
    "evaluation_design": {
        "label": "Evaluation design",
        "skills": ["eval harnesses", "test sets", "agent evaluation", "quality gates"],
        "evidence": [
            "Designed evaluation harnesses for agent outputs, workflow completion, safety checks, and regression testing.",
            "Built test cases and scoring rubrics to compare agent behavior across prompt, tool, and model changes.",
        ],
    },
    "productionization": {
        "label": "Productionization",
        "skills": ["production readiness", "release planning", "deployment controls", "operational support"],
        "evidence": [
            "Moved prototypes into production by defining release criteria, support paths, monitoring, and fallback procedures.",
            "Coordinated production readiness reviews across product, engineering, security, and business teams.",
        ],
    },
    "internal_transformation": {
        "label": "Internal Transformation production path",
        "skills": ["internal transformation", "operating model change", "enterprise rollout", "adoption planning"],
        "evidence": [
            "Partnered with internal transformation teams to convert lab concepts into scalable enterprise workflows.",
            "Planned rollout activities across business units, operating model updates, communications, and adoption tracking.",
        ],
    },
    "cloud_engineering_partnership": {
        "label": "Cloud and engineering partnership",
        "skills": ["cloud engineering", "platform teams", "DevOps collaboration", "secure deployment"],
        "evidence": [
            "Worked with cloud platform and engineering teams on deployment design, reliability, observability, and support.",
            "Converted prototype requirements into engineering tickets, architecture notes, and platform dependency plans.",
        ],
    },
    "code_quality_reliability": {
        "label": "Code quality and reliability",
        "skills": ["code review", "automated testing", "reliability engineering", "maintainability"],
        "evidence": [
            "Reviewed code quality, test coverage, error handling, and operational readiness before internal release.",
            "Improved reliability by adding structured logging, retries, validation, and documented failure modes.",
        ],
    },
    "security_scalability": {
        "label": "Security and scalability",
        "skills": ["secure architecture", "scalability", "identity controls", "data protection"],
        "evidence": [
            "Designed AI workflows with access controls, data protection, audit trails, and scalable service patterns.",
            "Resolved security and scalability issues before expanding prototypes to broader user groups.",
        ],
    },
    "demo_readiness": {
        "label": "Demo readiness",
        "skills": ["demo narrative", "showcase artifacts", "executive demos", "demo rehearsal"],
        "evidence": [
            "Prepared demo narratives, artifacts, and walkthroughs that made agentic AI capabilities easy to evaluate.",
            "Maintained demo readiness with current sample data, risk notes, and clear user journey scripts.",
        ],
    },
    "demo_safety_governance": {
        "label": "Demo safety and governance checks",
        "skills": ["demo safety", "governance checks", "risk review", "safe showcase"],
        "evidence": [
            "Ran demo safety checks covering data exposure, prompt behavior, user permissions, and governance assumptions.",
            "Documented demo constraints and risk controls before showing prototypes to business stakeholders.",
        ],
    },
    "reusable_demos_kits": {
        "label": "Reusable demos, kits, and handoff materials",
        "skills": ["handoff kits", "replication kits", "demo packaging", "implementation playbooks"],
        "evidence": [
            "Packaged validated prototypes into reusable demos, replication kits, and handoff material for downstream teams.",
            "Created implementation notes so other teams could reproduce agent patterns without restarting discovery.",
        ],
    },
    "ai_literacy_artifacts": {
        "label": "AI literacy artifacts",
        "skills": ["AI literacy", "one-pagers", "learning artifacts", "internal enablement"],
        "evidence": [
            "Captured build learnings in one-pagers, AI literacy notes, and reusable explanation artifacts.",
            "Turned technical decisions into plain-language materials for business teams and new builders.",
        ],
    },
    "builder_team_coaching": {
        "label": "Builder team coaching",
        "skills": ["builder coaching", "technical direction", "work review", "team development"],
        "evidence": [
            "Set direction for Consultants and Senior Consultants, reviewed work, and coached builders through trade-offs.",
            "Helped builders improve delivery quality by pairing on design choices, evaluation plans, and demo preparation.",
        ],
    },
    "service_line_leadership": {
        "label": "Service line leadership engagement",
        "skills": ["service line leaders", "senior manager alignment", "executive engagement", "internal stakeholders"],
        "evidence": [
            "Worked with service line leaders and senior managers to shape internal AI experimentation priorities.",
            "Translated leadership priorities into problem statements, prototype scope, and adoption plans.",
        ],
    },
    "enterprise_operations_fluency": {
        "label": "Enterprise operations fluency",
        "skills": ["enterprise operations", "process fluency", "regulated enterprise", "operating model"],
        "evidence": [
            "Mapped how enterprise functions operate today and identified where autonomous agents could improve delivery.",
            "Balanced strategy, technology, controls, and execution in complex regulated environments.",
        ],
    },
    "workflow_redesign": {
        "label": "Workflow and operating-model redesign",
        "skills": ["workflow redesign", "operating model design", "process decomposition", "decision systems"],
        "evidence": [
            "Redesigned multi-step workflows and decision systems around human-AI collaboration and measurable outcomes.",
            "Separated work into agent-owned, human-owned, and review-gated steps before build execution.",
        ],
    },
    "human_ai_collaboration": {
        "label": "Human-AI collaboration",
        "skills": ["human-AI handoffs", "review loops", "decision boundaries", "autonomy design"],
        "evidence": [
            "Designed human-AI handoffs with clear decision boundaries, review points, and escalation paths.",
            "Defined appropriate autonomy levels based on risk, workflow maturity, and user confidence.",
        ],
    },
    "builder_mindset": {
        "label": "Builder mindset",
        "skills": ["build mindset", "rapid prototyping", "hands-on execution", "working systems"],
        "evidence": [
            "Moved from concept to working system quickly, using code, configuration, APIs, and orchestration tools.",
            "Demonstrated ideas through functioning prototypes rather than static recommendations.",
        ],
    },
    "low_code_api_orchestration": {
        "label": "Low-code, API, and orchestration tools",
        "skills": ["low-code platforms", "API integration", "workflow orchestration", "configuration"],
        "evidence": [
            "Combined low-code tools, APIs, and orchestration logic to create usable enterprise workflow automation.",
            "Integrated AI components with existing platforms and data sources through pragmatic API patterns.",
        ],
    },
    "ambiguity_execution": {
        "label": "Ambiguity and execution",
        "skills": ["ambiguity", "structured assumptions", "iteration", "delivery momentum"],
        "evidence": [
            "Led ambiguous problem spaces by making reasonable assumptions, testing quickly, and keeping teams aligned.",
            "Maintained delivery momentum while problem definitions, stakeholders, and constraints evolved.",
        ],
    },
    "tradeoff_judgment": {
        "label": "Trade-off judgment",
        "skills": ["trade-off decisions", "structured thinking", "delivery judgment", "prioritization"],
        "evidence": [
            "Made informed trade-offs between build speed, reliability, governance, and user value.",
            "Coached teams to document assumptions and decide when to prototype, harden, pause, or scale.",
        ],
    },
    "prototype_portfolio": {
        "label": "Prototype portfolio",
        "skills": ["prototype portfolio", "GitHub demos", "demo write-ups", "build case"],
        "evidence": [
            "Maintained a prototype portfolio with build notes, demo assets, and explanations of design decisions.",
            "Prepared build-case submissions that showed practical problem solving, AI use, and original thinking.",
        ],
    },
    "builder_community": {
        "label": "Builder community contribution",
        "skills": ["builder community", "shared assets", "reuse", "community demos"],
        "evidence": [
            "Contributed demos, reusable assets, and implementation lessons back to the builder community.",
            "Helped peers reuse patterns by documenting components, limits, and setup steps.",
        ],
    },
    "revenue_origination": {
        "label": "Revenue origination",
        "skills": ["new business origination", "revenue growth", "deal sourcing", "opportunity creation"],
        "evidence": [
            "Originated new Data and AI opportunities by connecting partner capabilities with client business priorities.",
            "Created revenue growth plans with specific account targets, partner motions, and qualification criteria.",
        ],
    },
    "partner_pipeline_creation": {
        "label": "Partner pipeline creation",
        "skills": ["pipeline creation", "pipeline expansion", "opportunity management", "quarterly targets"],
        "evidence": [
            "Built and expanded partner-led pipeline through campaign follow-up, account mapping, and sales funnel discipline.",
            "Managed opportunities against quarterly targets with clear next steps, stage movement, and executive visibility.",
        ],
    },
    "microsoft_databricks_snowflake": {
        "label": "Microsoft, Databricks, and Snowflake partnerships",
        "skills": ["Microsoft", "Databricks", "Snowflake", "ISV partnerships"],
        "evidence": [
            "Coordinated opportunities with Microsoft, Databricks, Snowflake, and other ISV partner teams.",
            "Positioned Data and AI solutions using partner platform strengths and joint value propositions.",
        ],
    },
    "partner_field_sales": {
        "label": "Partner field sales collaboration",
        "skills": ["field sales", "partner channels", "co-selling", "lead sharing"],
        "evidence": [
            "Collaborated with partner field sales teams, channels, and customers to generate and qualify leads.",
            "Built account pursuit cadences with partner sellers, internal account teams, and solution leads.",
        ],
    },
    "sales_funnel_qualification": {
        "label": "Sales funnel qualification",
        "skills": ["lead qualification", "sales funnel", "nurturing", "pipeline tracking"],
        "evidence": [
            "Moved leads through the funnel by clarifying business need, decision process, timing, and value case.",
            "Nurtured early-stage opportunities with targeted follow-up, stakeholder mapping, and solution education.",
        ],
    },
    "strategic_partner_plans": {
        "label": "Strategic partner plans",
        "skills": ["partner plans", "revenue strategy", "joint business planning", "execution governance"],
        "evidence": [
            "Led partner plans and revenue origination strategies that prioritized pipeline growth and market adoption.",
            "Executed strategic business plans with cross-functional teams focused on opportunity identification.",
        ],
    },
    "solution_evangelism": {
        "label": "Data and AI solution evangelism",
        "skills": ["solution evangelism", "value proposition", "market awareness", "executive storytelling"],
        "evidence": [
            "Evangelized Data and AI solution value propositions to build awareness with partners and potential customers.",
            "Created executive narratives that linked emerging AI capabilities to measurable client outcomes.",
        ],
    },
    "business_reviews": {
        "label": "Partner and internal business reviews",
        "skills": ["business reviews", "pipeline reporting", "partner governance", "senior reporting"],
        "evidence": [
            "Prepared partner and internal business reviews covering pipeline movement, forecast risks, and action owners.",
            "Reported progress to senior management with clear metrics, blockers, and revenue implications.",
        ],
    },
    "crm_forecasting": {
        "label": "CRM analytics and revenue forecasting",
        "skills": ["CRM", "forecasting", "pipeline metrics", "analytics tools"],
        "evidence": [
            "Used CRM systems and analytics tools to track pipeline metrics, forecast revenue, and report progress.",
            "Improved forecast quality by standardizing opportunity stages, next actions, and partner attribution.",
        ],
    },
    "contract_legal_liaison": {
        "label": "Contract negotiation and legal liaison",
        "skills": ["contract negotiation", "legal liaison", "commercial terms", "deal governance"],
        "evidence": [
            "Participated in complex contract negotiations and coordinated legal review for new business deals.",
            "Clarified commercial terms, scope assumptions, data obligations, and partner responsibilities.",
        ],
    },
    "platform_technical_acumen": {
        "label": "Enterprise Data and AI platform acumen",
        "skills": ["enterprise data platforms", "AI platforms", "cloud data warehousing", "SaaS"],
        "evidence": [
            "Explained enterprise Data and AI platform capabilities to business, partner, and sales stakeholders.",
            "Connected platform features to client adoption paths, integration needs, and commercial value.",
        ],
    },
    "canadian_ai_market": {
        "label": "Canadian Data and AI market knowledge",
        "skills": ["Canadian market", "industry demand", "regional accounts", "market positioning"],
        "evidence": [
            "Built market views for Canadian Data and AI demand across industries, regions, and partner ecosystems.",
            "Adjusted pursuit strategy based on Canadian buying patterns, platform adoption, and account maturity.",
        ],
    },
    "joint_value_propositions": {
        "label": "Joint value propositions",
        "skills": ["joint value propositions", "solution packaging", "customer adoption", "offer positioning"],
        "evidence": [
            "Developed joint value propositions with partners that clarified business outcomes, platform fit, and delivery model.",
            "Positioned Data and AI services as preferred go-to-market offerings for partner-led customer conversations.",
        ],
    },
    "global_alliance_sales": {
        "label": "Global alliance and sales account management",
        "skills": ["global alliance", "sales account management", "partner governance", "executive relationships"],
        "evidence": [
            "Managed alliance and sales account relationships across internal, external, and partner leadership groups.",
            "Aligned global alliance guidance with local account planning and Canadian revenue priorities.",
        ],
    },
}

CATEGORIES.update(POSTING_SPECIFIC_CATEGORIES)

ROLE_CATEGORY_WEIGHTS["data_ai_alliance_exec"].update(
    {
        "revenue_origination": 12,
        "partner_pipeline_creation": 12,
        "microsoft_databricks_snowflake": 12,
        "partner_field_sales": 11,
        "sales_funnel_qualification": 11,
        "strategic_partner_plans": 11,
        "solution_evangelism": 10,
        "business_reviews": 10,
        "crm_forecasting": 10,
        "contract_legal_liaison": 9,
        "platform_technical_acumen": 9,
        "canadian_ai_market": 8,
        "joint_value_propositions": 10,
        "global_alliance_sales": 8,
    }
)

ROLE_CATEGORY_WEIGHTS["ai_builder_manager"].update(
    {
        "agentic_ai_delivery": 12,
        "internal_ai_lab": 10,
        "agent_plugins_skills_tools": 12,
        "approved_ai_stack": 9,
        "full_build_lifecycle": 12,
        "validated_outcomes": 11,
        "evaluation_design": 11,
        "productionization": 12,
        "internal_transformation": 11,
        "cloud_engineering_partnership": 10,
        "code_quality_reliability": 10,
        "security_scalability": 10,
        "demo_readiness": 9,
        "demo_safety_governance": 9,
        "reusable_demos_kits": 9,
        "ai_literacy_artifacts": 8,
        "builder_team_coaching": 11,
        "service_line_leadership": 10,
        "enterprise_operations_fluency": 10,
        "workflow_redesign": 11,
        "human_ai_collaboration": 10,
        "builder_mindset": 10,
        "low_code_api_orchestration": 9,
        "ambiguity_execution": 9,
        "tradeoff_judgment": 9,
    }
)

ROLE_CATEGORY_WEIGHTS["ai_builder_senior_consultant"].update(
    {
        "agentic_ai_delivery": 12,
        "internal_ai_lab": 11,
        "agent_plugins_skills_tools": 12,
        "approved_ai_stack": 10,
        "full_build_lifecycle": 11,
        "validated_outcomes": 9,
        "evaluation_design": 11,
        "productionization": 10,
        "internal_transformation": 8,
        "cloud_engineering_partnership": 9,
        "code_quality_reliability": 9,
        "security_scalability": 9,
        "reusable_demos_kits": 9,
        "human_ai_collaboration": 10,
        "builder_mindset": 12,
        "low_code_api_orchestration": 10,
        "prototype_portfolio": 11,
        "builder_community": 8,
    }
)

ROLE_CORE_CATEGORIES["data_ai_alliance_exec"] = [
    "revenue_origination",
    "partner_pipeline_creation",
    "microsoft_databricks_snowflake",
    "partner_field_sales",
    "sales_funnel_qualification",
    "strategic_partner_plans",
    "solution_evangelism",
    "business_reviews",
    "crm_forecasting",
    "contract_legal_liaison",
    "platform_technical_acumen",
    "joint_value_propositions",
]

ROLE_CORE_CATEGORIES["ai_builder_manager"] = [
    "agentic_ai_delivery",
    "agent_plugins_skills_tools",
    "full_build_lifecycle",
    "validated_outcomes",
    "evaluation_design",
    "productionization",
    "internal_transformation",
    "cloud_engineering_partnership",
    "code_quality_reliability",
    "security_scalability",
    "demo_readiness",
    "demo_safety_governance",
    "reusable_demos_kits",
    "builder_team_coaching",
    "workflow_redesign",
]

ROLE_CORE_CATEGORIES["ai_builder_senior_consultant"] = [
    "agentic_ai_delivery",
    "internal_ai_lab",
    "agent_plugins_skills_tools",
    "approved_ai_stack",
    "full_build_lifecycle",
    "evaluation_design",
    "productionization",
    "cloud_engineering_partnership",
    "code_quality_reliability",
    "security_scalability",
    "human_ai_collaboration",
    "prototype_portfolio",
]

ROLE_ADJACENT_CATEGORIES["data_ai_alliance_exec"] = [
    "canadian_ai_market",
    "global_alliance_sales",
    "partner_ecosystem",
    "commercial_negotiation",
    "account_planning",
    "market_development",
    "business_case",
    "stakeholder_management",
    "technical_pre_sales",
    "value_case_development",
]

ROLE_ADJACENT_CATEGORIES["ai_builder_manager"] = [
    "service_line_leadership",
    "enterprise_operations_fluency",
    "human_ai_collaboration",
    "builder_mindset",
    "low_code_api_orchestration",
    "ambiguity_execution",
    "tradeoff_judgment",
    "ai_literacy_artifacts",
    "product_management",
    "change_management",
    "responsible_ai",
]

ROLE_ADJACENT_CATEGORIES["ai_builder_senior_consultant"] = [
    "validated_outcomes",
    "internal_transformation",
    "reusable_demos_kits",
    "builder_community",
    "builder_mindset",
    "low_code_api_orchestration",
    "ambiguity_execution",
    "tradeoff_judgment",
    "automation",
    "client_workshops",
]


@dataclass(frozen=True)
class ResumeFile:
    folder: Path
    path: Path
    slug: str
    name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Expand existing assignment-folder resumes for three KPMG-style Data and AI roles."
    )
    parser.add_argument("--apply", action="store_true", help="Rewrite resume txt files. Omit for dry-run only.")
    parser.add_argument("--seed", type=int, default=31042, help="Deterministic random seed.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ASSIGNMENT_MANIFEST,
        help="Where to write the role/category assignment manifest.",
    )
    return parser.parse_args()


def discover_resumes() -> list[ResumeFile]:
    resumes: list[ResumeFile] = []
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or folder.name == "synthetic_resumes":
            continue
        txts = sorted(folder.glob("*_resume.txt"))
        if len(txts) != 1:
            continue
        slug = folder.name
        name = " ".join(part.capitalize() for part in slug.split("_"))
        resumes.append(ResumeFile(folder=folder, path=txts[0], slug=slug, name=name))
    if len(resumes) != sum(ROLE_DISTRIBUTION.values()):
        raise RuntimeError(f"Expected 310 assignment resumes, found {len(resumes)}.")
    return resumes


def weighted_sample(keys_to_weights: dict[str, int], count: int, rng: random.Random) -> list[str]:
    pool = dict(keys_to_weights)
    selected: list[str] = []
    while pool and len(selected) < count:
        keys = list(pool)
        weights = [pool[key] for key in keys]
        picked = rng.choices(keys, weights=weights, k=1)[0]
        selected.append(picked)
        del pool[picked]
    return selected


def role_weights(role: str) -> dict[str, int]:
    weights = {key: 1 for key in CATEGORIES}
    weights.update(ROLE_CATEGORY_WEIGHTS[role])
    weights.update(EXTRA_CATEGORY_WEIGHTS.get(role, {}))
    return weights


def tier_counts_for_role(role_count: int) -> dict[str, int]:
    top = max(1, round(role_count * 0.085))
    qualified = round(role_count * 0.32)
    adjacent = round(role_count * 0.40)
    poor = role_count - top - qualified - adjacent
    return {
        "top_fit": top,
        "qualified_fit": qualified,
        "adjacent_fit": adjacent,
        "poor_fit": poor,
    }


def assign_candidate_profiles(resumes: list[ResumeFile], rng: random.Random) -> dict[str, dict[str, str]]:
    shuffled = resumes[:]
    rng.shuffle(shuffled)
    assignments: dict[str, dict[str, str]] = {}
    offset = 0
    for role, role_count in ROLE_DISTRIBUTION.items():
        role_resumes = shuffled[offset : offset + role_count]
        offset += role_count
        cursor = 0
        for tier, tier_count in tier_counts_for_role(role_count).items():
            for resume in role_resumes[cursor : cursor + tier_count]:
                assignments[resume.slug] = {"role": role, "fit_tier": tier}
            cursor += tier_count
    return assignments


def category_count_for_tier(tier: str, rng: random.Random) -> int:
    if tier == "top_fit":
        return rng.randint(18, 24)
    if tier == "qualified_fit":
        return rng.randint(12, 18)
    if tier == "adjacent_fit":
        return rng.randint(6, 11)
    return rng.randint(1, 4)


def years_for_profile(role: str, tier: str, rng: random.Random) -> int:
    ranges = {
        "data_ai_alliance_exec": {
            "top_fit": (11, 17),
            "qualified_fit": (8, 13),
            "adjacent_fit": (5, 10),
            "poor_fit": (2, 8),
        },
        "ai_builder_manager": {
            "top_fit": (9, 15),
            "qualified_fit": (6, 11),
            "adjacent_fit": (4, 9),
            "poor_fit": (1, 6),
        },
        "ai_builder_senior_consultant": {
            "top_fit": (6, 10),
            "qualified_fit": (4, 8),
            "adjacent_fit": (2, 6),
            "poor_fit": (1, 5),
        },
    }
    low, high = ranges[role][tier]
    return rng.randint(low, high)


def alignment_score_for_tier(tier: str, rng: random.Random) -> int:
    ranges = {
        "top_fit": (91, 99),
        "qualified_fit": (72, 89),
        "adjacent_fit": (42, 68),
        "poor_fit": (8, 35),
    }
    low, high = ranges[tier]
    return rng.randint(low, high)


def dedupe(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def categories_for_profile(role: str, tier: str, rng: random.Random) -> list[str]:
    count = category_count_for_tier(tier, rng)
    core = ROLE_CORE_CATEGORIES[role]
    adjacent = ROLE_ADJACENT_CATEGORIES[role]
    selected: list[str] = []

    if tier == "top_fit":
        selected.extend(rng.sample(core, min(len(core), rng.randint(8, 10))))
        weights = role_weights(role)
    elif tier == "qualified_fit":
        selected.extend(rng.sample(core, min(len(core), rng.randint(5, 8))))
        weights = role_weights(role)
    elif tier == "adjacent_fit":
        selected.extend(rng.sample(core, min(len(core), rng.randint(1, 3))))
        selected.extend(rng.sample(adjacent, min(len(adjacent), rng.randint(3, 6))))
        weights = {key: 1 for key in CATEGORIES}
        for key in adjacent:
            weights[key] = 7
        for key in core:
            weights[key] = 2
    else:
        selected.extend(rng.sample(adjacent, min(len(adjacent), rng.randint(0, 2))))
        weights = {key: 1 for key in adjacent}
        for key in ["stakeholder_management", "visualization", "business_case", "sql_analytics", "change_management"]:
            weights[key] = 3

    selected = dedupe(selected)
    if len(selected) < count:
        selected.extend(weighted_sample(weights, count - len(selected), rng))
    return dedupe(selected)[:count]


def city_from_existing(text: str, fake: Faker) -> str:
    for line in text.splitlines():
        if "|" in line and "," in line:
            return line.split("|", 1)[0].strip()
    return f"{fake.city()}, {fake.state_abbr()}"


def email_for_name(name: str, fake: Faker) -> str:
    safe = re.sub(r"[^a-z.]", "", name.lower().replace(" ", "."))
    return f"{safe}@{fake.free_email_domain()}"


def format_list(items: Iterable[str]) -> str:
    return ", ".join(items)


def profile_title(role: str, tier: str, rng: random.Random) -> str:
    if tier in {"top_fit", "qualified_fit"}:
        return rng.choice(ROLE_TITLES[role])
    return rng.choice(ADJACENT_TITLES[role])


def category_skills(categories: list[str], rng: random.Random, tier: str) -> list[str]:
    skills: list[str] = []
    for key in categories:
        skills.extend(CATEGORIES[key]["skills"])
    if tier == "top_fit":
        target = rng.randint(26, 36)
    elif tier == "qualified_fit":
        target = rng.randint(20, 30)
    else:
        target = rng.randint(12, 20)
    rng.shuffle(skills)
    return dedupe(skills)[:target]


def relevant_certifications(role: str, tier: str, rng: random.Random) -> list[str]:
    role_cert_priority = {
        "data_ai_alliance_exec": [
            "Project Management Professional",
            "Prosci Change Management Certification",
            "Microsoft Certified: Azure AI Engineer Associate",
            "TOGAF Foundation",
        ],
        "ai_builder_manager": [
            "Microsoft Certified: Azure AI Engineer Associate",
            "Project Management Professional",
            "Certified ScrumMaster",
            "Databricks Machine Learning Associate",
        ],
        "ai_builder_senior_consultant": [
            "Microsoft Certified: Azure AI Engineer Associate",
            "AWS Certified Machine Learning - Specialty",
            "Google Cloud Professional Machine Learning Engineer",
            "Databricks Machine Learning Associate",
        ],
    }
    if tier == "top_fit":
        count = rng.randint(3, 5)
    elif tier == "qualified_fit":
        count = rng.randint(2, 4)
    else:
        count = rng.randint(1, 2)
    pool = dedupe(role_cert_priority[role] + CERTIFICATIONS)
    return rng.sample(pool, min(count, len(pool)))


def education_for_profile(role: str, tier: str, years: int, fake: Faker, rng: random.Random) -> tuple[str, str, int]:
    if tier in {"top_fit", "qualified_fit"}:
        degree = rng.choice(RELEVANT_DEGREES_BY_ROLE[role])
    else:
        degree = rng.choice(ADJACENT_DEGREES)
    school = f"{fake.city()} {rng.choice(['University', 'Institute of Technology', 'School of Business', 'Polytechnic'])}"
    grad_year = max(2006, 2026 - years - rng.randint(2, 6))
    return degree, school, grad_year


def outcome_metric(role: str, tier: str, rng: random.Random) -> str:
    if role == "data_ai_alliance_exec":
        metrics = [
            f"supported ${rng.randint(4, 28)}M in qualified alliance pipeline",
            f"increased partner-sourced opportunities by {rng.randint(18, 55)}%",
            f"enabled {rng.randint(6, 24)} joint account pursuits",
            f"reduced pursuit cycle time by {rng.randint(10, 32)}%",
        ]
    elif role == "ai_builder_manager":
        metrics = [
            f"reduced prototype-to-production cycle time by {rng.randint(15, 40)}%",
            f"coached a team of {rng.randint(4, 14)} consultants and engineers",
            f"improved delivery predictability by {rng.randint(12, 34)}%",
            f"delivered ${rng.randint(2, 14)}M in AI program value cases",
        ]
    else:
        to_days = rng.randint(1, 3)
        metrics = [
            f"improved model quality by {rng.randint(8, 27)}%",
            f"reduced manual analysis effort by {rng.randint(18, 48)}%",
            f"processed {rng.randint(2, 40)}M records through reusable pipelines",
            f"cut evaluation turnaround from {rng.randint(4, 12)} days to {to_days} {'day' if to_days == 1 else 'days'}",
        ]
    if tier == "adjacent_fit":
        metrics.extend(
            [
                f"standardized reporting for {rng.randint(3, 10)} stakeholder groups",
                f"reduced operational handoffs by {rng.randint(8, 20)}%",
            ]
        )
    return rng.choice(metrics)


def job_periods(start_year: int, job_count: int, rng: random.Random) -> list[tuple[int, str]]:
    start_year = min(start_year, 2026 - job_count)
    remaining_years = max(job_count, 2026 - start_year)
    periods: list[tuple[int, str]] = []
    current_year = start_year
    for job_idx in range(job_count):
        if job_idx == job_count - 1:
            periods.append((current_year, "Present"))
            break
        jobs_left_after = job_count - job_idx - 1
        max_duration = max(1, min(4, remaining_years - jobs_left_after))
        duration = rng.randint(1, max_duration)
        end_year = current_year + duration
        periods.append((current_year, str(end_year)))
        current_year = end_year
        remaining_years -= duration
    return periods


def role_article(role_label: str) -> str:
    if role_label.startswith("AI"):
        return "an"
    return "a"


def role_specific_artifacts(
    resume: ResumeFile,
    role: str,
    tier: str,
    categories: list[str],
    rng: random.Random,
) -> tuple[str, list[str]]:
    if role == "data_ai_alliance_exec":
        line_count = 5 if tier == "top_fit" else 4 if tier == "qualified_fit" else 3
        lines = [
            f"Built a Data and AI partner plan covering Microsoft, Databricks, Snowflake, target accounts, quarterly pipeline goals, and field-sales actions.",
            f"Maintained CRM forecast views for sourced and influenced pipeline, with stage hygiene, next actions, and partner attribution.",
            f"Led partner and internal business reviews that connected lead generation, funnel movement, forecast risk, and revenue enablement actions.",
            f"Shaped joint value propositions for enterprise Data and AI services using platform capabilities, adoption paths, and commercial value drivers.",
            f"Supported contract and legal review by clarifying solution scope, partner responsibilities, data considerations, and commercial assumptions.",
            f"Evangelized Data and AI solution narratives to senior decision-makers and partner customer teams across Canadian enterprise accounts.",
        ]
        rng.shuffle(lines)
        return "REVENUE AND ALLIANCE IMPACT", lines[:line_count]

    portfolio_url = f"https://github.com/{resume.slug.replace('_', '-')}/agentic-ai-builds"
    if role == "ai_builder_manager":
        line_count = 6 if tier == "top_fit" else 5 if tier == "qualified_fit" else 3
        lines = [
            f"Prototype portfolio: {portfolio_url}",
            "Led an AI Lab pipeline from problem statement through prototype, evaluation harness, productionization plan, change management, and product ownership.",
            "Packaged validated agents into demo narratives, safety notes, reusable kits, one-pagers, and handoff material for downstream internal teams.",
            "Partnered with cloud platform and engineering teams on code quality, reliability, security, scalability, observability, and release criteria.",
            "Coached Consultants and Senior Consultants by setting technical direction, reviewing agent designs, and documenting trade-off decisions.",
            "Defined human-AI handoffs, autonomy boundaries, governance checkpoints, and adoption metrics for regulated enterprise workflows.",
            "Prepared demo readiness artifacts covering user journey, risk assumptions, data boundaries, prompt behavior, and stakeholder narrative.",
        ]
        rest = lines[1:]
        rng.shuffle(rest)
        return "AGENTIC AI BUILD LEADERSHIP", [lines[0]] + rest[: line_count - 1]

    line_count = 5 if tier == "top_fit" else 4 if tier == "qualified_fit" else 3
    lines = [
        f"Prototype portfolio: {portfolio_url}",
        "Built, tested, and hardened agents, plugins, skills, and tools connected to enterprise platforms and internal data sources.",
        "Contributed reusable components and implementation notes back to a shared AI stack so later builds could start further ahead.",
        "Designed evaluations for tool use, workflow completion, output quality, safety constraints, and regression checks.",
        "Moved well-scoped prototypes through Internal Transformation handoff with deployment notes, support assumptions, and monitoring checks.",
        "Documented build decisions, assumptions, user handoffs, autonomy limits, and responsible AI considerations for prototype case review.",
        "Created demo assets for the builder community, including setup notes, sample data, walkthrough scripts, and known limitations.",
    ]
    rest = lines[1:]
    rng.shuffle(rest)
    return "AGENTIC AI BUILD PORTFOLIO", [lines[0]] + rest[: line_count - 1]


def build_fit_resume(
    resume: ResumeFile,
    role: str,
    tier: str,
    categories: list[str],
    fake: Faker,
    rng: random.Random,
) -> str:
    existing_text = resume.path.read_text(encoding="utf-8")
    city_state = city_from_existing(existing_text, fake)
    phone = fake.phone_number()
    email = email_for_name(resume.name, fake)
    years = years_for_profile(role, tier, rng)
    labels = [CATEGORIES[key]["label"] for key in categories]
    selected_skills = category_skills(categories, rng, tier)
    certifications = relevant_certifications(role, tier, rng)
    degree, school, grad_year = education_for_profile(role, tier, years, fake, rng)
    start_year = max(2008, 2026 - years)
    role_label = ROLE_LABELS[role]
    focus = ROLE_SUMMARY_FOCUS[role]
    if tier == "top_fit":
        summary = (
            f"{resume.name} is {role_article(role_label)} {role_label} with {years}+ years of direct Data and AI experience, "
            f"including {format_list(labels[:6])}. The profile shows repeated ownership of strategy, delivery, "
            f"stakeholder outcomes, and measurable value realization."
        )
    elif tier == "qualified_fit":
        summary = (
            f"{resume.name} is a data and technology consulting professional with {years}+ years of experience in {focus}. "
            f"Strongest evidence areas include {format_list(labels[:5])}, with practical delivery and stakeholder results."
        )
    else:
        summary = (
            f"{resume.name} is a business and analytics professional with {years}+ years of transferable experience related to "
            f"{format_list(labels[:4])}. The profile shows partial alignment to Data and AI work, with gaps in deeper role ownership."
        )

    text: list[str] = []
    text.append("=========================================")
    text.append(resume.name.upper())
    text.append(f"{city_state} | {phone} | {email}")
    text.append("=========================================")
    text.append("")
    text.append("PROFESSIONAL SUMMARY")
    text.append(summary)
    text.append("")
    text.append("AREAS OF EXPERTISE")
    expertise_count = 14 if tier == "top_fit" else 10 if tier == "qualified_fit" else 7
    for label in labels[: min(expertise_count, len(labels))]:
        text.append(f"  * {label}")
    text.append("")
    text.append("CORE SKILLS")
    text.append(format_list(selected_skills))
    text.append("")
    text.append("PROFESSIONAL EXPERIENCE")

    job_count = 4 if tier == "top_fit" else 3
    bullet_count = 6 if tier == "top_fit" else 5 if tier == "qualified_fit" else 4
    for job_idx, (period_start, end_label) in enumerate(job_periods(start_year, job_count, rng)):
        title = profile_title(role, tier, rng)
        company = fake.company()
        text.append(f"{title} - {company}")
        text.append(f"{period_start} - {end_label}")

        duty_categories = categories[job_idx * 4 : job_idx * 4 + 6]
        if len(duty_categories) < 4:
            duty_categories = rng.sample(categories, min(4, len(categories)))
        for key in duty_categories[:bullet_count]:
            evidence = rng.choice(CATEGORIES[key]["evidence"])
            metric = outcome_metric(role, tier, rng)
            text.append(f"  * {evidence} Outcome: {metric}.")
        text.append("")

    text.append("SELECTED ACHIEVEMENTS")
    achievement_count = 5 if tier == "top_fit" else 3 if tier == "qualified_fit" else 2
    for key in rng.sample(categories, min(achievement_count, len(categories))):
        text.append(f"  * {rng.choice(CATEGORIES[key]['evidence'])} Result: {outcome_metric(role, tier, rng)}.")
    text.append("")

    text.append("SELECTED PROJECTS")
    project_count = 4 if tier == "top_fit" else 3 if tier == "qualified_fit" else 2
    for _ in range(project_count):
        project_categories = rng.sample(categories, min(rng.randint(3, 5), len(categories)))
        project_labels = [CATEGORIES[key]["label"] for key in project_categories]
        text.append(
            f"  * Led {rng.choice(['discovery', 'prototype', 'implementation', 'enablement', 'roadmap'])} "
            f"work across {format_list(project_labels)}."
        )
    text.append("")

    section_title, section_lines = role_specific_artifacts(resume, role, tier, categories, rng)
    text.append(section_title)
    for line in section_lines:
        text.append(f"  * {line}")
    text.append("")

    text.append("TOOLS, PLATFORMS, AND METHODS")
    text.append(format_list(selected_skills[:14] + certifications[:2]))
    text.append("")
    text.append("CERTIFICATIONS")
    for cert in certifications:
        text.append(f"  * {cert}")
    text.append("")
    text.append("EDUCATION")
    text.append(f"{degree}")
    text.append(f"{school} - Class of {grad_year}")
    text.append("")
    return "\n".join(text)


def build_poor_fit_resume(
    resume: ResumeFile,
    role: str,
    categories: list[str],
    fake: Faker,
    rng: random.Random,
) -> str:
    existing_text = resume.path.read_text(encoding="utf-8")
    city_state = city_from_existing(existing_text, fake)
    phone = fake.phone_number()
    email = email_for_name(resume.name, fake)
    background = rng.choice(POOR_FIT_BACKGROUNDS)
    years = years_for_profile(role, "poor_fit", rng)
    school = f"{fake.city()} {rng.choice(['College', 'University', 'Career Institute', 'Business School'])}"
    grad_year = max(2010, 2026 - years - rng.randint(1, 4))
    skills = background["skills"][:]
    rng.shuffle(skills)
    weak_ai_exposure = rng.sample(
        ["basic Excel dashboards", "introductory analytics reports", "vendor CRM reports", "basic spreadsheet automation"],
        rng.randint(1, 2),
    )
    labels = [CATEGORIES[key]["label"] for key in categories]

    text: list[str] = []
    text.append("=========================================")
    text.append(resume.name.upper())
    text.append(f"{city_state} | {phone} | {email}")
    text.append("=========================================")
    text.append("")
    text.append("PROFESSIONAL SUMMARY")
    text.append(
        f"{resume.name} is an operations professional with {years}+ years of experience in {background['summary']}. "
        f"The profile includes limited exposure to {format_list(weak_ai_exposure)} but does not show direct ownership of AI delivery, "
        f"alliance strategy, machine learning engineering, or cloud AI implementation."
    )
    text.append("")
    text.append("AREAS OF EXPERIENCE")
    for skill in skills[:6]:
        text.append(f"  * {skill}")
    if labels:
        text.append(f"  * Basic familiarity with {format_list(labels[:2])}")
    text.append("")
    text.append("CORE SKILLS")
    text.append(format_list(skills + weak_ai_exposure))
    text.append("")
    text.append("PROFESSIONAL EXPERIENCE")

    job_count = rng.randint(2, 3)
    job_start = max(2012, 2026 - years)
    for job_idx, (period_start, end_label) in enumerate(job_periods(job_start, job_count, rng)):
        title = rng.choice(background["titles"])
        company = fake.company()
        text.append(f"{title} - {company}")
        text.append(f"{period_start} - {end_label}")
        for duty in rng.sample(background["duties"], min(3, len(background["duties"]))):
            text.append(f"  * {duty}")
        if categories and rng.random() < 0.35:
            key = rng.choice(categories)
            text.append(f"  * Assisted with a small reporting task loosely related to {CATEGORIES[key]['label'].lower()}.")
        text.append("")

    text.append("SELECTED ACHIEVEMENTS")
    text.append(f"  * Improved administrative follow-up time by {rng.randint(5, 18)}% through clearer trackers and handoff notes.")
    text.append(f"  * Maintained service or operations records with fewer than {rng.randint(2, 6)} recurring monthly exceptions.")
    text.append("")
    text.append("TOOLS AND METHODS")
    text.append(format_list(skills[:5] + weak_ai_exposure))
    text.append("")
    text.append("EDUCATION")
    text.append(rng.choice(background["degrees"]))
    text.append(f"{school} - Class of {grad_year}")
    text.append("")
    return "\n".join(text)


def build_resume(
    resume: ResumeFile,
    role: str,
    tier: str,
    categories: list[str],
    fake: Faker,
    rng: random.Random,
) -> str:
    if tier == "poor_fit":
        return build_poor_fit_resume(resume, role, categories, fake, rng)
    return build_fit_resume(resume, role, tier, categories, fake, rng)


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    fake = Faker("en_CA")
    Faker.seed(args.seed)

    resumes = discover_resumes()
    candidate_profiles = assign_candidate_profiles(resumes, rng)
    manifest: list[dict[str, object]] = []

    for resume in resumes:
        profile = candidate_profiles[resume.slug]
        role = profile["role"]
        tier = profile["fit_tier"]
        categories = categories_for_profile(role, tier, rng)
        score = alignment_score_for_tier(tier, rng)
        manifest.append(
            {
                "folder": resume.folder.name,
                "resume": resume.path.name,
                "target_role": role,
                "target_role_label": ROLE_LABELS[role],
                "fit_tier": tier,
                "fit_tier_label": FIT_TIER_LABELS[tier],
                "alignment_score": score,
                "categories": categories,
                "category_labels": [CATEGORIES[key]["label"] for key in categories],
                "posting_url": ROLE_POSTING_ANALYSIS[role]["url"],
                "posting_requirement_groups": ROLE_POSTING_ANALYSIS[role]["requirement_groups"],
            }
        )
        if args.apply:
            resume.path.write_text(build_resume(resume, role, tier, categories, fake, rng), encoding="utf-8")

    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Resumes discovered: {len(resumes)}")
    for role, count in ROLE_DISTRIBUTION.items():
        actual = sum(1 for item in manifest if item["target_role"] == role)
        print(f"{ROLE_LABELS[role]}: {actual}/{count}")
        for tier, tier_count in tier_counts_for_role(count).items():
            actual_tier = sum(1 for item in manifest if item["target_role"] == role and item["fit_tier"] == tier)
            print(f"  {FIT_TIER_LABELS[tier]}: {actual_tier}/{tier_count}")
    print(f"Categories available: {len(CATEGORIES)}")
    print(f"Manifest written: {args.manifest}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to rewrite existing resume txt files.")


if __name__ == "__main__":
    main()
