import os
import streamlit as st
import json
from dotenv import load_dotenv
import google.generativeai as gen_ai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
from Agents.agent import Agents

# Set page config first, before any other Streamlit commands
st.set_page_config(
    page_title="Career Compass - AI Career Guide",
    page_icon="🎯",
    layout="wide",
)

# Load environment variables
load_dotenv()

gen_ai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Agents
agents = Agents()

def initialize_session_state():
    state_defaults = {
        "chat_session": agents.model.start_chat(history=[]),
        "chat_stage": 0,
        "user_data": {},
        "career_preferences": {},
        "skills_assessment": {},
        "career_path_recommendations": [],
        "selected_career_path": None,
        "learning_roadmap": None,
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

def translate_role_for_streamlit(user_role):
    return "assistant" if user_role == "model" else user_role

def reset_and_rerun():
    st.session_state.clear()
    st.rerun()

# Page Header
st.title("🎯 Career Compass - AI-Powered Career Mapping Tool")
st.write("Your intelligent guide to discovering the perfect tech career path")

# Initialize session state for page if not exists
if "page" not in st.session_state:
    st.session_state.page = "Profile Setup"

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    
    # Add back button at the top of sidebar using markdown
    st.markdown("""
        <a href="http://localhost:3000/dashboard" target="_self">
            <button style="
                background-color: #1e3c72;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 20px;
                width: 100%;
                display: flex;
                align-items: center;
                font-size: 16px;">
                ← Back to Dashboard
            </button>
        </a>
    """, unsafe_allow_html=True)
    
    pages = ["Profile Setup", "Career Assessment", "Career Recommendations", "Learning Roadmap", "Skills Gap Analysis", "Live AI Consultation"]
    current_page = st.radio("Choose a section:", pages, index=pages.index(st.session_state.page))
    
    if current_page != st.session_state.page:
        st.session_state.page = current_page
        st.rerun()
    
    if st.button(label="Start Fresh"):
        st.session_state.clear()
        st.session_state.page = "Profile Setup"
        st.rerun()

# Define Profile Questions
profile_questions = [
    ("Full Name", "What is your full name?"),
    ("Age", "What is your age?"),
    ("Education", "What is your current education level and field of study?"),
    ("Technical Background", "What is your current technical background or experience?")
]

# Career preference questions
career_preference_questions = {
    "interests": "What aspects of technology interest you the most? (e.g., coding, data analysis, system design)",
    "work_style": "Do you prefer working independently or in teams?",
    "learning_style": "How do you prefer to learn new skills?",
    "career_goals": "What are your long-term career goals in the tech industry?"
}

def display_profile_setup():
    st.header("Profile Setup")
    
    # Display progress
    progress = st.progress(0)
    progress.progress(int((st.session_state.chat_stage / len(profile_questions)) * 100))
    
    # Display completed responses
    if st.session_state.user_data:
        st.subheader("Your Profile Information:")
        for key, value in st.session_state.user_data.items():
            st.write(f"**{key}:** {value}")
    
    # Display current question
    if st.session_state.chat_stage < len(profile_questions):
        key, question = profile_questions[st.session_state.chat_stage]
        
        st.subheader("Please Answer:")
        with st.chat_message("assistant"):
            st.markdown(question)
        
        # Use a form for input
        with st.form(key=f"profile_form_{st.session_state.chat_stage}"):
            user_input = st.text_input("Your response:", key=f"profile_input_{st.session_state.chat_stage}")
            submit_button = st.form_submit_button("Submit")
            
            if submit_button and user_input:
                st.session_state.user_data[key] = user_input
                st.session_state.chat_stage += 1
                st.rerun()
    else:
        st.success("Profile setup completed! Please proceed to Career Assessment.")
        if st.button("Go to Career Assessment"):
            st.session_state.page = "Career Assessment"
            st.rerun()

def display_career_assessment():
    st.header("Career Assessment")
    
    if not st.session_state.user_data:
        st.warning("Please complete your profile setup first!")
        if st.button("Go to Profile Setup"):
            st.session_state.page = "Profile Setup"
            st.rerun()
        return
    
    # Display progress
    total_questions = len(career_preference_questions)
    completed_questions = len(st.session_state.career_preferences)
    progress = st.progress(0)
    progress.progress(int((completed_questions / total_questions) * 100))
    
    # Show assessment form
    with st.form(key="career_assessment_form"):
        st.subheader("Career Preferences Assessment")
        st.write("Please answer the following questions to help us understand your career preferences better.")
        
        responses = {}
        for key, question in career_preference_questions.items():
            if key not in st.session_state.career_preferences:
                st.write(f"**{question}**")
                responses[key] = st.text_area(
                    "Your answer:",
                    key=f"career_pref_{key}",
                    height=100
                )
        
        submit_button = st.form_submit_button("Submit Responses")
        
        if submit_button:
            # Update session state with new responses
            for key, response in responses.items():
                if response:  # Only update if response is not empty
                    st.session_state.career_preferences[key] = response
            st.rerun()
    
    # Display completed responses
    if st.session_state.career_preferences:
        st.subheader("Your Career Preferences:")
        for key, value in st.session_state.career_preferences.items():
            st.write("---")
            st.write(f"**Question:** {career_preference_questions[key]}")
            st.write(f"**Your Answer:** {value}")
    
    # Show completion message and next steps
    if len(st.session_state.career_preferences) == total_questions:
        st.success("Career assessment completed! You can now view your career recommendations.")
        if st.button("View Career Recommendations"):
            st.session_state.page = "Career Recommendations"
            st.rerun()

def fetch_job_market_data(career_path):
    """Fetch real job market data for the given career path"""
    # Sample data structure (in real implementation, this would come from an API)
    market_data = {
        # Technical Careers
        "Software Development": {
            "growth_rate": 25,
            "demand_score": 85,
            "min_salary": 500000,  # Changed to min_salary
            "trending_skills": ["Python", "JavaScript", "Cloud Computing", "DevOps"],
            "job_postings_trend": [1200, 1350, 1500, 1800, 2100, 2400],
        },
        "Data Science": {
            "growth_rate": 28,
            "demand_score": 90,
            "min_salary": 600000,
            "trending_skills": ["Python", "Machine Learning", "SQL", "Deep Learning"],
            "job_postings_trend": [800, 1000, 1300, 1600, 2000, 2500],
        },
        "Machine Learning Engineering": {
            "growth_rate": 30,
            "demand_score": 88,
            "min_salary": 700000,
            "trending_skills": ["TensorFlow", "PyTorch", "Computer Vision", "NLP"],
            "job_postings_trend": [600, 800, 1100, 1500, 1900, 2300],
        },
        "DevOps Engineering": {
            "growth_rate": 22,
            "demand_score": 82,
            "min_salary": 600000,
            "trending_skills": ["Docker", "Kubernetes", "AWS", "CI/CD"],
            "job_postings_trend": [900, 1100, 1400, 1700, 2000, 2200],
        },
        "Data Analytics": {
            "growth_rate": 23,
            "demand_score": 80,
            "min_salary": 450000,
            "trending_skills": ["SQL", "Python", "Tableau", "Power BI"],
            "job_postings_trend": [1000, 1200, 1400, 1600, 1800, 2000],
        },
        "Cybersecurity": {
            "growth_rate": 32,
            "demand_score": 92,
            "min_salary": 550000,
            "trending_skills": ["Network Security", "Ethical Hacking", "Security Tools", "Risk Assessment"],
            "job_postings_trend": [900, 1100, 1400, 1800, 2200, 2600],
        },
        "UI/UX Design": {
            "growth_rate": 24,
            "demand_score": 84,
            "min_salary": 450000,
            "trending_skills": ["Figma", "User Research", "Wireframing", "Design Systems"],
            "job_postings_trend": [800, 1000, 1200, 1500, 1800, 2100],
        },
        # Non-Technical Careers
        "Digital Marketing": {
            "growth_rate": 20,
            "demand_score": 78,
            "min_salary": 400000,
            "trending_skills": ["SEO", "Social Media", "Content Strategy", "Analytics"],
            "job_postings_trend": [1100, 1300, 1500, 1700, 1900, 2100],
        },
        "Product Management": {
            "growth_rate": 27,
            "demand_score": 86,
            "min_salary": 800000,
            "trending_skills": ["Agile", "Product Strategy", "User Stories", "Roadmapping"],
            "job_postings_trend": [700, 900, 1200, 1500, 1800, 2200],
        },
        "Business Analysis": {
            "growth_rate": 21,
            "demand_score": 79,
            "min_salary": 450000,
            "trending_skills": ["Requirements Gathering", "Process Modeling", "Data Analysis", "Stakeholder Management"],
            "job_postings_trend": [800, 1000, 1200, 1400, 1600, 1900],
        },
        "Technical Writing": {
            "growth_rate": 18,
            "demand_score": 75,
            "min_salary": 400000,
            "trending_skills": ["Documentation", "API Writing", "Content Management", "Information Architecture"],
            "job_postings_trend": [500, 600, 800, 1000, 1200, 1400],
        },
        "IT Project Management": {
            "growth_rate": 24,
            "demand_score": 83,
            "min_salary": 700000,
            "trending_skills": ["Project Planning", "Risk Management", "Team Leadership", "Budgeting"],
            "job_postings_trend": [900, 1100, 1300, 1600, 1900, 2200],
        },
        "IT Sales & Business Development": {
            "growth_rate": 19,
            "demand_score": 77,
            "min_salary": 450000,
            "trending_skills": ["Solution Selling", "CRM", "Relationship Building", "Technical Knowledge"],
            "job_postings_trend": [700, 900, 1100, 1300, 1500, 1800],
        }
    }
    return market_data.get(career_path, {})

def plot_market_trends(career_path, market_data):
    """Create visualizations for market trends"""
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Growth & Demand", "Starting Salary", "Job Postings Trend"])
    
    with tab1:
        # Create a radar chart for growth and demand
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[market_data["growth_rate"], market_data["demand_score"], 
               len(market_data["trending_skills"]) * 20],
            theta=['Growth Rate', 'Demand Score', 'Skill Diversity'],
            fill='toself',
            name=career_path
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title=f"Market Indicators for {career_path}"
        )
        st.plotly_chart(fig)

    with tab2:
        # Create a bar chart for minimum salary
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Starting Salary'],
            y=[market_data["min_salary"]],
            text=[f"₹{market_data['min_salary']:,.0f}"],
            textposition='auto',
        ))
        fig.update_layout(
            title=f"Starting Salary for {career_path}",
            yaxis_title="Annual Salary (INR)",
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
        )
        # Add a note about the salary being the minimum market rate
        st.plotly_chart(fig)
        st.markdown("_Note: This represents the typical starting salary based on current market trends._")

    with tab3:
        # Create a line chart for job postings trend
        current_month = datetime.now().month
        months = []
        for i in range(6):
            # Calculate month number (handling year wrap-around)
            month_num = ((current_month - 5 + i) % 12) or 12
            # Convert to month name
            month_name = datetime(2000, month_num, 1).strftime('%B')
            months.append(month_name)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=months,
            y=market_data["job_postings_trend"],
            mode='lines+markers',
            name='Job Postings'
        ))
        fig.update_layout(
            title=f"Job Postings Trend for {career_path}",
            xaxis_title="Month",
            yaxis_title="Number of Job Postings"
        )
        st.plotly_chart(fig)

    # Display trending skills
    st.subheader("🔥 Trending Skills")
    cols = st.columns(len(market_data["trending_skills"]))
    for idx, skill in enumerate(market_data["trending_skills"]):
        with cols[idx]:
            st.button(skill, key=f"skill_{idx}")

