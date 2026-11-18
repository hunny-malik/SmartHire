# SmartHire: AI-Powered Resume Analysis, Skill Gap Mapping, Job Matching & Bilingual Voice Mock Interview System

---

## Executive Project Overview: SmartHire

**SmartHire** is an end-to-end, intelligent career advancement and interview preparation platform designed to streamline the transition from candidate resume evaluation to job placement. By combining Natural Language Processing (NLP), Large Language Models (LLMs), dynamic web aggregation, and speech recognition technology, SmartHire provides job seekers with a personalized, data-driven career copilot.

### Core Capabilities & Feature Architecture

```
+-----------------------------------------------------------------------------------+
|                                   SMARTHIRE                                       |
+-------------------+-------------------+--------------------+----------------------+
| 1. Resume Parsing | 2. Job Matching   | 3. Skill Gap       | 4. AI Mock           |
|    & Role Finder  |    & Links        |    Analysis        |    Interview         |
| - Text extraction | - Top 5-10 live   | - Target profile   | - Dual Mode (Voice & |
| - Entity extraction|   job postings    |   comparison       |   Text)              |
| - Top job role    | - LinkedIn, Indeed| - Actionable path  | - Bilingual: English |
|   identification  |   & Google Jobs   |   (e.g., LLD->SDE) |   & Hindi / Hinglish |
+-------------------+-------------------+--------------------+----------------------+
```

1. **Resume Upload & AI Analysis**: 
   Users upload their resume (PDF/DOCX). The system parses structured and unstructured details (skills, experience, education, projects) using NLP models to analyze the candidate's core competencies and identify top matching job titles.

2. **Top 5 to 10 Live Job Openings**:
   Based on the candidate's profile vector, SmartHire queries job aggregators (LinkedIn, Indeed, Google Jobs) to fetch real-time, relevant job listing links tailored to the candidate's location and experience level.

3. **Skill Gap Analysis & Career Transition Planning**:
   The platform compares candidate skills against target industry benchmarks. It highlights missing technical and soft skills and provides actionable career transition insights (e.g., *"By adding Low-Level Design (LLD) and System Architecture to your current profile, you become eligible for Software Development Engineer (SDE-II) roles"*).

4. **AI Interactive Mock Interview**:
   A real-time, role-tailored mock interview module offering:
   - **Dual-Mode Interaction**: Voice input/output (Speech-to-Text & Text-to-Speech) and text chat.
   - **Bilingual & Hinglish Support**: Capability to speak and understand English, Hindi, and code-switched Hindi-English (Hinglish) for localized candidate comfort.
   - **Dynamic Follow-up & Evaluation**: Tailored questions based on resume gaps and role requirements with immediate evaluation feedback.

---

## Milestone 2: Review of Existing Systems & Project Feasibility

### 2.1 Literature & Market Review

#### Existing Commercial Systems
* **ResumeWorded & Rezi**: Provide automated resume scoring and Applicant Tracking System (ATS) keyword matching. However, they rely on static keyword overlap, lack dynamic real-time job scraping, and offer no interview practice functionality.
* **Interviewer.ai & Interviewing.io**: Provide automated or peer-to-peer mock interviews. However, these platforms operate in isolation—they do not ingest user resumes to customize the interview questions based on individual skill gaps or specific job links.
* **LinkedIn Talent Insights & Coursera Skill Graph**: Offer high-level skill gap recommendations, but lack direct, interactive voice preparation tools or bilingual assistance.

#### Academic Literature & Technical Foundations
1. **Resume Parsing & Entity Extraction**: Transformer-based Named Entity Recognition (NER) models (*BERT-based NER*, *spaCy pipelines*) significantly outperform legacy rule-based parsers by capturing semantic context in varied resume layouts (Jia et al., 2022).
2. **Vector Space Skill Mapping**: Utilizing dense vector representations (*Sentence-BERT*) mapped against standardized skill taxonomies like **ESCO** (European Skills, Competencies, and Occupations) or **O*NET** allows for nuanced similarity scoring beyond exact string matches.
3. **Multilingual Speech Recognition**: Modern automatic speech recognition (ASR) frameworks like **OpenAI Whisper** exhibit high accuracy across multilingual and code-switched environments (e.g., English-Hindi / Hinglish), essential for Indian job markets (Radford et al., 2023).

