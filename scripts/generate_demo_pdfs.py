"""
Script to generate 15 realistic resume PDFs and 1 Job Description PDF for project demonstration.
Target Role: Senior Full Stack Software Engineer
Includes realistic formatting, authentic work histories, and varied candidate match tiers.
"""
from pathlib import Path
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_resumes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Styles Helper
# ---------------------------------------------------------------------------
def get_pdf_styles():
    base = getSampleStyleSheet()
    
    # Custom palette
    primary = colors.HexColor("#0f172a")     # Dark slate
    secondary = colors.HexColor("#2563eb")   # Royal blue
    text_dark = colors.HexColor("#1e293b")   # Body text
    text_muted = colors.HexColor("#64748b")  # Subtext / dates
    border_color = colors.HexColor("#e2e8f0")
    
    styles = {
        "Name": ParagraphStyle(
            "DocName",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=primary,
            spaceAfter=2,
        ),
        "Title": ParagraphStyle(
            "DocTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=secondary,
            spaceAfter=4,
        ),
        "Contact": ParagraphStyle(
            "DocContact",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=text_muted,
            spaceAfter=8,
        ),
        "SectionHeading": ParagraphStyle(
            "DocSectionHeading",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            textColor=primary,
            spaceBefore=6,
            spaceAfter=3,
            textTransform="uppercase",
        ),
        "Body": ParagraphStyle(
            "DocBody",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=text_dark,
            spaceAfter=3,
        ),
        "JobHeader": ParagraphStyle(
            "DocJobHeader",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=13,
            textColor=primary,
        ),
        "JobSub": ParagraphStyle(
            "DocJobSub",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11,
            textColor=text_muted,
        ),
        "Bullet": ParagraphStyle(
            "DocBullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11.5,
            textColor=text_dark,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=2,
        ),
        "SkillsBadge": ParagraphStyle(
            "DocSkillsBadge",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=text_dark,
        ),
        "JDTitle": ParagraphStyle(
            "DocJDTitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=primary,
            alignment=1, # Center
            spaceAfter=4,
        ),
        "JDCompany": ParagraphStyle(
            "DocJDCompany",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=secondary,
            alignment=1, # Center
            spaceAfter=12,
        ),
    }
    return styles, primary, secondary, border_color


