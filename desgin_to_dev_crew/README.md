# 📘 Design-to-Dev CrewAI App

**Automatically turn high-level software requirements into technical
design, backend & frontend code skeletons, test plans, and a peer-review
report.**\
Built using **CrewAI**, inspired and guided by **Ed Donner's outstanding
"AgenticAI Engineering" course on Udemy**.

------------------------------------------------------------------------

## 🔧 Prerequisite

**Ensure you have `uv` and `crewai` installed before running this
application.**

------------------------------------------------------------------------

## ⭐ Special Acknowledgement

This project was directly inspired by **Ed Donner's AgenticAI
Engineering course on Udemy**, which provides exceptional hands-on
guidance for:

-   Designing multi-agent AI systems\
-   Building structured YAML configurations for agents & tasks\
-   Writing tools allowing agents to interact with the filesystem\
-   Using CrewAI's sequential pipelines for deterministic output\
-   Applying real-world engineering discipline to agent workflows

A heartfelt thanks to **Ed Donner** for the clarity, practicality, and
engineering depth in his course. This app exists because of those
learnings.

------------------------------------------------------------------------

# 🚀 Overview

**Design-to-Dev Crew** is an AI-driven development pipeline that:

1.  Reads high-level product requirements\
2.  Generates a complete **end-to-end technical design**\
3.  Produces a **Spring Boot backend skeleton**\
4.  Produces a **React/Vue frontend skeleton**\
5.  Generates a **complete QA test plan**\
6.  Performs a **peer-review** on the entire output\
7.  Saves all generated files to disk using a secure custom tool

------------------------------------------------------------------------

# 🧠 Architecture

The pipeline is implemented using:

-   **agents.yaml** -- agent definitions\
-   **tasks.yaml** -- sequential tasks defining workflow\
-   **file_writer.py** -- secure filesystem-writing tool\
-   **crew.py** -- formal CrewAI crew definition\
-   **main.py** -- command-line runner

------------------------------------------------------------------------

## 👤 Agents

### Development Lead

Creates the full system technical design.

### Backend Developer

Creates Spring Boot backend skeleton & packages.

### Frontend Developer

Creates React/Vue folder structure & components.

### Tester

Creates full unit, integration & acceptance test plans.

### Peer Reviewer

Performs engineering-level review of all outputs.

------------------------------------------------------------------------

# 🛠 Tools

### 🔒 `write_file` Tool

Writes files only within:

    /home/cmohite/projects/AgenticAIEngineering/generated1/

Prevents path traversal and ensures safe file creation.

------------------------------------------------------------------------

# ▶ Running the app

``` bash
python -m design_to_dev_crew.main
```

Outputs appear in:

    generated1/{app_name}/

------------------------------------------------------------------------

# ❤️ Credits

Created by: **Tania Mahmud**

Special recognition to:\
\### ⭐ **Ed Donner -- AgenticAI Engineering (Udemy)**\
Whose course enabled this entire project.