#### Identified Gaps in Current Solutions
| Feature / Metric | Existing ATS / Resume Tools | Standalone Mock Interview Tools | Proposed SmartHire System |
| :--- | :--- | :--- | :--- |
| **Resume Parsing & Role Finding** | High (Static Score) | None | **High (Semantic Matching)** |
| **Live Job Links (LinkedIn/Google)** | None / Limited | None | **Integrated (Top 5-10 Links)** |
| **Skill Gap Transition Logic** | Basic List | None | **Contextual (e.g., LLD $\rightarrow$ SDE)** |
| **Interactive Voice Interview** | None | English Only | **Bilingual (English & Hindi)** |
| **Unified Pipeline** | No | No | **Yes (End-to-End)** |

---

### 2.2 Project Feasibility Analysis

#### Data Sources & Accessibility
* **Resume Corpus**: Kaggle Resume Dataset (2,400+ resumes across 24 job categories) augmented with synthetically generated edge-case resumes for model training and evaluation.
* **Skill Taxonomy & Job Ontology**: Open-access **ESCO API** and **O*NET OnLine** dataset providing structured hierarchies of technical skills, role titles, and prerequisites.
* **Job Search Data**: Live aggregation via **SerpAPI (Google Jobs API)**, **RapidAPI LinkedIn Jobs API**, and fallback web scraping via **Playwright/BeautifulSoup**.
* **Language & Speech Datasets**: Pre-trained **OpenAI Whisper** (base/small models) and Google Speech-to-Text API for multilingual audio processing.

#### Technical & Resource Feasibility
* **Compute Requirements**: Model inference (Sentence-Transformers, Whisper-base, LLM APIs) can run efficiently on standard student laptops / cloud free tiers (e.g., Google Colab free GPU / Kaggle Kernels / local CPU).
* **Development Stack**: Python (FastAPI backend), React.js / Vite (Frontend UI), Web Speech API / Whisper (Audio processing), Vector Store (FAISS / ChromaDB).

#### Zero-Cost & Open-Source Resource Guarantee
All models, datasets, frameworks, and APIs planned for **SmartHire** are **100% Free, Open-Source, or available under generous Free Tiers**, requiring **ZERO monetary budget**:

| Category / Component | Selected Technology | Licensing / Cost Model | 100% Free / Open-Source Status |
| :--- | :--- | :--- | :--- |
| **Resume Extraction** | `PDFPlumber`, `PyMuPDF` | Open-Source (MIT / AGPL) | **100% Free & Local** |
| **NLP & NER Embedding** | `spaCy`, `Sentence-Transformers` (`all-MiniLM-L6-v2`) | Open-Source (Apache 2.0) | **100% Free & Local** |
| **Skill Taxonomy Dataset** | ESCO API (European Commission) & O*NET | Open Data (CC BY 4.0 / Public Domain) | **100% Free Public Data** |
| **Resume Dataset** | Kaggle Resume Dataset (2,400+ samples) | Open Access (Public Dataset) | **100% Free** |
| **Job Scraping & Search** | `Playwright`, `BeautifulSoup4`, `DuckDuckGo Search API` / SerpAPI Free Tier | Open-Source / Free Tier (100 free/mo) | **100% Free & Open** |
| **Speech-to-Text (STT)** | OpenAI Whisper (`whisper-base` local) & Web Speech API | Open-Source (MIT) / Native Browser API | **100% Free & Local** |
| **Text-to-Speech (TTS)** | `Edge-TTS` (Microsoft Edge) & `gTTS` | Open-Source / Free Edge API wrapper | **100% Free** |
| **LLM Dialogue & Evaluation** | Ollama (`Llama-3.2-3B`, `Qwen-2.5`) or Groq / Google Gemini AI Studio Free Tiers | Open-Source Weights / Free API Tiers | **100% Free (Zero API cost)** |
| **Vector Database** | `FAISS` / `ChromaDB` | Open-Source (MIT / Apache 2.0) | **100% Free & Local** |

