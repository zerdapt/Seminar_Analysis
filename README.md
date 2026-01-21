# Seminar Analysis: Digital Humanism or Empty Promises?

### About the project
This repository contains the code and data analysis for the research paper **"Digital Humanism or Empty Promises? A Longitudinal Analysis of Ethical Reporting in Model Cards"**.

Here the documentation quality of **160 Machine Learning models** released between 2018 and 2025 gets analyzed. When it comes to the technical part, it involves a Python script that processes the aggregated metadata, so the developers documentation about the ethical risks can be evaluated. Specifically, it investigates the "Greenwashing Paradox" (prioritizing social bias over environmental impact) as well as the "GenAI Regression" (a drop in documentation standards during the recent generative AI boom). The analysis compares **Big Tech vs. Independent** developers and the **Pre-GenAI vs. GenAI** eras.

### Milestones
- Development of analysis script to process data and detect keywords
- Implementation of "Smart Ethics Check" to filter out placeholder documentation (e.g., "N/A")
- Stratification of data by Creator (Big Tech vs. Independent) and Era (Pre-GenAI vs. GenAI)
- Automated tagging of ethical themes: **Bias & Fairness**, **Safety & Misuse**, **Privacy**, and **Environmental Impact**
- Generation of the master report analysis_results_master.txt containing statistical insights
- Typesetting of the final research paper using LaTeX

#### Software

* **Python:** Version 3.9+
* **Pandas:** Data manipulation and analysis
* **OpenPyxl:** Excel file engine
* **LaTeX:** For thesis typesetting

### Getting Started

1.  **Clone the git repository**
    ```bash
    git clone https://github.com/zerdapt/Seminar_Analysis
    ```

2.  **Navigate to the project directory**
    ```bash
    cd Seminar-Analysis
    ```

3.  **Set up and activate the virtual environment**
    This creates an isolated environment for the project's dependencies.
    ```bash
    python -m venv venv
    ```
    Now, activate it:
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the analysis script**
    This will process the Excel data and generate the statistical report.
    ```bash
    python src/analysis.py
    ```

### Exploring the Results
After running the script, you can open **`analysis_results_master.txt`** to see the calculated adoption rates, domain breakdowns, and the comparison between Big Tech and Independent developers. The final interpretation of these numbers is available in the `thesis/` directory.
