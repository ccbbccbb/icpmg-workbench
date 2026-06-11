# /// script
# dependencies = [
#     "faker>=30.0.0",
# ]
# ///

import os
import random
from faker import Faker

# Initialize Faker
fake = Faker()

# Define industries and realistic components for synthetic matching
industries = {
    "Software Engineering": {
        "titles": ["Software Engineer", "Full Stack Developer", "DevOps Specialist", "Frontend Engineer", "Backend Developer"],
        "skills": ["Python", "JavaScript", "React", "Docker", "AWS", "SQL", "Git", "Kubernetes", "Java", "TypeScript"],
        "duties": ["Developed scalable microservices.", "Optimized database queries.", "Led migration to cloud architecture.", "Collaborated on Agile sprints.", "Implemented CI/CD pipelines."]
    },
    "Data Science & Analytics": {
        "titles": ["Data Scientist", "Data Analyst", "Machine Learning Engineer", "BI Developer", "Data Engineer"],
        "skills": ["Python", "R", "SQL", "Tableau", "Pandas", "PyTorch", "TensorFlow", "PowerBI", "Apache Spark"],
        "duties": ["Built predictive machine learning models.", "Designed interactive dashboards.", "Cleaned and processed unstructured data.", "Presented analytical insights to stakeholders.", "Optimized ETL pipelines."]
    },
    "Marketing & Communications": {
        "titles": ["Marketing Manager", "SEO Specialist", "Content Strategist", "Social Media Coordinator", "Growth Marketer"],
        "skills": ["Google Analytics", "SEO", "Copywriting", "HubSpot", "CRM", "A/B Testing", "Content Marketing", "PPC"],
        "duties": ["Managed multi-channel digital campaigns.", "Increased organic search traffic.", "Created engaging multimedia content.", "Analyzed campaign performance metrics.", "Coordinated product launch events."]
    },
    "Finance & Accounting": {
        "titles": ["Financial Analyst", "Accountant", "Investment Analyst", "Risk Manager", "Auditor"],
        "skills": ["Excel", "Financial Modeling", "GAAP", "SAP", "Forecasting", "Risk Assessment", "Auditing", "Tax Compliance"],
        "duties": ["Prepared monthly financial reports.", "Conducted comprehensive variance analysis.", "Managed corporate budgeting processes.", "Evaluated investment risk factors.", "Ensured compliance with regulatory frameworks."]
    }
}

universities = ["State University", "Tech Institute", "National University", "Metropolitan College"]
degrees = ["Bachelor of Science", "Master of Science", "Bachelor of Arts", "Master of Business Administration"]

# Setup destination directory
output_dir = "synthetic_resumes"
os.makedirs(output_dir, exist_ok=True)

# Build a deterministic pool of targeted genders
gender_pool = (["female"] * 158) + (["male"] * 152)
# Shuffle the pool so target domains and order remain fully randomized
random.shuffle(gender_pool)

for i, gender in enumerate(gender_pool, start=1):
    ind_name = random.choice(list(industries.keys()))
    ind_data = industries[ind_name]
    
    # Generate gender-accurate names
    if gender == "female":
        first_name = fake.first_name_female()
    else:
        first_name = fake.first_name_male()
        
    last_name = fake.last_name()
    name = f"{first_name} {last_name}"
    
    email = f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}"
    phone = fake.phone_number()
    city_state = f"{fake.city()}, {fake.state_abbr()}"
    
    edu_degree = random.choice(degrees)
    edu_major = ind_name if "Finance" in ind_name else ind_name.split(" & ")
    edu_inst = f"{fake.city()} {random.choice(universities)}"
    edu_year = random.randint(2012, 2022)
    
    num_skills = random.randint(4, 7)
    selected_skills = random.sample(ind_data["skills"], num_skills)
    
    resume_text = f"=========================================\n"
    resume_text += f"{name.upper()}\n"
    resume_text += f"{city_state} | {phone} | {email}\n"
    resume_text += f"=========================================\n\n"
    
    resume_text += f"PROFESSIONAL SUMMARY\n"
    resume_text += f"Results-driven professional specializing in {ind_name} with a proven track record of optimization and performance.\n\n"
    
    resume_text += f"TECHNICAL SKILLS\n"
    resume_text += f"{', '.join(selected_skills)}\n\n"
    
    resume_text += f"PROFESSIONAL EXPERIENCE\n"
    
    start_year = edu_year
    for job_idx in range(2):
        title = random.choice(ind_data["titles"])
        company = fake.company()
        end_year = start_year + random.randint(2, 4)
        if end_year > 2026:
            end_year = "Present"
            
        resume_text += f"{title} - {company}\n"
        resume_text += f"{start_year} - {end_year}\n"
        
        num_duties = random.randint(2, 3)
        selected_duties = random.sample(ind_data["duties"], num_duties)
        for duty in selected_duties:
            resume_text += f"  * {duty}\n"
        resume_text += "\n"
        
        if end_year == "Present":
            break
        start_year = end_year
        
    resume_text += f"EDUCATION\n"
    resume_text += f"{edu_degree} in {edu_major}\n"
    resume_text += f"{edu_inst} - Class of {edu_year}\n"
    
    # Prefix filename with gender to easily verify or sort in your data repo
    file_name = f"resume_{i:03d}_{gender}_{first_name}_{last_name}.txt"
    with open(os.path.join(output_dir, file_name), "w", encoding="utf-8") as f:
        f.write(resume_text)

print(f"✅ Successfully generated 310 resumes (158 female, 152 male) in '{output_dir}'.")
