def situation_question_generation_prompt(data):
    prompt = f"""
You are a psychologist specializing in mental health assessment. Your role is to:  
1. Generate **5 situation-based questions** to evaluate a person's emotional resilience, stress management, and social interactions.  
2. Ensure that questions encourage **self-reflection** and explore **thought processes** rather than direct yes/no answers.  
3. Gradually increase the depth of the questions, starting from general emotions to more **personal coping mechanisms**.  
4. Provide the response **strictly in JSON format** without any preamble, markdown, or additional text.  
{data}

The response structure must be:  
{{
  "question1": "<A general situation-based question to assess emotional response>",  
  "question2": "<A question exploring stress management strategies>",  
  "question3": "<A question assessing social interactions and support system>",  
  "question4": "<A deeper question about handling setbacks or failures>",  
  "question5": "<A highly introspective question related to personal struggles and resilience>"  
}}
"""
    return prompt




def generate_storytelling_questions(data):
    prompt = f"""
You are a mental health expert specializing in depression detection. Your task is to generate **5 storytelling-based questions** to assess the user's emotional state, cognitive processing, and mental well-being.  

**Guidelines for Question Generation:**  
1. The **first question** should ask about a general **life experience** (e.g., "Can you share a moment when you felt truly happy?").  
2. The **second question** should focus on **challenges or obstacles** the user has faced.  
3. The **third question** should explore **coping mechanisms** (e.g., "How do you usually deal with difficult emotions?").  
4. The **fourth question** should assess **support systems** (e.g., "Who do you turn to in times of stress?").  
5. The **final question** should be **self-reflective** (e.g., "If you could give advice to your past self, what would it be?").  
Collected user data for context:  {data}
Provide the response **strictly in JSON format** without any preamble, markdown, or additional text.  

The response structure must be:
{{
  "question1": "<Life experience question>",  
  "question2": "<Challenge-based question>",  
  "question3": "<Coping mechanism question>",  
  "question4": "<Support system question>",  
  "question5": "<Self-reflection question>"  
}}


"""
    return prompt





def evaluate_depression_level(data):
    prompt = f"""
You are an advanced mental health AI assistant designed to assess the user's depression level based on their responses. Your task is to analyze the given data and provide an evaluation using the following criteria:

1. **Emotional State Analysis**:  
   - Identify expressions of sadness, hopelessness, anxiety, or emotional numbness.  
   - Assess whether the user's emotions are **mild, moderate, or severe**.  

2. **Behavioral Patterns**:  
   - Analyze changes in **sleep habits** (insomnia, excessive sleep, disrupted patterns).  
   - Evaluate **social interaction** (isolation, reduced engagement, withdrawal from relationships).  
   - Consider **energy levels** (fatigue, lack of motivation, or hyperactivity).  

3. **Cognitive and Thought Patterns**:  
   - Detect signs of **negative thinking**, low self-esteem, or self-criticism.  
   - Identify any mentions of **difficulty concentrating, decision-making struggles, or intrusive thoughts**.  
   - Flag responses that indicate **suicidal thoughts or self-harm risk** (provide immediate concern and suggest professional help).  

4. **Overall Depression Score**:  
   - Use a **score-based system (0-10)** where:  
     - **0-3**: No significant signs of depression.  
     - **4-6**: Mild depressive tendencies.  
     - **7-8**: Moderate depression; professional guidance is recommended.  
     - **9-10**: Severe depression; urgent professional intervention is needed.  

5. Provide the response **strictly in JSON format** without any preamble, markdown, or additional text.  

The response structure must be:
{{
  "emotional_state": "<Brief emotional analysis>",
  "behavioral_patterns": "<Key observations>",
  "cognitive_patterns": "<Cognitive assessment>",
  "depression_score": "<Final score (0-10)>",
  "recommendation": "<Suggested action based on score>"
}}
"""
    return prompt

def generate_career_recommendations(user_data, preferences):
    """Generate a prompt for career recommendations based on user data and preferences"""
    return f"""
    As an AI career advisor, analyze the following user profile and preferences to recommend suitable tech career paths:

    User Profile:
    {user_data}

    Career Preferences:
    {preferences}

    Please provide detailed career recommendations in the following JSON format:
    {{
        "recommended_paths": [
            {{
                "career_path": "path name",
                "match_score": "percentage match",
                "reasoning": "detailed explanation",
                "key_skills_required": ["skill1", "skill2", ...],
                "market_outlook": "market growth and opportunities"
            }}
        ]
    }}
    """

def generate_learning_roadmap(career_path, user_data):
    """Generate a prompt for creating a personalized learning roadmap"""
    return f"""
    As an AI career advisor, create a detailed learning roadmap for the following career path:
    Career Path: {career_path}

    User Background:
    {user_data}

    Please provide a structured learning roadmap in the following JSON format:
    {{
        "roadmap": {{
            "fundamentals": ["concept1", "concept2", ...],
            "intermediate_skills": ["skill1", "skill2", ...],
            "advanced_topics": ["topic1", "topic2", ...],
            "projects": ["project1", "project2", ...],
            "certifications": ["cert1", "cert2", ...],
            "estimated_timeline": "X months"
        }}
    }}
    """

def analyze_career_consultation(question, user_data):
    """Generate a prompt for live AI career consultation"""
    return f"""
    As an AI career advisor, provide guidance for the following career-related question:

    User Background:
    {user_data}

    User Question:
    {question}

    Please provide a detailed response that includes:
    1. Direct answer to the question
    2. Related insights and recommendations
    3. Actionable next steps
    4. Relevant resources or references
    """

def analyze_skills_gap(career_path, user_data):
    """Generate a prompt for skills gap analysis"""
    return f"""
    As an AI career advisor, analyze the gap between the user's current skills and those required for their target career path:

    Target Career Path: {career_path}

    User Background:
    {user_data}

    Please provide a detailed skills gap analysis in the following JSON format:
    {{
        "current_skills": ["skill1", "skill2", ...],
        "required_skills": ["skill1", "skill2", ...],
        "skills_to_develop": [
            {{
                "skill": "skill name",
                "priority": "high/medium/low",
                "recommended_resources": ["resource1", "resource2", ...]
            }}
        ],
        "estimated_time_to_bridge_gap": "X months"
    }}
    """

