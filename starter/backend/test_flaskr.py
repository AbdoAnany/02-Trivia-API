import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from .flaskr import create_app
from .models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path ='postgres://{}:{}@{}/{}'.format('postgres','postgres','localhost:5432',database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)
    def test_delete_question(self):
        question = Question(
            question='Will this be deleted?',
            answer='Yes',
            difficulty=1,
            category='1')
        question.insert()
        id = question.id
        response = self.client().delete('/questions/{}'.format(id))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertEqual(data['message'], "Question successfully deleted")

    def test_delete_invalid_question(self):
        """Tests deletion of a non-existing question."""
        response = self.client().delete('/questions/123456')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_delete_question_with_invalid_id(self):
        response = self.client().delete('/questions/sushma')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_new_questions(self):
        self.new_question = {
            'question': 'What is the capital of India?',
            'answer': 'New Delhi',
            'difficulty': 2,
            'category': 3,}
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_create_invalid_question(self):
        request_data = {
            'question': '',
            'answer': '',
            'difficulty': 'sushma',
            'category': 1,}
        response = self.client().post('/questions', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_search_questions(self):
        request_data = {'searchTerm': 'artist',}
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
    def test_invalid_search_term(self):
        request_data = {'searchTerm': 'akkadbakkad',}
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue((data['questions']))
        self.assertEqual(data['current_category'], 'Art')

    def test_invalid_category(self):
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    def test_quiz_play(self):
        request_data = {
            'previous_questions': [2, 7],
            'quiz_category': {'type': 'Geography','id': 3}}
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 2)
        self.assertNotEqual(data['question']['id'], 7)
        self.assertEqual(data['question']['category'], 3)

    def test_invalid_quiz_play(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')
    def test_insert_question(self):
        sample_question = {
        'question': 'What is the color of sky',
        'answer': 'blue',
        'category': 1,
        'difficulty': 1}
        response = self.client().post('/questions', json=sample_question,content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()