import pandas as pd
import sys

# ==========================================
# 1. CONFIGURATION
# ==========================================
FILE_PATH = 'aggregated_data_final.xlsx'
OUTPUT_FILE = 'analysis_results_master.txt'

# STRATIFICATION: BIG TECH vs INDEPENDENT
BIG_TECH_KEYWORDS = [
    'google', 'meta', 'facebook', 'microsoft', 
    'nvidia', 'openai', 'amazon', 'apple', 'ibm', 'stabilityai', 
    'deepmind', 'salesforce', 'adobe', 'intel'
]

# RQ2: THEME KEYWORDS
THEME_KEYWORDS = {
    'Bias & Fairness': ['bias', 'fairness', 'discrimination', 'stereotype', 'gender', 'race', 'demographic', 'representation', 'inequality'],
    'Safety & Misuse': ['safety', 'misuse', 'harm', 'toxic', 'abuse', 'malicious', 'attack', 'fake', 'hallucination', 'risk', 'weapon', 'jailbreak'],
    'Privacy & PII': ['privacy', 'pii', 'consent', 'personal data', 'gdpr', 'anonym', 'surveillance', 'confidential'],
    'Environmental': ['carbon', 'energy', 'environment', 'emission', 'co2', 'footprint', 'sustain', 'power consumption']
}

# ==========================================
# 2. DATA LOADING & PROCESSING
# ==========================================
def load_data(filepath):
    print(f"Reading file: {filepath}...")
    try:
        df = pd.read_excel(filepath, engine='openpyxl')
    except Exception as e:
        print(f"ERROR: Could not read file. {e}")
        sys.exit()
    
    # Clean Headers
    df.columns = df.columns.str.strip().str.replace('\n', '').str.replace('\r', '')
    
    # Dynamic Column Finder
    try:
        ethic_col = [c for c in df.columns if 'ethical' in c.lower() and 'Q20' in c][0]
        date_col = [c for c in df.columns if 'Date' in c and 'Q3b' in c][0]
        creator_col = [c for c in df.columns if 'creator' in c.lower() and 'Q1' in c][0]
        task_col = [c for c in df.columns if 'Task' in c and 'HuggingFace' in c][0]
    except IndexError:
        print("ERROR: Could not find required columns. Check Excel headers.")
        sys.exit()

    # --- 1. SMART ETHICS CHECK (RQ1) ---
    df['ethical_text'] = df[ethic_col].fillna('').astype(str).str.strip().str.lower()
    
    def check_ethics(text):
        if len(text) < 3: return 0
        negative_phrases = [
            'n/a', 'none', 'missing', 'no information', 'not available',
            'not discussed', 'not explicitly discussed', 'no ethical considerations',
            'not mentioned', 'no mention', 'not provided', 'no specific',
            'not addressed', 'nothing mentioned'
        ]
        for phrase in negative_phrases:
            if phrase in text: return 0
        return 1

    df['has_ethics'] = df['ethical_text'].apply(check_ethics)
    
    # --- 2. DATES (RQ3) ---
    df['model_date'] = pd.to_datetime(df[date_col], errors='coerce')
    df['year'] = df['model_date'].dt.year
    df = df.dropna(subset=['year'])
    
    def define_era(year):
        return 'Pre-GenAI (2018-22)' if year <= 2022 else 'GenAI Era (2023-25)'
    df['era'] = df['year'].apply(define_era)
    
    # --- 3. CREATOR TYPE (Stratification) ---
    def is_big_tech(val):
        return any(k in str(val).lower() for k in BIG_TECH_KEYWORDS)
    df['is_big_tech'] = df[creator_col].apply(is_big_tech)
    df['creator_label'] = df['is_big_tech'].map({True: 'Big Tech', False: 'Independent'})

    # --- 4. DOMAIN CATEGORIZATION (RQ4) ---
    df['task_clean'] = df[task_col].fillna('').astype(str).str.lower()
    def categorize_domain(task):
        if 'text-to-image' in task or 'image-to-text' in task or 'multimodal' in task: return 'Multimodal'
        if any(x in task for x in ['text', 'translation', 'summarization', 'language', 'question', 'answering', 'fill-mask', 'conversation']): return 'NLP'
        if any(x in task for x in ['image', 'video', 'vision', 'object', 'detection', 'segmentation', 'face']): return 'Computer Vision'
        if 'audio' in task or 'speech' in task: return 'Audio'
        return 'Other'
    df['domain'] = df['task_clean'].apply(categorize_domain)

    # --- 5. THEME TAGGING (RQ2 & Deep Dive) ---
    for theme, keywords in THEME_KEYWORDS.items():
        # Check if ANY keyword exists in the text AND the model is documented
        df[theme] = df.apply(lambda row: 1 if (row['has_ethics'] == 1 and any(k in row['ethical_text'] for k in keywords)) else 0, axis=1)
    
    return df