#### Risk Assessment & Realistically Potential Failure Modes

| Risk Factor | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Web Scraping / API Rate Limits** (LinkedIn/Google blocking requests) | High | Implement cached job database, rate-limiting queues, and fallback to free search scrapers (`DuckDuckGo` / `Playwright`). |
| **Hindi/Hinglish ASR Audio Latency & Errors** (Technical terms spoken in Hindi accent) | Medium | Fine-tune Whisper STT prompts with domain-specific technical keyword bias; maintain fallback text input mode. |
| **LLM Hallucination in Skill Recommendations** (Suggesting irrelevant career jumps) | High | Constraint LLM prompts using structured ESCO skill graphs and strict JSON schema validation. |
| **Voice Interaction Latency** (Slow response time in mock interview) | Medium | Use streaming response protocols (WebSockets / Server-Sent Events) for real-time text and TTS streaming. |

---

## Milestone 3: Objectives & Methodology of Proposed Work

### 3.1 Measurable & Specific Objectives

To ensure project success, SmartHire targets the following quantitative performance metrics:

1. **Objective 1 (Resume Parsing & Skill Extraction Accuracy)**:
   Achieve an **F1-Score of \(\ge 0.88\)** and **Precision of \(\ge 0.90\)** on entity extraction (skills, education, work experience, job titles) across a held-out test dataset of 300 diverse resume layouts.

2. **Objective 2 (Job Matching & Link Relevance)**:
   Attain a **Normalized Discounted Cumulative Gain (NDCG@10) of \(\ge 0.82\)** and **Precision@5 of \(\ge 0.85\)** for fetched job listings and recommended job titles relative to the parsed candidate profile.

3. **Objective 3 (Skill Gap Transition Mapping)**:
   Identify at least **90% of critical prerequisite skill gaps** required for candidate target transitions (e.g., highlighting Low-Level Design for SDE-II roles) validated against expert skill taxonomies with user relevance rating **\(\ge 4.2 / 5.0\)**.

4. **Objective 4 (Mock Interview Latency & Speech Accuracy)**:
   Maintain an end-to-end voice interview turn latency of **\(\le 1.8 \text{ seconds}\)** while achieving a Word Error Rate **(WER) of \(\le 12\%\)** on English, Hindi, and Hinglish speech inputs.

---

### 3.2 Methodology & System Pipeline

The proposed methodology consists of 6 sequential phases, illustrated below:

```
[Resume Upload (PDF/DOCX)]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ Phase 1: Ingestion & Text Normalization                │
└─────────────────────────┬──────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: NER Parsing & Dense Vector Representation     │
└─────────────────────────┬──────────────────────────────┘
          │
          ├──────────────────────────────┐
          ▼                              ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ Phase 3: Job Title Match &   │ │ Phase 4: Skill Gap & Path    │
│ Live Job Search Aggregation  │ │ Transition Analysis          │
│ (LinkedIn / Google Jobs API) │ │ (Candidate vs Target Schema)  │
└─────────┬────────────────────┘ └─────────┬────────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         ▼
┌────────────────────────────────────────────────────────┐
│ Phase 5: Interactive AI Mock Interview Module          │
│ (Bilingual Audio/Text STT ──► LLM ──► TTS Engine)       │
└────────────────────────┬───────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────┐
│ Phase 6: Automated Candidate Evaluation & Feedback Report│
└────────────────────────────────────────────────────────┘
```