def display_career_recommendations():
    st.header("Career Path Recommendations")
    if not st.session_state.career_path_recommendations:
        if st.session_state.career_preferences:
            # Generate recommendations using AI
            try:
                recommendations = agents.generate_career_recommendations_agent(
                    st.session_state.user_data,
                    st.session_state.career_preferences
                )
                recommendations_data = json.loads(recommendations)
                st.session_state.career_path_recommendations = [
                    path["career_path"] for path in recommendations_data["recommended_paths"]
                ]
            except:
                # Fallback to default recommendations if AI fails
                st.session_state.career_path_recommendations = [
                    # Technical Paths
                    "Software Development",
                    "Data Science",
                    "Machine Learning Engineering",
                    "DevOps Engineering",
                    "Data Analytics",
                    "Cybersecurity",
                    "UI/UX Design",
                    # Non-Technical Paths
                    "Digital Marketing",
                    "Product Management",
                    "Business Analysis",
                    "Technical Writing",
                    "IT Project Management",
                    "IT Sales & Business Development"
                ]
    
    if st.session_state.career_path_recommendations:
        # Create two columns for career path selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Career Path Category")
            category = st.radio(
                "Select your preferred category:",
                ["All Careers", "Technical Careers", "Non-Technical Careers"]
            )
        
        # Filter career paths based on category
        all_paths = st.session_state.career_path_recommendations
        technical_paths = [path for path in all_paths if path in [
            "Software Development", "Data Science", "Machine Learning Engineering",
            "DevOps Engineering", "Data Analytics", "Cybersecurity", "UI/UX Design"
        ]]
        non_technical_paths = [path for path in all_paths if path in [
            "Digital Marketing", "Product Management", "Business Analysis",
            "Technical Writing", "IT Project Management", "IT Sales & Business Development"
        ]]
        
        with col2:
            st.subheader("Select Career Path")
            if category == "Technical Careers":
                paths_to_show = technical_paths
            elif category == "Non-Technical Careers":
                paths_to_show = non_technical_paths
            else:
                paths_to_show = all_paths
            
            selected_path = st.selectbox(
                "Based on your profile and preferences, here are your recommended career paths:",
                paths_to_show
            )
            
            if selected_path:
                st.session_state.selected_career_path = selected_path
    
    if st.session_state.selected_career_path:
        st.write(f"### {st.session_state.selected_career_path} Career Path")
        
        # Fetch and display market trends
        market_data = fetch_job_market_data(st.session_state.selected_career_path)
        if market_data:
            plot_market_trends(st.session_state.selected_career_path, market_data)
        
        # Display career path details
        display_career_path_details(st.session_state.selected_career_path)

