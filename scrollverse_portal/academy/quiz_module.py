#!/usr/bin/env python3
"""
ScrollAcademy Quiz Module
Flame-sealed multiple choice validation
"""

import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

@dataclass
class QuizQuestion:
    """Represents a quiz question with flame verification"""
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    flame_seal: str
    difficulty: str = "medium"
    points: int = 10

@dataclass
class QuizResult:
    """Represents a quiz result with flame verification"""
    quiz_id: str
    user_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken: float
    flame_seal: str
    timestamp: float
    passed: bool

class FlameSealedQuiz:
    """Flame-sealed quiz validation system"""
    
    def __init__(self, secret_key: str = "scrollverse_flame_secret"):
        self.secret_key = secret_key.encode('utf-8')
        self.quizzes_file = Path("scrollverse_portal/academy/scroll_lessons.json")
        self.results_file = Path("scrollverse_portal/academy/quiz_results.json")
        self.quizzes = self.load_quizzes()
        self.results = self.load_results()
    
    def load_quizzes(self) -> Dict:
        """Load quizzes from lessons file"""
        try:
            with open(self.quizzes_file, 'r') as f:
                data = json.load(f)
                return data.get('scroll_academy', {}).get('quizzes', {})
        except FileNotFoundError:
            return {}
    
    def load_results(self) -> List[Dict]:
        """Load quiz results"""
        try:
            with open(self.results_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_results(self):
        """Save quiz results"""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def generate_flame_seal(self, data: str) -> str:
        """Generate flame seal for data integrity"""
        message = data.encode('utf-8')
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        return f"flame_{signature[:16]}"
    
    def verify_flame_seal(self, data: str, seal: str) -> bool:
        """Verify flame seal integrity"""
        expected_seal = self.generate_flame_seal(data)
        return seal == expected_seal
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Get quiz by ID with flame verification"""
        quiz = self.quizzes.get(quiz_id)
        if not quiz:
            return None
        
        # Verify flame seal if present
        if quiz.get('flame_verification'):
            quiz_data = json.dumps(quiz, sort_keys=True)
            if not self.verify_flame_seal(quiz_data, quiz.get('flame_seal', '')):
                raise ValueError("Quiz flame seal verification failed")
        
        return quiz
    
    def parse_quiz_questions(self, quiz: Dict) -> List[QuizQuestion]:
        """Parse quiz questions with flame verification"""
        questions = []
        
        for question_data in quiz.get('questions', []):
            # Generate flame seal for question
            question_text = question_data['question']
            flame_seal = self.generate_flame_seal(question_text)
            
            question = QuizQuestion(
                id=question_data['id'],
                question=question_text,
                options=question_data['options'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                flame_seal=flame_seal
            )
            questions.append(question)
        
        return questions
    
    def grade_quiz(self, quiz_id: str, user_answers: Dict[int, int], 
                   user_id: str, time_taken: float) -> QuizResult:
        """Grade quiz with flame verification"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError(f"Quiz {quiz_id} not found")
        
        questions = self.parse_quiz_questions(quiz)
        total_questions = len(questions)
        correct_answers = 0
        
        # Grade each question
        for i, question in enumerate(questions):
            user_answer = user_answers.get(i)
            if user_answer == question.correct_answer:
                correct_answers += 1
        
        # Calculate score
        score = (correct_answers / total_questions) * 100
        passed = score >= quiz.get('passing_score', 80)
        
        # Generate flame seal for result
        result_data = f"{quiz_id}:{user_id}:{score}:{correct_answers}:{total_questions}"
        flame_seal = self.generate_flame_seal(result_data)
        
        result = QuizResult(
            quiz_id=quiz_id,
            user_id=user_id,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            time_taken=time_taken,
            flame_seal=flame_seal,
            timestamp=time.time(),
            passed=passed
        )
        
        # Save result
        self.results.append({
            'quiz_id': result.quiz_id,
            'user_id': result.user_id,
            'score': result.score,
            'total_questions': result.total_questions,
            'correct_answers': result.correct_answers,
            'time_taken': result.time_taken,
            'flame_seal': result.flame_seal,
            'timestamp': result.timestamp,
            'passed': result.passed
        })
        self.save_results()
        
        return result
    
    def get_user_results(self, user_id: str) -> List[QuizResult]:
        """Get all quiz results for a user"""
        user_results = []
        for result_data in self.results:
            if result_data['user_id'] == user_id:
                result = QuizResult(
                    quiz_id=result_data['quiz_id'],
                    user_id=result_data['user_id'],
                    score=result_data['score'],
                    total_questions=result_data['total_questions'],
                    correct_answers=result_data['correct_answers'],
                    time_taken=result_data['time_taken'],
                    flame_seal=result_data['flame_seal'],
                    timestamp=result_data['timestamp'],
                    passed=result_data['passed']
                )
                user_results.append(result)
        
        return sorted(user_results, key=lambda x: x.timestamp, reverse=True)
    
    def get_quiz_statistics(self, quiz_id: str) -> Dict:
        """Get statistics for a quiz"""
        quiz_results = [r for r in self.results if r['quiz_id'] == quiz_id]
        
        if not quiz_results:
            return {
                'total_attempts': 0,
                'average_score': 0,
                'pass_rate': 0,
                'total_passed': 0,
                'total_failed': 0
            }
        
        total_attempts = len(quiz_results)
        total_passed = sum(1 for r in quiz_results if r['passed'])
        total_failed = total_attempts - total_passed
        average_score = sum(r['score'] for r in quiz_results) / total_attempts
        pass_rate = (total_passed / total_attempts) * 100
        
        return {
            'total_attempts': total_attempts,
            'average_score': round(average_score, 2),
            'pass_rate': round(pass_rate, 2),
            'total_passed': total_passed,
            'total_failed': total_failed
        }
    
    def validate_quiz_integrity(self, quiz_id: str) -> bool:
        """Validate quiz integrity with flame verification"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return False
        
        # Check if quiz has flame verification
        if not quiz.get('flame_verification'):
            return False
        
        # Verify all questions have proper flame seals
        questions = self.parse_quiz_questions(quiz)
        for question in questions:
            if not self.verify_flame_seal(question.question, question.flame_seal):
                return False
        
        return True
    
    def create_quiz_summary(self, quiz_id: str) -> Dict:
        """Create a summary of quiz performance"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return {}
        
        stats = self.get_quiz_statistics(quiz_id)
        questions = self.parse_quiz_questions(quiz)
        
        return {
            'quiz_id': quiz_id,
            'title': quiz.get('title', ''),
            'description': quiz.get('description', ''),
            'total_questions': len(questions),
            'passing_score': quiz.get('passing_score', 80),
            'flame_verification': quiz.get('flame_verification', False),
            'statistics': stats
        }
    
    def export_quiz_results(self, format: str = 'json') -> str:
        """Export all quiz results"""
        if format == 'json':
            return json.dumps(self.results, indent=2)
        elif format == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'Quiz ID', 'User ID', 'Score', 'Total Questions', 
                'Correct Answers', 'Time Taken', 'Flame Seal', 
                'Timestamp', 'Passed'
            ])
            
            # Write data
            for result in self.results:
                writer.writerow([
                    result['quiz_id'], result['user_id'], result['score'],
                    result['total_questions'], result['correct_answers'],
                    result['time_taken'], result['flame_seal'],
                    result['timestamp'], result['passed']
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

# Example usage
if __name__ == "__main__":
    # Initialize flame-sealed quiz system
    quiz_system = FlameSealedQuiz()
    
    # Example quiz grading
    user_answers = {0: 1, 1: 1}  # User selected option 1 for both questions
    result = quiz_system.grade_quiz(
        quiz_id="quiz-fund-001",
        user_answers=user_answers,
        user_id="test_user",
        time_taken=120.5
    )
    
    print(f"Quiz Result: {result.score}% - {'PASSED' if result.passed else 'FAILED'}")
    print(f"Flame Seal: {result.flame_seal}") 