#### Step-by-Step Methodology Details

1. **Phase 1: Resume Ingestion & Preprocessing**
   - Extract raw text from candidate uploaded PDF/DOCX using `PDFPlumber` and `PyMuPDF`.
   - Perform text cleaning: removal of artifact encoding characters, section segmentation (Education, Skills, Experience, Projects).

2. **Phase 2: Resume Parsing & Skill Extraction**
   - Deploy fine-tuned `spaCy` NER model combined with `Sentence-Transformers` (`all-MiniLM-L6-v2`) to extract canonical skill names and calculate candidate profile vector \(V_{cand}\).
   - Classify top matching candidate job titles using vector cosine similarity against standard job role embedding index.

3. **Phase 3: Live Job Search Aggregation & Ranking**
   - Query job search API endpoints (Google Jobs via SerpAPI / LinkedIn API) using the identified job titles and candidate location.
   - Filter and rank top 5 to 10 live job postings using a hybrid sparse-dense scoring model:
     $$\text{Score} = \alpha \cdot \text{BM25}(Q, D) + (1-\alpha) \cdot \cos(V_{cand}, V_{job})$$
   - Display clickable job URLs with metadata (Company, Location, Salary Range, Date Posted).

4. **Phase 4: Skill Gap Analysis & Career Transition Engine**
   - Compare candidate skill vector \(V_{cand}\) against target role requirement vector \(V_{target}\).
   - Generate skill gap matrix \(G = V_{target} - V_{cand}\).
   - Apply graph-based prerequisite rules (e.g., if target = *SDE*, current = *Junior Developer*, missing = *LLD, System Design, Data Structures*). Output contextual career advice highlighting high-impact target skills.

5. **Phase 5: Interactive AI Mock Interview Engine**
   - **Question Generation**: Dynamic generation of 5-7 interview questions tailored to parsed resume projects and identified skill gaps.
   - **Speech Recognition (STT)**: User responds via speech (English or Hindi). Audio stream is processed using OpenAI Whisper STT fine-tuned for Indian accent/Hinglish context.
   - **Dialogue Management**: LLM evaluates answer correctness, asks logical follow-up questions, and transitions between technical and behavioral questions.
   - **Speech Synthesis (TTS)**: Convert AI questions into natural voice output using `Edge-TTS` / Google Cloud TTS.

6. **Phase 6: Comprehensive Feedback & Scoring**
   - Aggregate candidate performance metrics across communication clarity, technical accuracy, and confidence.
   - Produce a detailed downloadable evaluation report with suggested learning resources for identified skill gaps.

---

## Milestone 4: Relevance of Algorithms / Techniques

### 4.1 Algorithm Justification Matrix

| Sub-system Component | Chosen Technique / Model | Standard / Obvious Alternative | Technical Justification |
| :--- | :--- | :--- | :--- |
| **Resume Representation & Parsing** | **Sentence-Transformers (`all-MiniLM-L6-v2`) + spaCy NER** | Plain TF-IDF / Regex Matching | TF-IDF and regex rely on exact string matches and fail on semantic variations (e.g., missing that "React.js" relates to "Frontend Development"). Sentence-Transformers capture semantic context in a 384-dimensional dense vector space. |
| **Skill Gap & Path Recommendation** | **Graph Ontology (ESCO) + Vector Difference** | Simple Set Difference (`Target - Candidate`) | Simple set subtraction treats all skills independently and misses prerequisite hierarchies. Graph-based ontology recognizes skill dependencies (e.g., knowing C++ makes learning Java faster) and structures realistic learning pathways (e.g., LLD $\rightarrow$ SDE). |
| **Job Search Link Ranking** | **Hybrid Dense-Sparse Retrieval (BM25 + Cosine Similarity)** | Pure Keyword Database Lookup | Pure keyword search misses relevant listings with alternative job titles (e.g., "Full Stack Engineer" vs. "Software Developer"). Combining BM25 keyword precision with dense embedding semantic match yields optimal ranking accuracy. |
| **Voice Mock Interview STT** | **OpenAI Whisper (Multilingual/Hinglish)** | Standard Browser Web Speech API | Standard Web Speech APIs struggle with Indian accents, domain-specific tech vocabulary (e.g., "Kubernetes", "PyTorch"), and Hindi-English code-switching. Whisper handles code-switched audio robustly with lower Word Error Rate (WER). |
| **Interview Question & Feedback Generation** | **Prompt-Chained LLM (GPT-4o-mini / Llama 3) with JSON Schema** | Static Rule-Based Question Bank | Static question banks yield repetitive, non-adaptive interviews. Prompt-chained LLMs generate customized follow-up questions based on the candidate's specific resume projects and answer quality in real-time. |