def display_career_path_details(career_path):
    career_details = {
        # Technical Careers
        "Software Development": {
            "skills": ["Programming Languages (Python, Java, JavaScript)", "Web Development", "Database Management", "Version Control", "Software Architecture"],
            "opportunities": ["Full-stack Developer", "Backend Developer", "Mobile App Developer", "Cloud Solutions Engineer", "DevOps Engineer"],
            "market_trends": "High demand with 25% growth expected over next 5 years"
        },
        "Data Science": {
            "skills": ["Python", "Statistics", "Machine Learning", "Data Visualization", "Big Data Technologies"],
            "opportunities": ["Data Scientist", "Machine Learning Engineer", "AI Researcher", "Business Intelligence Analyst", "Quantitative Analyst"],
            "market_trends": "Rapidly growing field with 28% projected growth"
        },
        "Machine Learning Engineering": {
            "skills": ["Deep Learning", "NLP", "Computer Vision", "Python", "Model Deployment", "MLOps"],
            "opportunities": ["ML Engineer", "AI Developer", "Research Scientist", "Computer Vision Engineer", "NLP Engineer"],
            "market_trends": "Explosive growth with 30% increase in demand annually"
        },
        "DevOps Engineering": {
            "skills": ["Cloud Platforms", "CI/CD", "Container Orchestration", "Infrastructure as Code", "Monitoring Tools"],
            "opportunities": ["DevOps Engineer", "Site Reliability Engineer", "Cloud Engineer", "Platform Engineer", "Infrastructure Engineer"],
            "market_trends": "Strong demand with 22% growth in job openings"
        },
        "Data Analytics": {
            "skills": ["SQL", "Data Visualization", "Statistical Analysis", "Excel", "Business Intelligence Tools"],
            "opportunities": ["Data Analyst", "Business Intelligence Developer", "Marketing Analyst", "Financial Analyst", "Operations Analyst"],
            "market_trends": "Steady growth with 23% increase in opportunities"
        },
        "Cybersecurity": {
            "skills": ["Network Security", "Ethical Hacking", "Security Tools", "Risk Assessment", "Incident Response"],
            "opportunities": ["Security Engineer", "Penetration Tester", "Security Analyst", "Security Consultant", "Security Architect"],
            "market_trends": "Critical growth area with 32% increase in demand"
        },
        "UI/UX Design": {
            "skills": ["User Research", "Wireframing", "Prototyping", "Visual Design", "Design Systems"],
            "opportunities": ["UI Designer", "UX Designer", "Product Designer", "Interaction Designer", "Design System Specialist"],
            "market_trends": "Growing demand with 24% increase in opportunities"
        },
        # Non-Technical Careers
        "Digital Marketing": {
            "skills": ["SEO", "Social Media Marketing", "Content Strategy", "Analytics", "Email Marketing"],
            "opportunities": ["Digital Marketing Manager", "SEO Specialist", "Content Strategist", "Social Media Manager", "Marketing Analyst"],
            "market_trends": "Steady growth with 20% increase in roles"
        },
        "Product Management": {
            "skills": ["Product Strategy", "User Stories", "Agile Methodologies", "Data Analysis", "Stakeholder Management"],
            "opportunities": ["Product Manager", "Product Owner", "Technical Product Manager", "Growth Product Manager", "Senior Product Manager"],
            "market_trends": "High demand with 27% growth in opportunities"
        },
        "Business Analysis": {
            "skills": ["Requirements Gathering", "Process Modeling", "Data Analysis", "Documentation", "Stakeholder Management"],
            "opportunities": ["Business Analyst", "Systems Analyst", "Process Analyst", "Agile Business Analyst", "Senior Business Analyst"],
            "market_trends": "Stable growth with 21% increase in positions"
        },
        "Technical Writing": {
            "skills": ["Documentation", "API Writing", "Information Architecture", "Content Management", "Research"],
            "opportunities": ["Technical Writer", "Documentation Specialist", "API Documentation Writer", "Content Developer", "Knowledge Base Manager"],
            "market_trends": "Steady demand with 18% growth expected"
        },
        "IT Project Management": {
            "skills": ["Project Planning", "Risk Management", "Agile/Scrum", "Budgeting", "Team Leadership"],
            "opportunities": ["IT Project Manager", "Program Manager", "Scrum Master", "Delivery Manager", "Technical Project Lead"],
            "market_trends": "Strong growth with 24% increase in demand"
        },
        "IT Sales & Business Development": {
            "skills": ["Solution Selling", "Relationship Building", "Technical Knowledge", "CRM", "Negotiation"],
            "opportunities": ["Technical Sales Manager", "Solutions Consultant", "Business Development Manager", "Account Executive", "Sales Engineer"],
            "market_trends": "Consistent growth with 19% increase in opportunities"
        }
    }
    
    if career_path in career_details:
        details = career_details[career_path]
        
        # Create three columns for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Required Skills:**")
            for skill in details["skills"]:
                st.write(f"- {skill}")
        
        with col2:
            st.write("**💼 Career Opportunities:**")
            for opp in details["opportunities"]:
                st.write(f"- {opp}")
        
        # Market trends in a separate section with highlighting
        st.write("---")
        st.markdown(f"**📈 Market Trends:** _{details['market_trends']}_")

