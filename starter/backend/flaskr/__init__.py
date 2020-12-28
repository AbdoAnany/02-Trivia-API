import os
from flask import (Flask,
render_template,
request, Response,jsonify,abort,
flash, redirect,
url_for)
from flask_cors import CORS
import random

from .models import setup_db, Question, Category
from flask_sqlalchemy import SQLAlchemy

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
    

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
        'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
        "GET,POST,PATCH,DELETE,OPTIONS")
        return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route("/categories",methods=['GET'])
  def get_categories():     
        categories = Category.query.order_by(Category.type).all()
        formatted_category = {category.id: category.type for category in categories}
        return jsonify({
                'success': True,
                'categories': formatted_category
            }), 200
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def paginated_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [question.format() for question in questions]
        current_questions = questions[start:end]
        return current_questions

  @app.route('/questions')
  def get_questions():
        """
        Endpoint to handle GET requests for questions, including pagination (every 10 questions).
        This endpoint returns a list of questions, number of total questions, current category and categories.
        It returns a 404 code when the page is out of bound.
        """
        questions = Question.query.order_by(Question.id).all()
        total_questions = len(questions)
        current_questions = paginated_questions(request, questions)
        categories = Category.query.order_by(Category.id).all()
        categories_dict = {category.id: category.type for category in categories}
        return jsonify({
            'success': True,
            'total_questions': total_questions,
            'categories': categories_dict,
            'questions': current_questions
        }), 200
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 
  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            question.delete()
            return jsonify({
                'success': True,
                'deleted': id,
                'message': "Question successfully deleted"
            }), 200
        except Exception:
            abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
        """
        Endpoint to POST a new question. It requires the question and answer text, category, and difficulty score.
        A 422 status code is returned if the any of the json data is empty.
        """
        data = request.get_json()
        new_question = data.get('question', 'None')
        new_answer = data.get('answer', 'None')
        new_difficulty = data.get('difficulty', 'None')
        new_category = data.get('category', 'None')
        if new_question is None or new_answer is None or  new_difficulty is None or  new_category is None:
            abort(422)
        try:
            # create new question instance
            question = Question(
                question=new_question,
                answer=new_answer,
                difficulty=new_difficulty,
                category=new_category)

            question.insert()

            # return success message
            return jsonify({
                'success': True,
                'created': question.id,
                'total_questions': len(Question.query.all()),
                'message': "Question successfully created!"
            }), 201

        except Exception:
            abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
        """
        Endpoint to get questions based on a search term.
        This endpoint returns any questions for whom the search term is a substring of the question.
        """
        data = request.get_json()
        search_term = data.get('searchTerm', 'None')
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
        current_questions = paginated_questions(request, questions)
        try:
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            }), 200
        except Exception:
            abort(404)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
        """Endpoint to get questions based on category."""
        category = Category.query.filter_by(id=category_id).first()
        questions = Question.query.filter(Question.category==str(category.id)).all()
        current_questions = paginated_questions(request, questions)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'current_category': category.type
        })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz_question():
        """
        Endpoint to get questions for playing the quiz.
        This endpoint takes category and previous question parameters and return a random questions within the
        given category, if provided, and that is not one of the previous questions.
        """
        data = request.get_json()
        previous_questions = data.get('previous_questions', None)
        quiz_category = data.get('quiz_category', None)
        try:
            if quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category['id']).all()
            questions_list = [q.format() for q in questions if q.id not in previous_questions]
            if len(questions_list) == 0:
                next_question = None
            else:
                next_question = random.choice(questions_list)
            return jsonify({
                'success': True,
                'question': next_question
            }), 200

        except Exception:
            abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404
  @app.errorhandler(405)
  def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405
  @app.errorhandler(422)
  def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422


  return app

    