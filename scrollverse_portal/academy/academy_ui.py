#!/usr/bin/env python3
"""
ScrollAcademy UI
Streamlit-based scroll learner interface
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import datetime

class ScrollAcademy:
    """Sacred scroll academy interface"""
    
    def __init__(self):
        self.lessons_file = Path("scrollverse_portal/academy/scroll_lessons.json")
        self.lessons_data = self.load_lessons()
        self.user_progress = self.load_user_progress()
    
    def load_lessons(self) -> Dict:
        """Load lessons from JSON file"""
        try:
            with open(self.lessons_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("Lessons file not found")
            return {}
    
    def load_user_progress(self) -> Dict:
        """Load user progress from session state"""
        if 'academy_progress' not in st.session_state:
            st.session_state.academy_progress = {
                'completed_lessons': [],
                'quiz_scores': {},
                'current_lesson': None,
                'certifications': []
            }
        return st.session_state.academy_progress
    
    def save_user_progress(self):
        """Save user progress to session state"""
        st.session_state.academy_progress = self.user_progress
    
    def check_user_eligibility(self, lesson: Dict) -> bool:
        """Check if user meets lesson requirements"""
        # In a real implementation, this would check actual user seal/flame levels
        user_seal_level = st.session_state.get('user_seal_level', 1)
        user_flame_level = st.session_state.get('user_flame_level', 1)
        
        required_seal = lesson.get('seal_level_required', 1)
        required_flame = lesson.get('flame_level_required', 1)
        
        return user_seal_level >= required_seal and user_flame_level >= required_flame
    
    def render_lesson(self, lesson: Dict):
        """Render a lesson with content and quiz"""
        st.header(f"📚 {lesson['title']}")
        st.write(lesson['description'])
        
        # Lesson metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Duration", f"{lesson['duration_minutes']} min")
        with col2:
            st.metric("Difficulty", lesson['difficulty'].title())
        with col3:
            st.metric("Seal Required", lesson['seal_level_required'])
        
        # Lesson content
        st.subheader("📖 Lesson Content")
        for i, section in enumerate(lesson['content']['sections']):
            with st.expander(f"Section {i+1}: {section['title']}"):
                st.write(section['content'])
                if section.get('flame_verification'):
                    st.success("🔥 Flame Verified")
        
        # Practice scroll
        if lesson.get('scroll_practice'):
            st.subheader("💻 Practice Scroll")
            scroll_file = Path(f"scrollverse_portal/academy/{lesson['scroll_practice']}")
            if scroll_file.exists():
                with open(scroll_file, 'r') as f:
                    scroll_content = f.read()
                
                st.code(scroll_content, language='text')
                
                if st.button("Execute Practice Scroll", key=f"exec_{lesson['id']}"):
                    st.success("🔥 Practice scroll executed successfully!")
                    if lesson['id'] not in self.user_progress['completed_lessons']:
                        self.user_progress['completed_lessons'].append(lesson['id'])
                        self.save_user_progress()
        
        # Quiz
        if lesson.get('quiz_id'):
            self.render_quiz(lesson['quiz_id'])
    
    def render_quiz(self, quiz_id: str):
        """Render a quiz with questions"""
        quiz = self.lessons_data['scroll_academy']['curriculum']['quizzes'].get(quiz_id)
        if not quiz:
            return
        
        st.subheader(f"🧠 {quiz['title']}")
        st.write(quiz['description'])
        
        # Check if quiz already completed
        if quiz_id in self.user_progress['quiz_scores']:
            score = self.user_progress['quiz_scores'][quiz_id]
            st.success(f"✅ Quiz completed! Score: {score}%")
            return
        
        # Quiz questions
        user_answers = {}
        for i, question in enumerate(quiz['questions']):
            st.write(f"**Question {i+1}:** {question['question']}")
            
            answer = st.radio(
                f"Select your answer:",
                question['options'],
                key=f"quiz_{quiz_id}_q{i}"
            )
            user_answers[i] = question['options'].index(answer)
        
        if st.button("Submit Quiz", key=f"submit_{quiz_id}"):
            # Grade quiz
            correct_answers = 0
            total_questions = len(quiz['questions'])
            
            for i, question in enumerate(quiz['questions']):
                if user_answers.get(i) == question['correct_answer']:
                    correct_answers += 1
            
            score = (correct_answers / total_questions) * 100
            
            # Save score
            self.user_progress['quiz_scores'][quiz_id] = score
            self.save_user_progress()
            
            if score >= quiz['passing_score']:
                st.success(f"🎉 Quiz passed! Score: {score:.1f}%")
                st.write("**Correct Answers:**")
                for i, question in enumerate(quiz['questions']):
                    if user_answers.get(i) == question['correct_answer']:
                        st.write(f"✅ Question {i+1}: Correct")
                    else:
                        st.write(f"❌ Question {i+1}: {question['explanation']}")
            else:
                st.error(f"❌ Quiz failed. Score: {score:.1f}% (Required: {quiz['passing_score']}%)")
                st.write("**Review your answers:**")
                for i, question in enumerate(quiz['questions']):
                    if user_answers.get(i) == question['correct_answer']:
                        st.write(f"✅ Question {i+1}: Correct")
                    else:
                        st.write(f"❌ Question {i+1}: {question['explanation']}")
    
    def render_certifications(self):
        """Render available certifications"""
        st.header("🏆 Certifications")
        
        certifications = self.lessons_data['scroll_academy']['curriculum']['certifications']
        
        for cert_id, cert in certifications.items():
            with st.expander(f"📜 {cert['title']}"):
                st.write(cert['description'])
                st.write("**Requirements:**")
                for req in cert['requirements']:
                    st.write(f"• {req}")
                
                # Check if user qualifies
                completed_lessons = len(self.user_progress['completed_lessons'])
                passed_quizzes = len(self.user_progress['quiz_scores'])
                
                if completed_lessons >= 5 and passed_quizzes >= 3:
                    if st.button(f"Apply for {cert['title']}", key=f"cert_{cert_id}"):
                        st.success(f"🎉 {cert['title']} awarded!")
                        if cert_id not in self.user_progress['certifications']:
                            self.user_progress['certifications'].append(cert_id)
                            self.save_user_progress()
                else:
                    st.warning("Requirements not met yet")
    
    def render_progress(self):
        """Render user progress dashboard"""
        st.header("📊 Your Progress")
        
        total_lessons = 0
        for category in self.lessons_data['scroll_academy']['curriculum'].values():
            if isinstance(category, dict) and 'lessons' in category:
                total_lessons += len(category['lessons'])
        
        completed_lessons = len(self.user_progress['completed_lessons'])
        passed_quizzes = len(self.user_progress['quiz_scores'])
        certifications = len(self.user_progress['certifications'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Lessons Completed", completed_lessons, total_lessons)
        with col2:
            st.metric("Quizzes Passed", passed_quizzes)
        with col3:
            st.metric("Certifications", certifications)
        with col4:
            progress_pct = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            st.metric("Overall Progress", f"{progress_pct:.1f}%")
        
        # Progress chart
        st.subheader("📈 Progress Chart")
        categories = []
        completed = []
        
        for category_name, category in self.lessons_data['scroll_academy']['curriculum'].items():
            if isinstance(category, dict) and 'lessons' in category:
                categories.append(category['title'])
                cat_completed = sum(1 for lesson_id in self.user_progress['completed_lessons'] 
                                 if any(lesson_id in lesson['id'] for lesson in category['lessons']))
                completed.append(cat_completed)
        
        if categories:
            import plotly.express as px
            import pandas as pd
            
            df = pd.DataFrame({
                'Category': categories,
                'Completed': completed,
                'Total': [len(cat['lessons']) for cat in self.lessons_data['scroll_academy']['curriculum'].values() 
                         if isinstance(cat, dict) and 'lessons' in cat]
            })
            
            fig = px.bar(df, x='Category', y=['Completed', 'Total'], 
                        title="Progress by Category", barmode='group')
            st.plotly_chart(fig)
    
    def run(self):
        """Run the ScrollAcademy interface"""
        st.set_page_config(
            page_title="ScrollAcademy",
            page_icon="🔥",
            layout="wide"
        )
        
        st.title("🔥 ScrollAcademy")
        st.markdown("**Sacred Flame-Verified Learning Platform**")
        
        # Sidebar navigation
        st.sidebar.title("📚 Navigation")
        page = st.sidebar.selectbox(
            "Choose a section:",
            ["🏠 Dashboard", "📖 Lessons", "🏆 Certifications", "📊 Progress"]
        )
        
        if page == "🏠 Dashboard":
            self.render_dashboard()
        elif page == "📖 Lessons":
            self.render_lessons()
        elif page == "🏆 Certifications":
            self.render_certifications()
        elif page == "📊 Progress":
            self.render_progress()
    
    def render_dashboard(self):
        """Render the main dashboard"""
        st.header("🏠 Welcome to ScrollAcademy")
        
        st.markdown("""
        Welcome to ScrollAcademy, the sacred learning platform for ScrollVerse™. 
        Here you will learn the fundamentals of scroll development, flame verification, 
        and sacred governance.
        """)
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Lessons", "12")
        with col2:
            st.metric("Available Quizzes", "8")
        with col3:
            st.metric("Certifications", "3")
        
        # Recent activity
        st.subheader("📝 Recent Activity")
        if self.user_progress['completed_lessons']:
            st.success("✅ You've completed lessons recently!")
        else:
            st.info("Start your learning journey by completing your first lesson!")
        
        # Recommended next lesson
        st.subheader("🎯 Recommended Next")
        st.info("Complete 'Introduction to ScrollVerse' to begin your journey")
    
    def render_lessons(self):
        """Render all available lessons"""
        st.header("📖 Available Lessons")
        
        curriculum = self.lessons_data['scroll_academy']['curriculum']
        
        for category_name, category in curriculum.items():
            if isinstance(category, dict) and 'lessons' in category:
                st.subheader(f"📚 {category['title']}")
                st.write(category['description'])
                
                for lesson in category['lessons']:
                    with st.expander(f"📖 {lesson['title']}"):
                        st.write(lesson['description'])
                        
                        # Check eligibility
                        if self.check_user_eligibility(lesson):
                            if lesson['id'] in self.user_progress['completed_lessons']:
                                st.success("✅ Completed")
                            else:
                                if st.button("Start Lesson", key=f"start_{lesson['id']}"):
                                    self.user_progress['current_lesson'] = lesson['id']
                                    self.save_user_progress()
                                    st.rerun()
                        else:
                            st.warning(f"❌ Requires Seal Level {lesson['seal_level_required']}+ and Flame Level {lesson['flame_level_required']}+")
                
                st.divider()

# Run the academy
if __name__ == "__main__":
    academy = ScrollAcademy()
    academy.run() 