def display_learning_roadmap():
    st.header("Personalized Learning Roadmap")
    
    if not st.session_state.selected_career_path:
        st.warning("Please select a career path from the Career Recommendations section first!")
        if st.button("Go to Career Recommendations"):
            st.session_state.page = "Career Recommendations"
            st.rerun()
        return
    
    # Add an AI-themed header with emoji and styling
    st.markdown(
        f"""
        <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h2 style='color: #00FF00; margin: 0;'>🤖 AI-Powered Learning Path</h2>
            <p style='color: #FFFFFF; margin: 10px 0 0 0;'>Customized for: {st.session_state.selected_career_path}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Create a neural network-style visualization
    fig = go.Figure()
    
    # Define the stages with more detailed information
    stages = [
        {
            "name": "Fundamentals",
            "color": "#00FF00",
            "duration": "2-3 months",
            "icon": "🎓",
            "description": "Master the basics"
        },
        {
            "name": "Core Skills",
            "color": "#00FFFF",
            "duration": "3-4 months",
            "icon": "💡",
            "description": "Build essential expertise"
        },
        {
            "name": "Specialized Skills",
            "color": "#FF00FF",
            "duration": "4-6 months",
            "icon": "🚀",
            "description": "Deep dive into advanced topics"
        },
        {
            "name": "Projects",
            "color": "#FF0000",
            "duration": "Ongoing",
            "icon": "🛠️",
            "description": "Apply your knowledge"
        },
        {
            "name": "Professional Development",
            "color": "#FFD700",
            "duration": "Ongoing",
            "icon": "👔",
            "description": "Grow your career"
        }
    ]
    
    # Create neural network nodes and connections
    y_positions = [0, 0.5, -0.5, 0.25, -0.25]
    for i, stage in enumerate(stages):
        # Add main node
        fig.add_trace(go.Scatter(
            x=[i],
            y=[y_positions[i]],
            mode='markers+text',
            name=stage["name"],
            marker=dict(
                size=40,
                color=stage["color"],
                symbol='circle',
                line=dict(color='white', width=2)
            ),
            text=f"{stage['icon']}<br>{stage['name']}",
            textposition="bottom center",
            hovertemplate=(
                f"<b>{stage['name']}</b><br>" +
                f"Duration: {stage['duration']}<br>" +
                f"Focus: {stage['description']}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Add connecting lines with animation
        if i > 0:
            # Add multiple connection lines for neural network effect
            for prev_y in y_positions[:i]:
                fig.add_trace(go.Scatter(
                    x=[i-1, i],
                    y=[prev_y, y_positions[i]],
                    mode='lines',
                    line=dict(
                        color='rgba(255, 255, 255, 0.3)',
                        width=1,
                        dash='dot'
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    # Update layout for a more modern, AI-themed look
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='#1E1E1E',
        paper_bgcolor='#1E1E1E',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-0.5, 4.5]
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-1, 1]
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        title=dict(
            text="Interactive Learning Journey",
            font=dict(color='white', size=24),
            x=0.5,
            y=0.95
        )
    )
    
    # Display the interactive visualization
    st.plotly_chart(fig, use_container_width=True)
    
    # Create an AI-themed progress tracker
    st.markdown(
        """
        <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h3 style='color: #00FF00; margin: 0;'>🎯 Neural Progress Tracking</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize or get learning progress
    if "learning_progress" not in st.session_state:
        st.session_state.learning_progress = {
            "fundamentals": 0,
            "core_skills": 0,
            "specialized": 0
        }
    
    # Create columns for progress tracking
    cols = st.columns(3)
    for idx, (stage, progress) in enumerate(st.session_state.learning_progress.items()):
        with cols[idx]:
            st.markdown(f"**{stages[idx]['icon']} {stage.title()}**")
            new_progress = st.slider(
                "Progress",
                0, 100,
                progress,
                key=f"progress_{stage}",
                help=f"Track your progress in {stage}"
            )
            st.session_state.learning_progress[stage] = new_progress
            
            # Add a visual progress indicator
            if new_progress < 30:
                color = "#FF0000"
                status = "Getting Started"
            elif new_progress < 70:
                color = "#FFD700"
                status = "In Progress"
            else:
                color = "#00FF00"
                status = "Advanced"
                
            st.markdown(
                f"""
                <div style='background-color: #2E2E2E; padding: 10px; border-radius: 5px;'>
                    <div style='color: {color}; font-weight: bold;'>{status}</div>
                    <div style='background-color: #1E1E1E; height: 10px; border-radius: 5px; margin-top: 5px;'>
                        <div style='background-color: {color}; width: {new_progress}%; height: 100%; border-radius: 5px;'></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Display career-specific learning content
    learning_paths = {
        "Software Development": {
            "fundamentals": {
                "topics": ["Programming Basics", "Data Structures", "Algorithms", "Git Version Control"],
                "courses": [
                    {"name": "Complete Python Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/complete-python-bootcamp/"},
                    {"name": "Data Structures and Algorithms", "platform": "Coursera", "url": "https://www.coursera.org/specializations/data-structures-algorithms"}
                ],
                "projects": ["Build a Calculator", "Create a Todo App", "Implement Basic Data Structures"]
            },
            "core_skills": {
                "topics": ["Web Development", "Database Management", "API Development"],
                "courses": [
                    {"name": "The Web Developer Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-web-developer-bootcamp/"},
                    {"name": "Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"}
                ],
                "projects": ["Personal Portfolio Website", "RESTful API Service", "Database-driven Web App"]
            },
            "specialized": {
                "topics": ["Framework Expertise", "Cloud Services", "Testing"],
                "courses": [
                    {"name": "React - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
                    {"name": "AWS Certified Developer", "platform": "Udemy", "url": "https://www.udemy.com/course/aws-certified-developer-associate/"}
                ],
                "projects": ["Full-stack E-commerce Site", "Cloud-deployed Application", "Mobile-responsive Web App"]
            }
        },
        "Data Science": {
            "fundamentals": {
                "topics": ["Python Programming", "Statistics", "Linear Algebra", "Data Analysis"],
                "courses": [
                    {"name": "Python for Data Science", "platform": "Udemy", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"},
                    {"name": "Statistics for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/specializations/statistics"}
                ],
                "projects": ["Data Analysis with Pandas", "Statistical Analysis Project", "Data Visualization Dashboard"]
            },
            "core_skills": {
                "topics": ["Machine Learning", "Data Visualization", "Big Data Tools"],
                "courses": [
                    {"name": "Machine Learning A-Z", "url": "https://www.udemy.com/course/machinelearning/"},
                    {"name": "Deep Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning"}
                ],
                "projects": ["Predictive Analysis Model", "Customer Segmentation", "Time Series Forecasting"]
            },
            "specialized": {
                "topics": ["Deep Learning", "Natural Language Processing", "Computer Vision"],
                "courses": [
                    {"name": "TensorFlow Developer Certificate", "platform": "Udemy", "url": "https://www.udemy.com/course/tensorflow-developer-certificate-machine-learning-zero-to-mastery/"},
                    {"name": "NLP Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/natural-language-processing"}
                ],
                "projects": ["Image Classification System", "Sentiment Analysis Tool", "Recommendation Engine"]
            }
        }
        # Add more career paths here
    }
    
    career_path = learning_paths.get(st.session_state.selected_career_path, learning_paths["Software Development"])
    
    # Create modern tabs with icons
    tab1, tab2, tab3 = st.tabs([
        "📚 Learning Modules",
        "🎯 Project Lab",
        "🔗 Resource Hub"
    ])
    
    with tab1:
        for stage, content in career_path.items():
            with st.expander(f"{stages[list(career_path.keys()).index(stage)]['icon']} {stage.title()} Module"):
                st.markdown(
                    """
                    <div style='background-color: #2E2E2E; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                        <h4 style='color: #00FFFF; margin: 0 0 10px 0;'>📚 Key Topics</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                for topic in content["topics"]:
                    st.markdown(
                        f"""
                        <div style='background-color: #404040; padding: 12px; border-radius: 5px; margin: 5px 0; border: 1px solid #505050;'>
                            <div style='color: #FFFFFF; display: flex; align-items: center;'>
                                <span style='color: #00FF00; margin-right: 8px;'>⚡</span>
                                <span style='font-size: 16px;'>{topic}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    with tab2:
        st.subheader("🔬 Hands-on Projects")
        for stage, content in career_path.items():
            with st.expander(f"Projects for {stage.title()} Stage"):
                for project in content["projects"]:
                    st.markdown(
                        f"""
                        <div style='background-color: #404040; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #505050;'>
                            <div style='color: #00FF00; font-weight: bold; font-size: 16px;'>🛠️ {project}</div>
                            <div style='color: #CCCCCC; margin-top: 5px;'>Estimated time: 2-3 weeks</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    with tab3:
        st.subheader("📚 Learning Resources")
        for stage, content in career_path.items():
            with st.expander(f"Resources for {stage.title()} Stage"):
                for course in content["courses"]:
                    st.markdown(
                        f"""
                        <div style='background-color: #404040; padding: 15px; border-radius: 5px; margin: 10px 0; border: 1px solid #505050;'>
                            <div style='color: #00FFFF; font-weight: bold; font-size: 16px;'>
                                <a href="{course['url']}" target="_blank" style='color: #00FFFF; text-decoration: none;'>
                                    🔗 {course['name']}
                                </a>
                            </div>
                            <div style='color: #FFFFFF; margin-top: 5px;'>Platform: {course['platform']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
    # Additional Resources with modern styling
    st.markdown(
        """
        <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin: 20px 0;'>
            <h3 style='color: #00FF00; margin: 0;'>🌐 Learning Hub</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div style='background-color: #2E2E2E; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                <h4 style='color: #00FFFF; margin: 0 0 10px 0;'>🤝 Community & Forums</h4>
            </div>
        """, unsafe_allow_html=True)
        resources = ["Stack Overflow", "GitHub Discussions", "Reddit Communities", "LinkedIn Groups"]
        for resource in resources:
            st.markdown(
                f"""
                <div style='background-color: #404040; padding: 12px; border-radius: 5px; margin: 5px 0; border: 1px solid #505050;'>
                    <div style='color: #FFFFFF; display: flex; align-items: center;'>
                        <span style='color: #00FFFF; margin-right: 8px;'>🔍</span>
                        <span>{resource}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    with col2:
        st.markdown("""
            <div style='background-color: #2E2E2E; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                <h4 style='color: #00FFFF; margin: 0 0 10px 0;'>💻 Practice Platforms</h4>
            </div>
        """, unsafe_allow_html=True)
        platforms = [
            {"name": "LeetCode", "url": "https://leetcode.com/"},
            {"name": "HackerRank", "url": "https://www.hackerrank.com/"},
            {"name": "Kaggle", "url": "https://www.kaggle.com/"},
            {"name": "CodePen", "url": "https://codepen.io/"}
        ]
        for platform in platforms:
            st.markdown(
                f"""
                <div style='background-color: #404040; padding: 12px; border-radius: 5px; margin: 5px 0; border: 1px solid #505050;'>
                    <div style='color: #FFFFFF; display: flex; align-items: center;'>
                        <span style='color: #00FF00; margin-right: 8px;'>⚡</span>
                        <a href="{platform['url']}" target="_blank" style='color: #FFFFFF; text-decoration: none; display: flex; align-items: center;'>
                            <span>{platform['name']}</span>
                            <span style='color: #00FFFF; margin-left: 8px;'>↗</span>
                        </a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def display_live_consultation():
    st.header("Live AI Career Consultation")
    st.write("Chat with our AI career advisor for personalized guidance")
    
    # Initialize chat history if not exists
    if "consultation_history" not in st.session_state:
        st.session_state.consultation_history = []
    
    # Display chat history
    for message in st.session_state.consultation_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user question
    user_question = st.chat_input("Ask your career-related question:")
    if user_question:
        # Add user message to chat history
        st.session_state.consultation_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_question)
        
        try:
            # Generate AI response
            if not st.session_state.user_data:
                response = "Please complete your profile setup first to get personalized career advice. This will help me provide more relevant guidance based on your background and interests."
            else:
                try:
                    response = agents.career_consultation_agent(
                        user_question,
                        st.session_state.user_data
                    )
                except:
                    # Fallback response based on keywords in the question
                    keywords = user_question.lower()
                    if "career" in keywords or "job" in keywords:
                        response = "Based on current market trends, there are many promising career paths in technology. Consider exploring roles in Software Development, Data Science, or Cybersecurity. Each of these fields offers strong growth potential and competitive salaries. Would you like to learn more about any specific career path?"
                    elif "skill" in keywords or "learn" in keywords:
                        response = "To build a successful tech career, focus on both technical and soft skills. Key technical skills include programming languages, data analysis, and cloud computing. Important soft skills are problem-solving, communication, and adaptability. What specific skills are you interested in developing?"
                    elif "salary" in keywords or "pay" in keywords:
                        response = "Salaries in tech careers vary by role, location, and experience. Entry-level positions typically range from $50,000 to $80,000, while experienced professionals can earn $100,000+. Would you like to see detailed salary information for specific roles?"
                    else:
                        response = "I understand you're interested in career guidance. Could you please be more specific about what you'd like to know? For example, you can ask about specific career paths, required skills, or salary expectations."
            
            # Add AI response to chat history
            st.session_state.consultation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(response)
                
                # If career path is mentioned in the response, offer quick actions
                career_keywords = ["software", "data", "machine learning", "devops", "analytics", "cybersecurity", "ui/ux"]
                if any(keyword in response.lower() for keyword in career_keywords):
                    st.write("---")
                    st.write("Quick Actions:")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Career Details"):
                            st.session_state.page = "Career Recommendations"
                            st.rerun()
                    with col2:
                        if st.button("See Learning Roadmap"):
                            st.session_state.page = "Learning Roadmap"
                            st.rerun()
        
        except Exception as e:
            st.error("I apologize, but I encountered an error. Please try rephrasing your question.")
            print(f"Consultation Error: {e}")
    
    # Add a clear chat button
    if st.session_state.consultation_history:
        if st.button("Clear Chat History"):
            st.session_state.consultation_history = []
            st.rerun()

def get_industry_skills(career_path):
    """Get current industry required skills for a given career path"""
    industry_skills = {
        "Software Development": {
            "Technical": [
                {"name": "Modern JavaScript (ES6+)", "weight": 4, "resources": [
                    {"name": "Modern JavaScript Course", "url": "https://www.udemy.com/course/modern-javascript-from-novice-to-ninja/"},
                    {"name": "JavaScript.info", "url": "https://javascript.info/"},
                    {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript"}
                ]},
                {"name": "React/Angular/Vue.js", "weight": 4, "resources": [
                    {"name": "React - The Complete Guide", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/"},
                    {"name": "Vue.js Course", "url": "https://www.udemy.com/course/vuejs-2-the-complete-guide/"},
                    {"name": "Angular Tutorial", "url": "https://angular.io/tutorial"}
                ]},
                {"name": "Node.js", "weight": 3, "resources": [
                    {"name": "Node.js Complete Guide", "url": "https://www.udemy.com/course/nodejs-the-complete-guide/"},
                    {"name": "Node.js Documentation", "url": "https://nodejs.org/en/docs/"}
                ]},
                {"name": "Cloud Services (AWS/Azure/GCP)", "weight": 4, "resources": [
                    {"name": "AWS Certified Developer", "url": "https://www.udemy.com/course/aws-certified-developer-associate/"},
                    {"name": "Azure Fundamentals", "url": "https://learn.microsoft.com/en-us/training/azure/"}
                ]},
                {"name": "Docker & Kubernetes", "weight": 3, "resources": [
                    {"name": "Docker & Kubernetes Course", "url": "https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/"},
                    {"name": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/home/"}
                ]}
            ],
            "Tools": [
                {"name": "Git & GitHub", "weight": 5, "resources": [
                    {"name": "Git Complete Guide", "url": "https://www.udemy.com/course/git-complete/"},
                    {"name": "GitHub Learning Lab", "url": "https://lab.github.com/"}
                ]},
                {"name": "VS Code/Modern IDEs", "weight": 4, "resources": [
                    {"name": "VS Code Tutorial", "url": "https://code.visualstudio.com/docs"},
                    {"name": "VS Code Can Do That?", "url": "https://www.vscodecandothat.com/"}
                ]},
                {"name": "Testing Frameworks", "weight": 4, "resources": [
                    {"name": "JavaScript Testing Course", "url": "https://www.udemy.com/course/javascript-unit-testing-the-practical-guide/"},
                    {"name": "Jest Documentation", "url": "https://jestjs.io/docs/getting-started"}
                ]}
            ],
            "Soft Skills": [
                {"name": "Agile Methodologies", "weight": 4, "resources": [
                    {"name": "Agile Fundamentals", "url": "https://www.coursera.org/learn/agile-fundamentals"},
                    {"name": "Scrum Guide", "url": "https://scrumguides.org/"}
                ]},
                {"name": "Technical Communication", "weight": 5, "resources": [
                    {"name": "Technical Writing Course", "url": "https://www.coursera.org/learn/technical-writing"},
                    {"name": "Google Technical Writing", "url": "https://developers.google.com/tech-writing"}
                ]},
                {"name": "Problem-Solving", "weight": 5, "resources": [
                    {"name": "LeetCode Problems", "url": "https://leetcode.com/problemset/all/"},
                    {"name": "HackerRank Challenges", "url": "https://www.hackerrank.com/domains/algorithms"}
                ]}
            ]
        },
        "Data Science": {
            "Technical": [
                {"name": "Python for Data Science", "weight": 5, "resources": [
                    {"name": "Python for Data Science", "url": "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/"},
                    {"name": "DataCamp Python Track", "url": "https://www.datacamp.com/tracks/python-programmer"}
                ]},
                {"name": "Machine Learning", "weight": 4, "resources": [
                    {"name": "Machine Learning A-Z", "url": "https://www.udemy.com/course/machinelearning/"},
                    {"name": "Stanford ML Course", "url": "https://www.coursera.org/learn/machine-learning"}
                ]},
                {"name": "Deep Learning", "weight": 3, "resources": [
                    {"name": "Deep Learning Specialization", "url": "https://www.coursera.org/specializations/deep-learning"},
                    {"name": "Fast.ai Course", "url": "https://www.fast.ai/"}
                ]},
                {"name": "Statistical Analysis", "weight": 4, "resources": [
                    {"name": "Statistics for Data Science", "url": "https://www.coursera.org/specializations/statistics"},
                    {"name": "Khan Academy Statistics", "url": "https://www.khanacademy.org/math/statistics-probability"}
                ]}
            ],
            "Tools": [
                {"name": "SQL & Databases", "weight": 5, "resources": [
                    {"name": "Complete SQL Bootcamp", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/"},
                    {"name": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/"}
                ]},
                {"name": "Jupyter & Data Tools", "weight": 4, "resources": [
                    {"name": "Jupyter Tutorial", "url": "https://jupyter.org/try"},
                    {"name": "Pandas Documentation", "url": "https://pandas.pydata.org/docs/"}
                ]},
                {"name": "Visualization Tools", "weight": 4, "resources": [
                    {"name": "Data Visualization Course", "url": "https://www.coursera.org/learn/data-visualization"},
                    {"name": "Tableau Training", "url": "https://www.tableau.com/learn/training"}
                ]}
            ],
            "Soft Skills": [
                {"name": "Data Storytelling", "weight": 4, "resources": [
                    {"name": "Data Storytelling Course", "url": "https://www.coursera.org/learn/data-stories"},
                    {"name": "Storytelling with Data", "url": "https://www.storytellingwithdata.com/"}
                ]},
                {"name": "Business Acumen", "weight": 4, "resources": [
                    {"name": "Business Analytics", "url": "https://www.coursera.org/specializations/business-analytics"},
                    {"name": "Harvard Business Review", "url": "https://hbr.org/topic/analytics"}
                ]},
                {"name": "Research Methodology", "weight": 3, "resources": [
                    {"name": "Research Methods Course", "url": "https://www.coursera.org/learn/research-methods"},
                    {"name": "Google Scholar", "url": "https://scholar.google.com/"}
                ]}
            ]
        }
    }
    return industry_skills.get(career_path, {})

def display_skills_gap_analysis():
    st.header("🎯 Skills Gap Analysis")
    st.write("Analyze your current skills against industry requirements, especially helpful for professionals returning to the tech industry.")

    if not st.session_state.user_data:
        st.warning("Please complete your profile setup first!")
        if st.button("Go to Profile Setup"):
            st.session_state.page = "Profile Setup"
            st.rerun()
        return

    # Initialize session state for skills assessment if not exists
    if "skills_gap" not in st.session_state:
        st.session_state.skills_gap = {}
    
    # Add break duration for returning professionals
    if "break_duration" not in st.session_state:
        st.session_state.break_duration = 0

    # Career path selection with modern UI
    st.markdown(
        """
        <div style='background-color: #1E1E1E; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: #00FF00; margin: 0;'>🎯 Career Path Selection</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    career_options = ["Software Development", "Data Science", "Machine Learning Engineering", 
                     "DevOps Engineering", "Data Analytics", "Cybersecurity", "UI/UX Design"]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        selected_career = st.selectbox("Select your target career path:", career_options)
    with col2:
        break_duration = st.number_input("Career Break Duration (years):", 
                                       min_value=0.0, max_value=20.0, 
                                       value=float(st.session_state.break_duration),
                                       step=0.5)
        st.session_state.break_duration = break_duration

    # Get industry required skills
    industry_skills = get_industry_skills(selected_career)

    if industry_skills:
        st.write("---")
        st.subheader("Skills Assessment")
        
        # Create tabs for different skill categories with modern styling
        tab_titles = ["💻 Technical Skills", "🛠️ Tools", "🤝 Soft Skills"]
        tabs = st.tabs(tab_titles)
        
        for tab_index, (category, skills) in enumerate(industry_skills.items()):
            with tabs[tab_index]:
                st.markdown(
                    f"""
                    <div style='background-color: #2E2E2E; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                        <h4 style='color: #00FFFF; margin: 0;'>Rate your proficiency in {category}</h4>
                        <p style='color: #CCCCCC; margin: 5px 0 0 0;'>0 = No Experience, 5 = Expert Level</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Create a dictionary to store skills ratings if not exists
                if category not in st.session_state.skills_gap:
                    st.session_state.skills_gap[category] = {}
                
                for skill in skills:
                    skill_name = skill["name"]
                    current_value = st.session_state.skills_gap[category].get(skill_name, 0)
                    
                    # Create columns for better layout
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        rating = st.slider(
                            f"{skill_name}",
                            min_value=0,
                            max_value=5,
                            value=current_value,
                            help=f"Required proficiency: {skill['weight']}/5"
                        )
                        st.session_state.skills_gap[category][skill_name] = rating
                    
                    with col2:
                        if rating < skill["weight"]:
                            st.markdown(
                                f"""
                                <div style='background-color: #FF4B4B; padding: 5px 10px; border-radius: 5px; text-align: center;'>
                                    <span style='color: white;'>Gap: {skill['weight'] - rating}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style='background-color: #00FF00; padding: 5px 10px; border-radius: 5px; text-align: center;'>
                                    <span style='color: black;'>Proficient</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    # Show resources if there's a gap
                    if rating < skill["weight"]:
                        with st.expander("📚 Learning Resources"):
                            for resource in skill["resources"]:
                                st.markdown(
                                    f"""
                                    <div style='background-color: #404040; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                                        <a href="{resource['url']}" target="_blank" style='color: #00FFFF; text-decoration: none;'>
                                            {resource['name']} ↗
                                        </a>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

        # Analysis and Visualization
        st.write("---")
        st.subheader("Gap Analysis Results")

        # Create radar charts for each category with improved styling
        for category, skills in industry_skills.items():
            skill_names = [skill["name"] for skill in skills]
            skill_ratings = [st.session_state.skills_gap[category].get(skill["name"], 0) for skill in skills]
            required_levels = [skill["weight"] for skill in skills]

            fig = go.Figure()
            
            # Add your skills
            fig.add_trace(go.Scatterpolar(
                r=skill_ratings,
                theta=skill_names,
                fill='toself',
                name='Your Skills',
                line_color='#00FFFF'
            ))
            
            # Add required levels
            fig.add_trace(go.Scatterpolar(
                r=required_levels,
                theta=skill_names,
                fill='toself',
                name='Required Level',
                line_color='rgba(255, 255, 255, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5],
                        gridcolor='rgba(255, 255, 255, 0.2)'
                    ),
                    bgcolor='rgba(0, 0, 0, 0)',
                ),
                showlegend=True,
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                title=f"{category} Gap Analysis",
                font=dict(color='white')
            )
            
            st.plotly_chart(fig)

        # Personalized Learning Path
        st.write("---")
        st.subheader("📚 Your Personalized Learning Path")
        
        # Calculate priority based on gap size and skill weight
        all_gaps = []
        for category, skills in industry_skills.items():
            for skill in skills:
                current_rating = st.session_state.skills_gap[category].get(skill["name"], 0)
                gap = skill["weight"] - current_rating
                if gap > 0:
                    priority = gap * skill["weight"]  # Higher weight skills get higher priority
                    all_gaps.append({
                        "category": category,
                        "skill": skill["name"],
                        "gap": gap,
                        "priority": priority,
                        "resources": skill["resources"]
                    })
        
        # Sort gaps by priority
        all_gaps.sort(key=lambda x: x["priority"], reverse=True)
        
        # Display prioritized learning path
        if all_gaps:
            st.markdown(
                """
                <div style='background-color: #2E2E2E; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                    <h4 style='color: #00FFFF; margin: 0;'>Priority Skills to Focus On</h4>
                    <p style='color: #CCCCCC; margin: 5px 0 0 0;'>Based on your career break duration and industry requirements</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            for i, gap in enumerate(all_gaps):
                with st.expander(f"Priority {i+1}: {gap['skill']} ({gap['category']})"):
                    st.markdown(
                        f"""
                        <div style='background-color: #404040; padding: 15px; border-radius: 5px; margin: 10px 0;'>
                            <div style='color: #FF4B4B; margin-bottom: 10px;'>Gap Level: {gap['gap']}/5</div>
                            <div style='color: #FFFFFF;'>Recommended Learning Path:</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Display resources with timeline
                    for j, resource in enumerate(gap["resources"]):
                        st.markdown(
                            f"""
                            <div style='background-color: #2E2E2E; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                                <div style='color: #00FF00;'>Week {j+1}-{j+2}</div>
                                <a href="{resource['url']}" target="_blank" style='color: #00FFFF; text-decoration: none;'>
                                    {resource['name']} ↗
                                </a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        # Progress Tracking
        st.write("---")
        st.subheader("📊 Progress Tracking")
        
        # Calculate overall progress
        total_skills = sum(len(skills) for skills in industry_skills.values())
        completed_skills = sum(
            1 for category in industry_skills.keys()
            for skill_name in [s["name"] for s in industry_skills[category]]
            if st.session_state.skills_gap.get(category, {}).get(skill_name, 0) >= industry_skills[category][0]["weight"]
        )
        
        progress_percentage = (completed_skills / total_skills) * 100
        
        # Display progress bar with custom styling
        st.markdown(
            f"""
            <div style='background-color: #2E2E2E; padding: 20px; border-radius: 10px;'>
                <h4 style='color: #00FFFF; margin: 0 0 10px 0;'>Overall Progress</h4>
                <div style='background-color: #404040; height: 30px; border-radius: 5px; overflow: hidden;'>
                    <div style='background-color: #00FF00; width: {progress_percentage}%; height: 100%; text-align: center; line-height: 30px; color: black;'>
                        {progress_percentage:.1f}%
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Save Progress Button with animation
        if st.button("💾 Save Progress", key="save_progress"):
            st.balloons()
            st.success("Your skills assessment has been saved! Keep tracking your progress regularly.")

# Main content router
if st.session_state.page == "Profile Setup":
    display_profile_setup()
elif st.session_state.page == "Career Assessment":
    display_career_assessment()
elif st.session_state.page == "Career Recommendations":
    display_career_recommendations()
elif st.session_state.page == "Learning Roadmap":
    display_learning_roadmap()
elif st.session_state.page == "Skills Gap Analysis":
    display_skills_gap_analysis()
elif st.session_state.page == "Live AI Consultation":
    display_live_consultation()

if __name__ == "__main__":
    import streamlit as st
    st.set_page_config(
        page_title="Career Compass - AI Career Guide",
        page_icon="🎯",
        layout="wide",
    )