# ==========================================
# 3. ANALYSIS & REPORTING
# ==========================================
def analyze_themes(df):
    """Counts theme occurrences"""
    valid_docs = df[df['has_ethics'] == 1]['ethical_text']
    theme_counts = {k: 0 for k in THEME_KEYWORDS.keys()}
    for text in valid_docs:
        for theme, keywords in THEME_KEYWORDS.items():
            if any(k in text for k in keywords):
                theme_counts[theme] += 1
    return theme_counts

def generate_report(df):
    with open(OUTPUT_FILE, 'w') as f:
        f.write("=======================================================\n")
        f.write("   SEMINAR ANALYSIS: MASTER REPORT (RQ1 - RQ4)\n")
        f.write("=======================================================\n\n")
        
        # --- PART 1: OVERVIEW (RQ1) ---
        total = len(df)
        documented = df['has_ethics'].sum()
        rate = (documented / total) * 100
        
        f.write(f"--- RQ1: EXTENT OF COVERAGE ---\n")
        f.write(f"Total Models Analyzed: {total}\n")
        f.write(f"Documented Models:     {documented}\n")
        f.write(f"Global Adoption Rate:  {rate:.2f}%\n\n")
        
        # Stratification
        tech_stats = df.groupby('is_big_tech')['has_ethics'].mean() * 100
        f.write(f"Adoption by Creator:\n")
        f.write(f"   Big Tech:    {tech_stats.get(True, 0):.2f}%\n")
        f.write(f"   Independent: {tech_stats.get(False, 0):.2f}%\n\n")

        # --- PART 2: DOMAIN ANALYSIS (RQ4) ---
        f.write(f"--- RQ4: DOMAIN ANALYSIS ---\n")
        domain_counts = df['domain'].value_counts()
        domain_stats = df.groupby('domain')['has_ethics'].mean() * 100
        for domain in domain_stats.index:
            count = domain_counts[domain]
            rate = domain_stats[domain]
            f.write(f"   {domain.ljust(15)}: {rate:.2f}% (n={count})\n")
        f.write("\n")

        # --- PART 3: TOPICAL ANALYSIS (RQ2) ---
        theme_counts = analyze_themes(df)
        f.write(f"--- RQ2: ETHICAL THEMES (Global) ---\n")
        f.write(f"(Based on {documented} documented models)\n")
        for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / documented) * 100
            f.write(f"   {theme.ljust(16)}: {count} models ({pct:.1f}%)\n")
        f.write("\n")

        # --- PART 4: TEMPORAL EVOLUTION (RQ3) ---
        f.write(f"--- RQ3: TEMPORAL EVOLUTION ---\n")
        era_stats = df.groupby('era')['has_ethics'].mean() * 100
        for era, score in era_stats.sort_index(ascending=False).items():
            f.write(f"   {era}: {score:.2f}%\n")
            
        f.write("\nYearly Breakdown:\n")
        year_stats = df.groupby('year')['has_ethics'].mean() * 100
        for year, score in year_stats.items():
            f.write(f"   {int(year)}: {score:.2f}%\n")
        f.write("\n")

        f.write("=======================================================\n")
        f.write("             DEEP DIVE ANALYSIS (CROSS-TABS)\n")
        f.write("=======================================================\n\n")

        # --- DEEP DIVE 1: THEMES OVER TIME ---
        f.write("1. HOW DID THE CONVERSATION CHANGE? (Themes by Era)\n")
        f.write("(% of documented models in that era discussing the topic)\n")
        
        # Calculate mean of theme columns grouped by Era, filtered for documented models only
        era_themes = df[df['has_ethics']==1].groupby('era')[list(THEME_KEYWORDS.keys())].mean() * 100
        
        for theme in THEME_KEYWORDS.keys():
            f.write(f"\n   [{theme}]\n")
            for era in era_themes.index:
                val = era_themes.loc[era, theme]
                f.write(f"      {era}: {val:.1f}%\n")
            
        # --- DEEP DIVE 2: CREATOR PRIORITIES ---
        f.write("\n2. CORPORATE vs. INDEPENDENT PRIORITIES (Themes by Creator)\n")
        
        creator_themes = df[df['has_ethics']==1].groupby('creator_label')[list(THEME_KEYWORDS.keys())].mean() * 100
        
        for theme in THEME_KEYWORDS.keys():
            f.write(f"\n   [{theme}]\n")
            for creator in creator_themes.index:
                val = creator_themes.loc[creator, theme]
                f.write(f"      {creator.ljust(12)}: {val:.1f}%\n")

    print(f"Success! Master report saved to: {OUTPUT_FILE}")

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    data = load_data(FILE_PATH)
    generate_report(data)