---

### 4.2 Paragraph Technical Justification for Chosen Techniques

#### 1. Resume Parsing & Embedding: Sentence-Transformers + Custom NER
> **Why this fits better than plain TF-IDF or regex rules**: 
> Resumes display extreme layout heterogeneity and syntactic variation. Plain regex rules break when encountering non-standard formatting, while TF-IDF treats words as orthogonal tokens, failing to recognize that terms like *"PostgreSQL"*, *"MongoDB"*, and *"Relational Databases"* belong to the same underlying skill cluster. We chose `Sentence-Transformers (all-MiniLM-L6-v2)` coupled with a fine-tuned `spaCy` NER model because transformer embeddings project skills and experience into a continuous semantic vector space. This allows SmartHire to accurately match candidate profiles to job titles even when exact keywords do not match word-for-word.

#### 2. Skill Gap & Career Path Mapping: Graph Ontology + Vector Difference Analysis
> **Why this fits better than simple set difference**:
> A naive set difference (\(\text{Target Skills} \setminus \text{Candidate Skills}\)) treats all missing skills as isolated, flat check-boxes. It cannot infer skill dependencies or career transition bridge logic (e.g., recommending Low-Level Design [LLD] and Design Patterns to elevate a candidate from a Junior Coder to an SDE role). We chose an ESCO/O*NET Graph Ontology combined with vector difference scoring because graph structures explicitly encode directed skill dependencies and prerequisite paths. This enables SmartHire to deliver contextual, prioritized learning roadmaps rather than an overwhelming list of missing keywords.

#### 3. Live Job Aggregation & Ranking: Hybrid Dense-Sparse Retrieval (BM25 + Cosine Similarity)
> **Why this fits better than basic keyword database search**:
> Standard SQL keyword queries (`WHERE title LIKE '%Python%'`) either return excessive noisy results or miss relevant job postings that use synonymous job titles (e.g., *"Backend Engineer"* vs *"Python Developer"*). We selected a Hybrid Retrieval model combining BM25 (sparse retrieval for exact technical term precision, such as specific tool names) with Dense Vector Cosine Similarity (for capturing overall role context). This dual mechanism ensures that the top 5 to 10 live job links retrieved from LinkedIn or Google Jobs are both keyword-accurate and semantically aligned with the candidate's career goals.

#### 4. AI Voice Mock Interview Pipeline: Multilingual OpenAI Whisper + Streaming LLM
> **Why this fits better than rule-based trees or basic Web Speech APIs**:
> Traditional mock interview tools rely on static decision trees and native browser Web Speech APIs. Browser STT engines consistently fail when candidates switch between Hindi and English (Hinglish) or speak technical jargon with regional accents. We chose OpenAI Whisper (fine-tuned with domain prompts) integrated with a streaming LLM dialogue manager. Whisper provides robust Automatic Speech Recognition (ASR) across code-switched audio, while the LLM dynamically evaluates candidate responses, asks intelligent follow-up questions, and streams audio back in real-time, delivering a realistic, conversational interview experience.

---
*Document prepared for Project SmartHire.*