# ---------------------------------------------------------------------------
# Job Description Generator
# ---------------------------------------------------------------------------
def generate_job_description_pdf(filepath: Path):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles, primary, secondary, border = get_pdf_styles()
    story = []

    # Title & Header
    story.append(Paragraph("JOB DESCRIPTION: SENIOR FULL STACK SOFTWARE ENGINEER", styles["JDTitle"]))
    story.append(Paragraph("CloudScale Technologies Inc. &bull; Enterprise Cloud Platform &bull; San Francisco, CA (Hybrid)", styles["JDCompany"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary, spaceAfter=10))

    # Overview
    story.append(Paragraph("Position Overview", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=5))
    story.append(Paragraph(
        "We are hiring a high-performing <b>Senior Full Stack Software Engineer</b> to design, build, and deploy "
        "mission-critical cloud platforms and enterprise web services. In this role, you will work across the entire "
        "stack, architecting high-throughput microservices, engineering scalable backend APIs, optimizing relational and document databases, "
        "and crafting responsive user interfaces. You will collaborate in an Agile sprint environment with product managers, "
        "QA teams, and DevOps engineers to deliver secure, production-ready software solutions.",
        styles["Body"]
    ))
    story.append(Spacer(1, 6))

    # Key Responsibilities
    story.append(Paragraph("Key Responsibilities", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=5))
    responsibilities = [
        "Design, develop, and maintain resilient <b>REST APIs</b> and microservices in <b>Python</b> to support heavy customer traffic.",
        "Build modern, performant, and responsive front-end user interfaces utilizing <b>JavaScript</b> and component-driven architectures.",
        "Design, query, and optimize relational and distributed <b>Databases</b> using advanced <b>SQL</b> schema design and indexing.",
        "Apply robust Object-Oriented Programming (<b>OOP</b>) principles, design patterns, and clean code standards.",
        "Containerize microservices with <b>Docker</b> and maintain automated <b>CI/CD</b> deployment pipelines.",
        "Implement comprehensive <b>Unit Testing</b> and test-driven development (TDD) suites to guarantee code stability.",
        "Collaborate in cross-functional <b>Agile</b> and <b>Scrum</b> ceremonies including sprint planning, daily standups, and backlog refinement.",
        "Leverage <b>Git</b> version control for branching, peer pull request reviews, and continuous delivery.",
        "Perform root cause analysis and technical troubleshooting on production incidents to maintain strict uptime SLAs."
    ]
    for resp in responsibilities:
        story.append(Paragraph(f"&bull; {resp}", styles["Bullet"]))
    story.append(Spacer(1, 6))

    # Technical Skills & Requirements
    story.append(Paragraph("Candidate Qualifications & Required Skills", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=5))
    
    req_data = [
        [
            Paragraph("<b>Required Skills (Must-Have):</b>", styles["JobHeader"]),
            Paragraph("<b>Python, JavaScript, REST APIs, SQL, Git, OOP, Databases</b>", styles["SkillsBadge"])
        ],
        [
            Paragraph("<b>Preferred Skills (Nice-to-Have):</b>", styles["JobHeader"]),
            Paragraph("<b>Docker, CI/CD, Unit Testing, Agile, Scrum, Problem Solving, Microservices</b>", styles["SkillsBadge"])
        ],
        [
            Paragraph("<b>Experience Level:</b>", styles["JobHeader"]),
            Paragraph("3 to 7+ years of hands-on software development experience across backend and full-stack environments.", styles["Body"])
        ],
        [
            Paragraph("<b>Education:</b>", styles["JobHeader"]),
            Paragraph("Bachelor's or Master's degree in Computer Science, Software Engineering, Information Technology, or equivalent practical industry experience.", styles["Body"])
        ],
    ]
    t = Table(req_data, colWidths=[160, 380])
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Evaluation Criteria Box
    story.append(Paragraph("Screening & Evaluation Framework", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=5))
    story.append(Paragraph(
        "Applicants will be evaluated through our dual-branch NLP matching architecture: <b>Skill Verification (55%)</b> "
        "matching core languages, frameworks, and tools, combined with <b>Semantic Resume TF-IDF Similarity (45%)</b> "
        "analyzing real-world engineering project experience, production scale, and responsibilities.",
        styles["Body"]
    ))

    doc.build(story)
    print(f"Generated JD: {filepath.name}")


# ---------------------------------------------------------------------------
# Resume Builder Helper
# ---------------------------------------------------------------------------
def build_resume_pdf(
    filepath: Path,
    name: str,
    title: str,
    contact_line: str,
    summary: str,
    skill_categories: dict[str, str],
    experience: list[dict],
    education: list[dict],
    certifications: list[str] = None
):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32,
    )
    styles, primary, secondary, border = get_pdf_styles()
    story = []

    # Header
    story.append(Paragraph(name, styles["Name"]))
    story.append(Paragraph(title, styles["Title"]))
    story.append(Paragraph(contact_line, styles["Contact"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary, spaceAfter=6))

    # Summary
    story.append(Paragraph("Professional Summary", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=4))
    story.append(Paragraph(summary, styles["Body"]))
    story.append(Spacer(1, 4))

    # Technical Skills
    story.append(Paragraph("Core Technical Skills", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=4))
    skill_rows = []
    for cat_name, skill_val in skill_categories.items():
        skill_rows.append([
            Paragraph(f"<b>{cat_name}:</b>", styles["JobHeader"]),
            Paragraph(skill_val, styles["SkillsBadge"])
        ])
    t_skills = Table(skill_rows, colWidths=[120, 420])
    t_skills.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_skills)
    story.append(Spacer(1, 4))

    # Professional Experience
    story.append(Paragraph("Professional Experience", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=4))

    for exp in experience:
        header_table = Table([
            [
                Paragraph(f"<b>{exp['role']}</b> &bull; {exp['company']}", styles["JobHeader"]),
                Paragraph(f"<font color='#64748b'>{exp['dates']} | {exp.get('location', 'Remote')}</font>", styles["JobSub"])
            ]
        ], colWidths=[360, 180])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        for bullet in exp["bullets"]:
            story.append(Paragraph(f"&bull; {bullet}", styles["Bullet"]))
        story.append(Spacer(1, 3))

    # Education & Certifications
    story.append(Paragraph("Education & Credentials", styles["SectionHeading"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border, spaceAfter=4))
    for edu in education:
        edu_table = Table([
            [
                Paragraph(f"<b>{edu['degree']}</b> &bull; {edu['institution']}", styles["JobHeader"]),
                Paragraph(f"<font color='#64748b'>{edu['dates']} | {edu.get('location', '')}</font>", styles["JobSub"])
            ]
        ], colWidths=[380, 160])
        edu_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(edu_table)
        if "details" in edu and edu["details"]:
            story.append(Paragraph(f"&bull; {edu['details']}", styles["Bullet"]))

    if certifications:
        cert_text = " &bull; ".join(certifications)
        story.append(Paragraph(f"<b>Certifications:</b> {cert_text}", styles["Body"]))

    doc.build(story)
    print(f"Generated Resume: {filepath.name}")


# ---------------------------------------------------------------------------
# Candidates Definition Data
# ---------------------------------------------------------------------------
def generate_all_resumes():
    # 1. ALEX CHEN (Top Tier Match ~93%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "01_Resume_Alex_Chen_Senior_Full_Stack.pdf",
        name="Alex Chen",
        title="Senior Full Stack Software Engineer",
        contact_line="San Francisco, CA | (415) 890-2341 | alex.chen.dev@gmail.com | linkedin.com/in/alexchen-dev | github.com/alexchen-cloud",
        summary="Results-driven Senior Full Stack Software Engineer with 7+ years of experience architecting resilient cloud platforms, high-throughput microservices, and modern web applications. Expert in Python, JavaScript, REST APIs, SQL, and enterprise Databases. Proven track record establishing robust CI/CD pipelines, containerizing workloads with Docker, and applying OOP design patterns to achieve 99.99% system availability.",
        skill_categories={
            "Programming Languages": "Python, JavaScript, TypeScript, SQL, Java",
            "Web & APIs": "REST APIs, GraphQL, FastAPI, Django, React, Node.js, Express",
            "Databases & Storage": "Databases, PostgreSQL, SQL, MySQL, Redis, MongoDB",
            "DevOps & Infrastructure": "Docker, CI/CD, Git, Linux, Kubernetes, AWS",
            "Practices & Testing": "OOP, Unit Testing, Agile, Scrum, Microservices, Problem Solving"
        },
        experience=[
            {
                "role": "Lead Full Stack Software Engineer",
                "company": "Nexus Cloud Systems",
                "dates": "2021 - Present",
                "location": "San Francisco, CA",
                "bullets": [
                    "Architected and deployed 14 high-throughput microservices using <b>Python</b> (FastAPI) and <b>JavaScript</b> (React), serving 1.2M daily active users.",
                    "Designed scalable <b>REST APIs</b> and optimized relational <b>Databases</b> with complex <b>SQL</b> query tuning, reducing response latency by 42%.",
                    "Built automated <b>CI/CD</b> workflows with <b>Git</b> and <b>Docker</b> containers, cutting deployment turnaround from 4 hours to 12 minutes.",
                    "Mentored 6 junior engineers on <b>OOP</b> design principles, clean architecture, and <b>Unit Testing</b>, maintaining 94% test coverage.",
                    "Collaborated in bi-weekly <b>Agile</b> and <b>Scrum</b> sprints to deliver roadmap features ahead of schedule."
                ]
            },
            {
                "role": "Full Stack Developer",
                "company": "FinFlow Technologies",
                "dates": "2018 - 2021",
                "location": "San Jose, CA",
                "bullets": [
                    "Developed secure customer dashboard and payment checkout workflows using <b>Python</b>, <b>JavaScript</b>, and PostgreSQL <b>Databases</b>.",
                    "Implemented <b>REST APIs</b> interfacing third-party payment gateways with strict idempotency and <b>SQL</b> transaction isolation.",
                    "Containerized monolithic applications into modular <b>Docker</b> services, streamlining local development and automated testing.",
                    "Led code reviews using <b>Git</b> pull requests, enforcing rigorous <b>Unit Testing</b> and <b>OOP</b> standards."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of California, Berkeley",
                "dates": "2014 - 2018",
                "location": "Berkeley, CA",
                "details": "Graduated Magna Cum Laude. Coursework in Distributed Systems, Database Management, and Algorithms."
            }
        ],
        certifications=["AWS Certified Solutions Architect", "Docker Certified Associate (DCA)"]
    )

    # 2. SARAH JENKINS (Top Tier Match ~90%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "02_Resume_Sarah_Jenkins_Lead_Full_Stack.pdf",
        name="Sarah Jenkins",
        title="Lead Full Stack Developer",
        contact_line="Seattle, WA | (206) 555-0192 | s.jenkins.eng@outlook.com | linkedin.com/in/sarahjenkins-tech | github.com/sjenkins-code",
        summary="Accomplished Full Stack Developer with 6 years of experience building mission-critical SaaS web applications. Deep expertise across Python backend architectures, modern JavaScript UI frameworks, relational SQL databases, and secure REST APIs. Dedicated advocate of test-driven development, OOP best practices, Docker containerization, and Agile team execution.",
        skill_categories={
            "Core Technologies": "Python, JavaScript, SQL, REST APIs, Databases",
            "Frameworks": "Django, Flask, React, Node.js, Next.js",
            "Tools & DevOps": "Git, Docker, CI/CD, PostgreSQL, Redis",
            "Methodologies": "OOP, Unit Testing, Agile, Scrum, Problem Solving"
        },
        experience=[
            {
                "role": "Senior Full Stack Developer",
                "company": "Apex Digital Platforms",
                "dates": "2020 - Present",
                "location": "Seattle, WA",
                "bullets": [
                    "Engineered enterprise analytics dashboard utilizing <b>Python</b> backend and <b>JavaScript</b> front-end, processing 85M events daily.",
                    "Created 30+ production <b>REST APIs</b> and normalized relational <b>Databases</b> with high-efficiency <b>SQL</b> queries and partitioning.",
                    "Established automated <b>CI/CD</b> deployment pipelines with <b>Docker</b> and GitHub Actions, lowering production release bugs by 38%.",
                    "Enforced <b>OOP</b> modularity and structured <b>Unit Testing</b> (pytest/Jest), elevating automated regression coverage to 91%.",
                    "Facilitated <b>Agile</b> sprint retrospectives and backlog grooming sessions as team <b>Scrum</b> master."
                ]
            },
            {
                "role": "Software Engineer",
                "company": "BrightWave Software",
                "dates": "2018 - 2020",
                "location": "Portland, OR",
                "bullets": [
                    "Built full-stack portal modules using <b>Python</b>, <b>JavaScript</b>, and MySQL <b>Databases</b>.",
                    "Integrated secure <b>REST APIs</b> with authentication middleware (OAuth2/JWT) and <b>SQL</b> storage.",
                    "Maintained version control with <b>Git</b> and resolved cross-functional technical blockers with strong <b>Problem Solving</b>."
                ]
            }
        ],
        education=[
            {
                "degree": "M.S. in Software Engineering",
                "institution": "Georgia Institute of Technology",
                "dates": "2019 - 2021",
                "location": "Online / Atlanta, GA"
            },
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Washington",
                "dates": "2014 - 2018",
                "location": "Seattle, WA"
            }
        ],
        certifications=["Certified ScrumMaster (CSM)", "AWS Certified Developer Associate"]
    )

    # 3. MICHAEL RODRIGUEZ (Top Tier Match ~86%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "03_Resume_Michael_Rodriguez_Senior_Software_Engineer.pdf",
        name="Michael Rodriguez",
        title="Senior Software Engineer - Full Stack",
        contact_line="Austin, TX | (512) 441-9082 | m.rodriguez.code@gmail.com | linkedin.com/in/mrodriguez-dev | github.com/mrodriguez-cloud",
        summary="Senior Software Engineer with 5+ years of production experience developing distributed backend services, high-performance web applications, and database engines. Highly skilled in Python, JavaScript, REST APIs, SQL, OOP, and Git. Experienced working in Agile squads with Docker containerization, automated Unit Testing, and CI/CD pipelines.",
        skill_categories={
            "Languages": "Python, JavaScript, SQL, HTML, CSS",
            "Backend & APIs": "REST APIs, FastAPI, Django, Node.js, Express",
            "Databases": "Databases, PostgreSQL, SQL, MySQL, Redis",
            "DevOps & Quality": "Git, Docker, CI/CD, Unit Testing, OOP, Agile"
        },
        experience=[
            {
                "role": "Senior Software Engineer",
                "company": "DataPeak Solutions",
                "dates": "2021 - Present",
                "location": "Austin, TX",
                "bullets": [
                    "Designed and shipped cloud microservices in <b>Python</b> and <b>JavaScript</b>, handling 40,000 requests per minute.",
                    "Architected high-throughput <b>REST APIs</b> backed by PostgreSQL <b>Databases</b> and optimized <b>SQL</b> execution plans.",
                    "Integrated <b>Docker</b> containers into continuous integration <b>CI/CD</b> workflows, reducing build failures by 50%.",
                    "Spearheaded comprehensive <b>Unit Testing</b> initiatives and adherence to <b>OOP</b> patterns across engineering squads.",
                    "Collaborated in daily <b>Agile</b> standups and sprint planning to deliver enterprise features."
                ]
            },
            {
                "role": "Software Developer",
                "company": "TechFrontier Inc",
                "dates": "2019 - 2021",
                "location": "Dallas, TX",
                "bullets": [
                    "Engineered interactive web components using <b>JavaScript</b> and connected them to <b>Python</b> backend endpoints.",
                    "Managed relational <b>SQL</b> schemas, wrote migrations, and implemented caching layers.",
                    "Collaborated via <b>Git</b> branches, code reviews, and contributed to <b>Problem Solving</b> complex distributed bugs."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science & Engineering",
                "institution": "University of Michigan",
                "dates": "2015 - 2019",
                "location": "Ann Arbor, MI"
            }
        ],
        certifications=["HashiCorp Certified: Terraform Associate"]
    )

    # 4. PRIYA SHARMA (Top Tier Match ~84%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "04_Resume_Priya_Sharma_Full_Stack_Engineer.pdf",
        name="Priya Sharma",
        title="Full Stack Software Engineer",
        contact_line="New York, NY | (646) 302-8819 | priya.sharma.dev@gmail.com | linkedin.com/in/priyasharma-eng | github.com/priyasharma-code",
        summary="Proactive Full Stack Engineer with 4.5 years of industry experience building scalable web solutions. Proficient in Python, JavaScript, REST APIs, SQL, OOP, and modern Databases. Strong hands-on background in containerizing microservices with Docker, implementing automated Unit Testing, and maintaining CI/CD deployment pipelines within Agile/Scrum teams.",
        skill_categories={
            "Stack": "Python, JavaScript, REST APIs, SQL, Databases, Git",
            "Frameworks": "React, FastAPI, Django, Node.js",
            "Infrastructure": "Docker, CI/CD, Linux, AWS",
            "Concepts": "OOP, Unit Testing, Scrum, Agile, Problem Solving"
        },
        experience=[
            {
                "role": "Full Stack Engineer",
                "company": "Catalyst Labs",
                "dates": "2022 - Present",
                "location": "New York, NY",
                "bullets": [
                    "Developed full-stack web applications using <b>Python</b>, <b>JavaScript</b>, and modern UI components.",
                    "Constructed scalable <b>REST APIs</b> and normalized <b>SQL</b> data structures across enterprise <b>Databases</b>.",
                    "Automated integration testing and deployment pipelines using <b>Git</b>, <b>Docker</b>, and <b>CI/CD</b> tooling.",
                    "Implemented rigorous <b>Unit Testing</b> suites achieving 88% code coverage across all core services.",
                    "Actively engaged in <b>Agile</b> and <b>Scrum</b> sprint cycles with cross-functional product teams."
                ]
            },
            {
                "role": "Software Developer",
                "company": "CloudSphere Solutions",
                "dates": "2020 - 2022",
                "location": "Boston, MA",
                "bullets": [
                    "Built backend services and database access layers using <b>Python</b> and <b>SQL</b>.",
                    "Assisted frontend team with <b>JavaScript</b> asynchronous data fetching and state management.",
                    "Diagnosed production performance issues using systematic <b>Problem Solving</b> and <b>OOP</b> design."
                ]
            }
        ],
        education=[
            {
                "degree": "B.Tech in Computer Science & Engineering",
                "institution": "National Institute of Technology / Columbia MS Coursework",
                "dates": "2016 - 2020",
                "location": "New York, NY"
            }
        ]
    )

    # 5. DAVID KIM (Strong Candidate ~76%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "05_Resume_David_Kim_Backend_Python_Developer.pdf",
        name="David Kim",
        title="Backend Software Engineer",
        contact_line="Chicago, IL | (312) 604-1188 | david.kim.backend@gmail.com | linkedin.com/in/davidkim-backend | github.com/dkim-python",
        summary="Backend Software Engineer with 4 years of experience specializing in Python distributed systems, REST APIs, and database engineering. Deep knowledge of relational SQL, Databases, OOP design patterns, Docker containerization, and Unit Testing. Passionate about system performance, asynchronous workflows, and Agile delivery.",
        skill_categories={
            "Backend Languages": "Python, SQL, Go (basic), Bash",
            "APIs & Systems": "REST APIs, FastAPI, Django, Databases, PostgreSQL",
            "DevOps & Quality": "Docker, CI/CD, Git, Unit Testing, OOP",
            "Process": "Agile, Scrum, Problem Solving, Code Review"
        },
        experience=[
            {
                "role": "Backend Software Engineer",
                "company": "CoreScale Systems",
                "dates": "2021 - Present",
                "location": "Chicago, IL",
                "bullets": [
                    "Designed high-performance microservices and <b>REST APIs</b> in <b>Python</b> handling 5M daily queries.",
                    "Optimized relational <b>Databases</b> with complex <b>SQL</b> indexing, decreasing database CPU utilization by 35%.",
                    "Built <b>Docker</b> containerized deployment pipelines integrated with <b>Git</b> and <b>CI/CD</b>.",
                    "Applied clean <b>OOP</b> architecture and authored extensive <b>Unit Testing</b> test suites.",
                    "Participated in daily <b>Agile</b> standups and sprint planning sessions."
                ]
            },
            {
                "role": "Python Developer",
                "company": "Infotech Solutions",
                "dates": "2020 - 2021",
                "location": "Urbana, IL",
                "bullets": [
                    "Developed backend data integration scripts and scheduled tasks in <b>Python</b>.",
                    "Wrote complex <b>SQL</b> queries and maintained database integrity across staging and production.",
                    "Utilized <b>Git</b> for team version control and defect resolution."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Illinois Urbana-Champaign",
                "dates": "2016 - 2020",
                "location": "Urbana, IL"
            }
        ]
    )

    # 6. ELENA ROSTOVA (Strong Candidate ~74%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "06_Resume_Elena_Rostova_Web_Application_Engineer.pdf",
        name="Elena Rostova",
        title="Web Application Engineer",
        contact_line="Denver, CO | (720) 419-5520 | elena.rostova.web@gmail.com | linkedin.com/in/elenarostova | github.com/erostova-web",
        summary="Talented Web Application Engineer with 3.5 years of experience delivering modern responsive applications and web services. Strong expertise in JavaScript, REST APIs, SQL, Git, and Databases. Hands-on experience developing backend endpoints with Python and adhering to OOP and Agile methodologies.",
        skill_categories={
            "Frontend & UI": "JavaScript, React, HTML, CSS, Redux",
            "Backend & APIs": "REST APIs, Node.js, Python (FastAPI/Flask)",
            "Data & Tools": "SQL, Databases, PostgreSQL, Git, Unit Testing",
            "Methodology": "OOP, Agile, Problem Solving"
        },
        experience=[
            {
                "role": "Web Application Engineer",
                "company": "WebSphere Studios",
                "dates": "2021 - Present",
                "location": "Denver, CO",
                "bullets": [
                    "Engineered rich, interactive client applications in <b>JavaScript</b> (React) connected to backend <b>REST APIs</b>.",
                    "Developed supporting <b>Python</b> backend endpoints and integrated with relational <b>SQL</b> <b>Databases</b>.",
                    "Practiced strict <b>OOP</b> modularity and wrote automated <b>Unit Testing</b> using Jest and Pytest.",
                    "Managed code branching, peer reviews, and release tags using <b>Git</b>.",
                    "Collaborated closely with product designers within an <b>Agile</b> framework."
                ]
            },
            {
                "role": "Junior Developer",
                "company": "ByteCraft Technologies",
                "dates": "2020 - 2021",
                "location": "Boulder, CO",
                "bullets": [
                    "Constructed reusable <b>JavaScript</b> UI widgets and consumed external <b>REST APIs</b>.",
                    "Wrote database queries in <b>SQL</b> and assisted with system documentation."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Information Technology",
                "institution": "Purdue University",
                "dates": "2016 - 2020",
                "location": "West Lafayette, IN"
            }
        ]
    )

    # 7. MARCUS VANCE (Strong Candidate ~70%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "07_Resume_Marcus_Vance_Software_Engineer.pdf",
        name="Marcus Vance",
        title="Software Engineer",
        contact_line="Atlanta, GA | (404) 918-3209 | marcus.vance.code@gmail.com | linkedin.com/in/marcusvance-dev | github.com/mvance-stack",
        summary="Software Engineer with 3 years of full-stack engineering experience. Solid foundation in Python, JavaScript, REST APIs, SQL, and relational Databases. Experienced applying OOP design patterns, writing Unit Testing suites, and collaborating in fast-paced Agile teams using Git.",
        skill_categories={
            "Core Languages": "Python, JavaScript, SQL",
            "Web Development": "REST APIs, Django, React, Databases",
            "Engineering": "Git, OOP, Unit Testing, Agile, Problem Solving"
        },
        experience=[
            {
                "role": "Software Engineer",
                "company": "SwiftApp Innovations",
                "dates": "2022 - Present",
                "location": "Atlanta, GA",
                "bullets": [
                    "Built full stack features utilizing <b>Python</b> (Django) and <b>JavaScript</b> for internal business portals.",
                    "Authored clean <b>REST APIs</b> and designed relational <b>Databases</b> using PostgreSQL and <b>SQL</b>.",
                    "Implemented <b>Unit Testing</b> procedures and applied <b>OOP</b> standards to improve software maintainability.",
                    "Coordinated sprint deliverables in an <b>Agile</b> environment with <b>Git</b> version control."
                ]
            },
            {
                "role": "Junior Engineer",
                "company": "CodeVenture Labs",
                "dates": "2021 - 2022",
                "location": "Raleigh, NC",
                "bullets": [
                    "Assisted with backend <b>Python</b> scripts and client-side <b>JavaScript</b> validation.",
                    "Executed <b>SQL</b> queries for data verification and reporting."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science",
                "institution": "University of Texas at Austin",
                "dates": "2017 - 2021",
                "location": "Austin, TX"
            }
        ]
    )

    # 8. ANANYA PATEL (Strong Candidate ~68%)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "08_Resume_Ananya_Patel_Cloud_Backend_Developer.pdf",
        name="Ananya Patel",
        title="Cloud & Backend Developer",
        contact_line="San Jose, CA | (408) 555-4921 | ananya.patel.cloud@gmail.com | linkedin.com/in/ananyapatel-cloud | github.com/apatel-dev",
        summary="Software Developer with 4 years of experience focusing on cloud microservices, backend Python APIs, and distributed data systems. Hands-on experience with SQL, Databases, Docker containers, CI/CD automation, and Git. Strong technical problem solving and OOP foundations.",
        skill_categories={
            "Languages": "Python, SQL, Bash",
            "Cloud & DevOps": "Docker, CI/CD, Git, Databases, AWS",
            "Backend": "REST APIs, OOP, Unit Testing, Agile, Problem Solving"
        },
        experience=[
            {
                "role": "Cloud Application Developer",
                "company": "SkyHigh Data Systems",
                "dates": "2021 - Present",
                "location": "San Jose, CA",
                "bullets": [
                    "Engineered cloud backend microservices using <b>Python</b> and published secure <b>REST APIs</b>.",
                    "Automated container build and test workflows with <b>Docker</b>, <b>CI/CD</b>, and <b>Git</b>.",
                    "Maintained transactional <b>Databases</b> with structured <b>SQL</b> schemas and data validation.",
                    "Leveraged <b>OOP</b> design patterns and performed <b>Unit Testing</b> across all core modules."
                ]
            },
            {
                "role": "Associate Developer",
                "company": "Zenith Systems",
                "dates": "2020 - 2021",
                "location": "Santa Clara, CA",
                "bullets": [
                    "Wrote automated data ingestion pipelines in <b>Python</b> and queried <b>SQL</b> databases.",
                    "Collaborated with sprint teams using <b>Agile</b> methodology."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Engineering",
                "institution": "San Jose State University",
                "dates": "2016 - 2020",
                "location": "San Jose, CA"
            }
        ]
    )

    # 9. JAMES WILSON (Moderate Fit ~55% - DevOps / Infra)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "09_Resume_James_Wilson_DevOps_Engineer.pdf",
        name="James Wilson",
        title="DevOps & Infrastructure Engineer",
        contact_line="Philadelphia, PA | (215) 880-1422 | james.wilson.devops@gmail.com | linkedin.com/in/jwilson-infra | github.com/jwilson-devops",
        summary="DevOps Engineer with 5 years of experience automating cloud infrastructure, container orchestration, and continuous integration pipelines. Strong expertise in Docker, CI/CD, Git, Linux, and Python automation. Solid root cause analysis and Agile troubleshooting skills, with foundational familiarity in SQL databases.",
        skill_categories={
            "DevOps & Cloud": "Docker, CI/CD, Git, Linux, Kubernetes, Terraform",
            "Scripting & Data": "Python, Bash, SQL, Databases",
            "Methodology": "Agile, Jira, Root Cause Analysis, Problem Solving"
        },
        experience=[
            {
                "role": "Senior DevOps Engineer",
                "company": "CloudOps Global",
                "dates": "2021 - Present",
                "location": "Philadelphia, PA",
                "bullets": [
                    "Built enterprise <b>CI/CD</b> deployment pipelines deploying <b>Docker</b> containers across hybrid cloud clusters.",
                    "Authored automated infrastructure maintenance scripts in <b>Python</b> and managed version control with <b>Git</b>.",
                    "Monitored production <b>Databases</b> and performed <b>Root Cause Analysis</b> on server performance bottlenecks.",
                    "Managed infrastructure incident tickets and sprint workflows in <b>Jira</b> using <b>Agile</b> best practices."
                ]
            },
            {
                "role": "Systems Administrator",
                "company": "NetWorks Corp",
                "dates": "2019 - 2021",
                "location": "Pittsburgh, PA",
                "bullets": [
                    "Automated system provisioning and daily backup scripts using <b>Python</b> and bash.",
                    "Maintained database server availability and performed basic <b>SQL</b> schema backups."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Network Engineering",
                "institution": "Pennsylvania State University",
                "dates": "2015 - 2019",
                "location": "University Park, PA"
            }
        ],
        certifications=["AWS Certified SysOps Administrator", "Certified Kubernetes Administrator (CKA)"]
    )

    # 10. LUCAS SILVA (Moderate Fit ~50% - Data / SQL Analyst)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "10_Resume_Lucas_Silva_Data_Analyst.pdf",
        name="Lucas Silva",
        title="Data Analyst & SQL Specialist",
        contact_line="Los Angeles, CA | (310) 902-7711 | lucas.silva.data@gmail.com | linkedin.com/in/lucassilva-data | github.com/lsilva-analytics",
        summary="Detail-oriented Data Analyst with 3 years of experience in SQL querying, Python data processing, and enterprise Databases. Skilled in Pandas, data cleaning, automated reporting, and Git. Looking to leverage data and technical backend skills in software-adjacent projects.",
        skill_categories={
            "Data & Querying": "SQL, Databases, PostgreSQL, MySQL, Pandas",
            "Programming": "Python, R, Excel",
            "Analytics & Tools": "Data Visualization, Tableau, Git, Reporting, Problem Solving"
        },
        experience=[
            {
                "role": "Data Analyst",
                "company": "Insight Analytics Partners",
                "dates": "2021 - Present",
                "location": "Los Angeles, CA",
                "bullets": [
                    "Wrote complex <b>SQL</b> stored procedures, window functions, and joins across distributed <b>Databases</b>.",
                    "Developed automated ETL and reporting scripts using <b>Python</b> and <b>Pandas</b>.",
                    "Maintained analytical code repositories and version control using <b>Git</b>.",
                    "Delivered data insights to executive stakeholders through <b>Data Visualization</b> and automated <b>Reporting</b>."
                ]
            },
            {
                "role": "Junior BI Analyst",
                "company": "MarketMetrics Co",
                "dates": "2020 - 2021",
                "location": "San Diego, CA",
                "bullets": [
                    "Extracted business data from transactional <b>SQL</b> databases and created executive dashboards in Tableau.",
                    "Supported data cleansing and validation routines with <b>Python</b>."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Statistics & Data Science",
                "institution": "University of California, Los Angeles (UCLA)",
                "dates": "2016 - 2020",
                "location": "Los Angeles, CA"
            }
        ]
    )

    # 11. CHLOE BENNETT (Moderate Fit ~48% - Frontend Specialist)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "11_Resume_Chloe_Bennett_Frontend_Developer.pdf",
        name="Chloe Bennett",
        title="Frontend UI/UX Developer",
        contact_line="Brooklyn, NY | (718) 555-8910 | chloe.bennett.ui@gmail.com | linkedin.com/in/chloebennett-ui | github.com/cbennett-frontend",
        summary="Creative Frontend Developer with 3 years of experience crafting interactive user interfaces and responsive web applications. Deep proficiency in JavaScript, React, HTML5, CSS, and REST APIs integration. Experienced with Git version control, Unit Testing, and Agile sprint execution.",
        skill_categories={
            "Frontend Core": "JavaScript, TypeScript, React, HTML, CSS",
            "Web & APIs": "REST APIs, GraphQL, Redux, Responsive Design",
            "Engineering Tools": "Git, Unit Testing, Agile, Documentation, Communication"
        },
        experience=[
            {
                "role": "Frontend Developer",
                "company": "PixelCraft Media",
                "dates": "2021 - Present",
                "location": "New York, NY",
                "bullets": [
                    "Engineered single-page web applications using <b>JavaScript</b> (React) and modern CSS architectures.",
                    "Integrated frontend client components with backend <b>REST APIs</b>.",
                    "Conducted frontend <b>Unit Testing</b> using Jest and React Testing Library, reducing browser defects by 30%.",
                    "Managed source code and pull requests with <b>Git</b> in a collaborative <b>Agile</b> team."
                ]
            },
            {
                "role": "Web Designer & UI Developer",
                "company": "CreativeWave Agency",
                "dates": "2020 - 2021",
                "location": "Jersey City, NJ",
                "bullets": [
                    "Designed mobile-friendly landing pages and interactive components in <b>JavaScript</b>.",
                    "Collaborated with product owners on <b>Documentation</b> and design systems."
                ]
            }
        ],
        education=[
            {
                "degree": "B.A. in Digital Arts & Computer Science",
                "institution": "New York University (NYU)",
                "dates": "2016 - 2020",
                "location": "New York, NY"
            }
        ]
    )

    # 12. DANIEL O'CONNOR (Moderate Fit ~44% - Junior Programmer)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "12_Resume_Daniel_O_Connor_Junior_Programmer.pdf",
        name="Daniel O'Connor",
        title="Junior Software Programmer",
        contact_line="Columbus, OH | (614) 772-0199 | daniel.oconnor.dev@gmail.com | linkedin.com/in/danieloconnor-code | github.com/doconnor-junior",
        summary="Enthusiastic Junior Programmer and recent Computer Science graduate with 1 year of internship experience. Academic foundation in Python, JavaScript, SQL, OOP, and Git. Eager to contribute to production full-stack systems and learn industry best practices.",
        skill_categories={
            "Languages": "Python, JavaScript, SQL, C++",
            "Core Concepts": "OOP, Git, Databases, Problem Solving"
        },
        experience=[
            {
                "role": "Software Engineering Intern",
                "company": "StartupForge Inc",
                "dates": "2023 - 2024",
                "location": "Columbus, OH",
                "bullets": [
                    "Contributed bug fixes and feature enhancements in <b>Python</b> and <b>JavaScript</b>.",
                    "Wrote basic <b>SQL</b> queries to retrieve records from PostgreSQL <b>Databases</b>.",
                    "Maintained code changes on separate branches using <b>Git</b> and engaged in team code reviews.",
                    "Applied fundamental <b>OOP</b> concepts to organize helper functions and utilities."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Computer Science",
                "institution": "Ohio State University",
                "dates": "2019 - 2023",
                "location": "Columbus, OH",
                "details": "Dean's List. Capstone Project: Web-based campus event tracker with Python and SQLite."
            }
        ]
    )

    # 13. EMILY WATSON (Low Match ~25% - Finance)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "13_Resume_Emily_Watson_Financial_Analyst.pdf",
        name="Emily Watson",
        title="Senior Financial Analyst",
        contact_line="Boston, MA | (617) 492-3301 | emily.watson.fin@gmail.com | linkedin.com/in/emilywatson-cfa",
        summary="Strategic Senior Financial Analyst with 6 years of experience in corporate finance, budgeting, financial modeling, and variance analysis. Expert in advanced Excel, valuation methodologies, forecasting, and executive reporting. Proven ability to guide strategic capital allocation and optimize operating cash flow.",
        skill_categories={
            "Financial Analysis": "Financial Modeling, Valuation, Variance Analysis, Forecasting",
            "Accounting & Planning": "Accounting, Budgeting, Cash Flow, Reporting, KPIs",
            "Tools": "Excel, Power BI, PowerPoint, SAP"
        },
        experience=[
            {
                "role": "Senior Financial Analyst",
                "company": "Horizon Capital Partners",
                "dates": "2020 - Present",
                "location": "Boston, MA",
                "bullets": [
                    "Built 3-statement <b>Financial Modeling</b> and discount cash flow (DCF) <b>Valuation</b> models for M&A evaluations.",
                    "Conducted monthly <b>Variance Analysis</b> comparing actual performance to <b>Budgeting</b> forecasts.",
                    "Formulated quarterly financial <b>Forecasting</b> and prepared executive presentations tracking corporate <b>KPIs</b>.",
                    "Optimized working capital processes, driving a 14% improvement in free <b>Cash Flow</b>."
                ]
            },
            {
                "role": "Financial Analyst",
                "company": "Sterling Group",
                "dates": "2018 - 2020",
                "location": "Hartford, CT",
                "bullets": [
                    "Prepared recurring monthly financial <b>Reporting</b> and reconciliations in <b>Excel</b>.",
                    "Audited general ledger accounts and verified compliance with GAAP <b>Accounting</b> standards."
                ]
            }
        ],
        education=[
            {
                "degree": "B.S. in Finance & Economics",
                "institution": "Boston College",
                "dates": "2014 - 2018",
                "location": "Chestnut Hill, MA"
            }
        ],
        certifications=["CFA Level II Candidate", "Financial Modeling & Valuation Analyst (FMVA)"]
    )

    # 14. ROBERT TAYLOR (Low Match ~18% - Marketing)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "14_Resume_Robert_Taylor_Digital_Marketing_Manager.pdf",
        name="Robert Taylor",
        title="Digital Marketing & Growth Manager",
        contact_line="Austin, TX | (512) 388-6612 | robert.taylor.mkt@gmail.com | linkedin.com/in/roberttaylor-growth",
        summary="Data-driven Digital Marketing Manager with 5 years of experience accelerating customer acquisition across multi-channel campaigns. Skilled in SEO, Google Ads, Meta Ads, Content Marketing, and email marketing automation. Track record improving conversion rates and scaling qualified lead pipelines.",
        skill_categories={
            "Paid Acquisition": "Google Ads, Meta Ads, Conversion Optimization, Lead Generation",
            "Content & SEO": "SEO, Content Marketing, Copywriting, Landing Pages",
            "Strategy": "Marketing Analytics, Email Marketing, KPIs, Reporting"
        },
        experience=[
            {
                "role": "Growth Marketing Manager",
                "company": "Elevate Media Group",
                "dates": "2021 - Present",
                "location": "Austin, TX",
                "bullets": [
                    "Managed $1.5M annual paid advertising budgets across <b>Google Ads</b> and <b>Meta Ads</b>, driving a 3.4x ROAS.",
                    "Orchestrated organic <b>SEO</b> and <b>Content Marketing</b> initiatives, boosting organic domain search traffic by 85%.",
                    "A/B tested high-converting <b>Landing Pages</b> and revised sales <b>Copywriting</b> to increase lead conversions by 28%.",
                    "Monitored customer acquisition costs (CAC) and campaign <b>KPIs</b> via <b>Marketing Analytics</b> dashboards."
                ]
            },
            {
                "role": "Digital Marketing Specialist",
                "company": "BrandPulse Agency",
                "dates": "2019 - 2021",
                "location": "Dallas, TX",
                "bullets": [
                    "Executed targeted <b>Email Marketing</b> drip sequences and analyzed open/click <b>Reporting</b>.",
                    "Optimized keyword targeting and on-page technical <b>SEO</b> for 12 corporate client websites."
                ]
            }
        ],
        education=[
            {
                "degree": "B.A. in Communications & Marketing",
                "institution": "University of Colorado Boulder",
                "dates": "2015 - 2019",
                "location": "Boulder, CO"
            }
        ],
        certifications=["Google Ads Search Certification", "HubSpot Inbound Marketing Certified"]
    )

    # 15. JESSICA MILLER (Low Match ~12% - HR / Operations)
    build_resume_pdf(
        filepath=OUTPUT_DIR / "15_Resume_Jessica_Miller_HR_Operations_Lead.pdf",
        name="Jessica Miller",
        title="People Operations & HR Lead",
        contact_line="Phoenix, AZ | (602) 410-9923 | jessica.miller.hr@gmail.com | linkedin.com/in/jessicamiller-hr",
        summary="People Operations professional with 4 years of experience managing talent onboarding, HR process improvement, and employee engagement. Skilled in cross-functional coordination, project planning, stakeholder communication, and ticketing administration within fast-paced enterprise environments.",
        skill_categories={
            "People Operations": "Project Planning, Process Improvement, Stakeholder Communication",
            "Service & Systems": "Ticketing, Customer Satisfaction, Escalations, SLA, Jira",
            "HR Competencies": "Onboarding, Employee Relations, Documentation, Collaboration"
        },
        experience=[
            {
                "role": "People Operations Manager",
                "company": "TalentBridge Inc",
                "dates": "2021 - Present",
                "location": "Phoenix, AZ",
                "bullets": [
                    "Directed end-to-end employee onboarding workflows and led continuous <b>Process Improvement</b> initiatives.",
                    "Administered enterprise HR support <b>Ticketing</b> queues in <b>Jira</b>, consistently beating <b>SLA</b> targets.",
                    "Fostered internal <b>Stakeholder Communication</b> and championed workplace <b>Customer Satisfaction</b> programs.",
                    "Handled sensitive personnel <b>Escalations</b> with discretion and objective problem resolution."
                ]
            },
            {
                "role": "HR Coordinator",
                "company": "Summit Health Systems",
                "dates": "2020 - 2021",
                "location": "Tempe, AZ",
                "bullets": [
                    "Maintained employee records, compliance <b>Documentation</b>, and assisted with annual benefit enrollments.",
                    "Collaborated with department heads on workforce <b>Project Planning</b>."
                ]
            }
        ],
        education=[
            {
                "degree": "B.A. in Human Resources Management",
                "institution": "Arizona State University",
                "dates": "2016 - 2020",
                "location": "Tempe, AZ"
            }
        ],
        certifications=["SHRM Certified Professional (SHRM-CP)"]
    )

if __name__ == "__main__":
    jd_path = OUTPUT_DIR / "Job_Description_Full_Stack_Engineer.pdf"
    generate_job_description_pdf(jd_path)
    generate_all_resumes()
    print(f"\nSuccessfully generated 1 Job Description and 15 Resumes in: {OUTPUT_DIR}")
