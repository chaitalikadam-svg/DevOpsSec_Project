# FinTrack: A Personal Finance Tracking Application

FinTrack is a **Django** web application for tracking income and expenses, setting savings goals with deadlines, analysing spending by category and exporting transactions to Excel. The project's focus is **DevSecOps**: every push to `main` runs static code analysis (Pylint) and a security and quality scan (SonarCloud) before the app is automatically deployed to AWS Elastic Beanstalk.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [CI/CD Pipeline](#cicd-pipeline)
- [Code Quality and Security Findings](#code-quality-and-security-findings)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Required Secrets](#required-secrets)



## Features

- **Registration and login:** sign up with username, email, password and password confirmation, then log in
- **Dashboard:** total income, total expenses and net savings at a glance
- **Transactions:** add income or expense entries (type, category, title, amount, date), view them in a list with debit and credit amounts, edit or delete them
- **Validation:** future dates cannot be selected
- **Categories:** food, entertainment, utilities, transportation, health, others
- **Goals:** set a savings goal with a title, amount and deadline
- **Analysis:** choose a start and end date to see income and expenses as a **pie chart** by category
- **Export:** download transactions as an **XLSX** file

## Tech Stack

| Area | Technology |
|---|---|
| Backend | Django (Python 3.9) |
| Frontend | Django templates, Tailwind CSS (CDN) |
| Static analysis | Pylint |
| Security and quality scan | SonarCloud (with pytest and coverage) |
| CI/CD | GitHub Actions |
| Hosting | AWS Elastic Beanstalk (Python 3.9 on 64-bit Amazon Linux 2023) |

## CI/CD Pipeline

The workflow (`devsecops.yml`) is triggered by a **push to `main`** or a **merged pull request into `main`**, and runs three dependent jobs. If any stage fails, the pipeline stops and nothing is deployed.
![Architecture Diagram](CICD.drawio)



| Stage | What it does |
|---|---|
| **Pylint** | Checks out the code, sets up Python 3.9, installs dependencies and runs Pylint (scored 0 to 10, with message codes such as C, R, W, E, F) |
| **SonarCloud** | Checks out the code (full history), sets up JDK 17 and Python 3.9, installs dependencies, runs `pytest` with coverage, then runs the SonarCloud scan (exclusions: migrations, `__pycache__`, `staticfiles`) |
| **Deploy** | Runs only after SonarCloud succeeds: sets up Python, installs the EB CLI, configures AWS credentials from secrets, then `eb init` and `eb deploy --label "deploy-<run_id>"` |

Each deployment is labelled with its GitHub Actions run ID, so every release can be traced to a specific workflow run.

## Code Quality and Security Findings

Issues found by the pipeline during development, and how each was resolved:

| Tool | Code | Issue | Fix |
|---|---|---|---|
| Pylint | C0411 | Wrong import order in `finance/views.py` | Reordered imports: standard library, third party, then first party |
| Pylint | C0116 | Missing function/class docstrings | Added docstrings |
| Pylint | C0301 | Line too long (over 100 characters) | Wrapped long lines in parentheses |
| Pylint | C0303 | Trailing whitespace | Removed it |
| Pylint | W0404 | Module `HttpResponse` re-imported | Removed the duplicate import |
| Pylint | W0613 | Unused `args` / `kwargs` arguments | Removed them |
| SonarCloud | Reliability (medium) | `<html>` tag missing `lang` attribute | Added `lang="en"` |
| SonarCloud | Maintainability | Commented-out code | Removed it |
| SonarCloud | Reliability (low) / Maintainability (medium) | Anchor tag used as a button (logout) | Replaced with a `<button>` |

## Project Structure

> Adjust this to match your repository layout.

```
DevOpsSec_Project/
├── .github/workflows/
│   └── devsecops.yml       # Pylint -> SonarCloud -> Deploy
├── finance/
│   ├── models.py           # Trans and Goal models
│   ├── forms.py            # RegisterForm, TransactionForm, GoalForm
│   ├── views.py            # Welcome, Register, Dashboard, edit/delete views
│   ├── admin.py            # Export resource (XLSX)
│   └── templates/finance/  # base.html, welcome.html, register.html, analysis.html, ...
├── manage.py
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9+
- Git
- (For deployment) AWS account, EB CLI, and a SonarCloud account

### Run locally

```bash
git clone https://github.com/Chaitali-Kadam1008/DevOpsSec_Project.git
cd DevOpsSec_Project

python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>, register a user and start adding transactions.

### Run the quality checks locally

```bash
pylint finance
pytest
coverage run -m pytest && coverage xml -o coverage.xml
```

### Deploy manually (optional)

```bash
eb init <app-name> --region us-east-1 --platform "Python 3.9 running on 64bit Amazon Linux 2023"
eb use <environment-name>
eb deploy
```

With the pipeline in place this is no longer needed: pushing to `main` deploys automatically.

## Required Secrets

Add these under **Repository → Settings → Secrets and variables → Actions**:

| Secret | Purpose |
|---|---|
| `SONAR_TOKEN` | SonarCloud authentication |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `AWS_SESSION_TOKEN` | Temporary credentials |
| `AWS_REGION` | Deployment region |
| `EB_APP_NAME` | Elastic Beanstalk application name |
| `EB_ENV_NAME` | Elastic Beanstalk environment name |

Secrets are injected at runtime and are never committed to the code, in line with DevSecOps best practice.
