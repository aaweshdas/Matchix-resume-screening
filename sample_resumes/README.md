# Demonstration Dataset: Resumes & Job Description (PDF Format)

This directory contains **16 production-grade PDF documents** designed to showcase and evaluate the **Resume Screening & Candidate Classification System**:
- **1 Job Description PDF**: `Job_Description_Full_Stack_Engineer.pdf`
- **15 Candidate Resumes in PDF format**: Realistic, fully-formatted CVs spanning different seniority levels, skill specializations, and career backgrounds.

---

## 📁 Directory Contents

| File Name | Candidate / Document | Role & Experience | Target Match Tier |
| :--- | :--- | :--- | :--- |
| **`Job_Description_Full_Stack_Engineer.pdf`** | **Target Job Opening** | Senior Full Stack Software Engineer (CloudScale Technologies) | **Target Reference JD** |
| `01_Resume_Alex_Chen_Senior_Full_Stack.pdf` | Alex Chen | Senior Full Stack Engineer (7+ yrs exp, Python, React, Microservices) | 🏆 **Top Tier Match (88.0%)** |
| `02_Resume_Sarah_Jenkins_Lead_Full_Stack.pdf` | Sarah Jenkins | Lead Full Stack Developer (6 yrs exp, Python, JS, TDD, Docker) | 🏆 **Top Tier Match (88.9%)** |
| `03_Resume_Michael_Rodriguez_Senior_Software_Engineer.pdf` | Michael Rodriguez | Senior Software Engineer (5+ yrs exp, Python, JS, SQL, CI/CD) | 🏆 **Top Tier Match (83.7%)** |
| `04_Resume_Priya_Sharma_Full_Stack_Engineer.pdf` | Priya Sharma | Full Stack Engineer (4.5 yrs exp, Python, JS, REST APIs, Databases) | 🏆 **Top Tier Match (86.8%)** |
| `05_Resume_David_Kim_Backend_Python_Developer.pdf` | David Kim | Backend Software Engineer (4 yrs exp, Heavy Python/SQL, less frontend) | 🥈 **Strong Candidate (75.7%)** |
| `06_Resume_Elena_Rostova_Web_Application_Engineer.pdf` | Elena Rostova | Web Application Engineer (3.5 yrs exp, Heavy JS/UI, secondary Python) | 🥈 **Strong Candidate (69.8%)** |
| `07_Resume_Marcus_Vance_Software_Engineer.pdf` | Marcus Vance | Software Engineer (3 yrs exp, Python/Django, JS, SQL) | 🥈 **Strong Candidate (79.1%)** |
| `08_Resume_Ananya_Patel_Cloud_Backend_Developer.pdf` | Ananya Patel | Cloud & Backend Developer (4 yrs exp, Python, Docker, CI/CD) | 🥈 **Strong Candidate (69.3%)** |
| `09_Resume_James_Wilson_DevOps_Engineer.pdf` | James Wilson | DevOps & Infrastructure Engineer (Docker, CI/CD, Linux, Python scripts) | 🥉 **Moderate Fit (50.9%)** |
| `10_Resume_Lucas_Silva_Data_Analyst.pdf` | Lucas Silva | Data Analyst & SQL Specialist (SQL, Python, Pandas, Tableau) | 🥉 **Moderate / Borderline (32.8%)** |
| `11_Resume_Chloe_Bennett_Frontend_Developer.pdf` | Chloe Bennett | Frontend UI Developer (JavaScript, React, CSS, lacks backend SQL/Python) | 🥉 **Moderate / Borderline (42.5%)** |
| `12_Resume_Daniel_O_Connor_Junior_Programmer.pdf` | Daniel O'Connor | Junior Programmer (1 yr exp, foundational CS knowledge, junior scale) | 🥉 **Moderate Fit (55.0%)** |
| `13_Resume_Emily_Watson_Financial_Analyst.pdf` | Emily Watson | Senior Financial Analyst (Corporate finance, Valuation, DCF, Excel) | ❌ **Low Match / Gap (1.4%)** |
| `14_Resume_Robert_Taylor_Digital_Marketing_Manager.pdf` | Robert Taylor | Digital Marketing Manager (SEO, Google Ads, Meta Ads, Copywriting) | ❌ **Low Match / Gap (1.4%)** |
| `15_Resume_Jessica_Miller_HR_Operations_Lead.pdf` | Jessica Miller | People Operations & HR Lead (Talent onboarding, Jira ticketing, SLAs) | ❌ **Low Match / Gap (3.1%)** |

---

## 🎯 How to Demonstrate the Project Using These Files

### Option 1: Live Interactive Web UI (Recommended)
1. Start the system by running `run_fullstack.bat` (or start the Flask backend on port 5000 and the Vite frontend on port 5173).
2. In the web interface, navigate to the **"Batch Resume Screening & Parsing"** tab.
3. Under **Job Description Selection**, click **"Upload Job Description (PDF/DOCX/TXT)"** and select `Job_Description_Full_Stack_Engineer.pdf`.
   - *The NLP engine immediately parses the PDF, extracts the title, identifies required skills (Python, JavaScript, REST APIs, SQL, Git, OOP, Databases) and preferred skills (Docker, CI/CD, Unit Testing, Agile, Scrum).*
4. In the **Candidate Resumes Upload** box, drag & drop or select all 15 resume PDFs from this `sample_resumes/` folder.
   - *The system parses all PDFs asynchronously, shows word counts, character counts, and preview chips for extracted skills.*
5. Click **"Screen 15 Resumes"**:
   - The dual-branch matching algorithm computes skill overlap and semantic text similarity for each candidate.
   - A ranked leaderboard will appear with candidates color-coded by tier (Top Tier Match, Strong Candidate, Moderate Fit, and Low Match).
   - Click on any candidate to inspect their matched skills and missing skill gaps.

### Option 2: 1-on-1 Deep Match & Pipeline Trace
1. In the web interface, go to **"Deep Match & Gap Analysis"** or **"Pipeline Architecture"**.
2. Select any candidate resume and test with custom job inputs to observe the exact multi-stage breakdown:
   - **Raw Resume Text Ingestion**
   - **NLP Text Normalization & Stopword Filtering**
   - **Rule-based Skill Extraction**
   - **Sublinear TF-IDF Vector Space Embedding**
   - **Weighted Dual-Branch Scoring & Fit Classification**

### Option 3: Terminal / Script Demonstration
You can run an automated screening script against all 15 resumes at any time using:
```bash
python scripts/test_screening_demo.py
```
