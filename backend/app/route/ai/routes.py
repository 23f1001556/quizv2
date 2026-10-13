from flask import Blueprint, jsonify, request
from app.auth.decors import login_required
from app.ai.services import (
    GeminiUnavailableError,
    analyze_quiz_performance,
    generate_questions,
    process_media,
)
import os
import werkzeug.utils

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

@ai_bp.route("/analyze_performance", methods=["POST"])
@login_required 
def analyze_perf():
    try:
        data = request.get_json()
        quiz_ids = data.get("quiz_ids", [])
        
        if not quiz_ids:
            return jsonify({"message": "No quizzes selected"}), 400

        from app.models.score import Scores
        from app.models.quiz import Quiz
        from app.models.users import User
        
        user = User.query.get(request.user_id)
        
        performance_data = []
        
        for q_id in quiz_ids:
            # Get latest score for this quiz
            score = Scores.query.filter_by(user_id=request.user_id, quiz_id=q_id).order_by(Scores.id.desc()).first()
            quiz = Quiz.query.get(q_id)
            
            if score and quiz:
                # Simulating "weak concepts" retrieval. 
                # In a real app with granular question tagging, we'd query wrong answers tags.
                # Here we default to the Quiz name/remarks as context.
                performance_data.append({
                    "quiz_title": quiz.name,
                    "score": f"{score.total_score}", # Total questions count isn't in Score model, but AI can work with raw score
                    "weak_concepts": [quiz.name, quiz.remarks] # Using metadata as proxy for concepts
                })
        
        if not performance_data:
             return jsonify({"message": "No score data found for selected quizzes"}), 404

        analysis = analyze_quiz_performance(user.user_name, performance_data)
        
        # Save history
        from app.models.Ai.history import AIHistory
        from app.configs.extensions import db
        
        history = AIHistory(
            user_id=request.user_id,
            action="analyze_performance",
            prompt=f"Analyzed {len(quiz_ids)} quizzes",
            response=str(analysis)
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({"analysis": analysis}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/generate_study_material", methods=["POST"])
@login_required
def gen_study_material():
    try:
        data = request.get_json()
        topic = data.get("topic")
        weakness_context = data.get("context", "")

        from app.ai.services import generate_study_material
        material = generate_study_material(topic, weakness_context)
        
        # Save history
        from app.models.Ai.history import AIHistory
        from app.configs.extensions import db
        history = AIHistory(
            user_id=request.user_id,
            action="generate_study_material",
            prompt=f"Study Guide: {topic}",
            response=str(material)
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({"material": material}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/generate_questions", methods=["POST"])
@login_required # Added login required
def gen_questions():
    try:
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"message": "Request body must be a JSON object"}), 400

        topic = data.get("topic")
        if not isinstance(topic, str) or not topic.strip() or len(topic) > 300:
            return jsonify({"message": "Topic must be between 1 and 300 characters"}), 400

        try:
            count = int(data.get("count", 5))
        except (TypeError, ValueError):
            return jsonify({"message": "Question count must be an integer from 1 to 15"}), 400
        if not 1 <= count <= 15:
            return jsonify({"message": "Question count must be between 1 and 15"}), 400

        difficulty = data.get("difficulty", "Medium")
        if not isinstance(difficulty, str) or difficulty not in {"Easy", "Medium", "Hard"}:
            return jsonify({"message": "Difficulty must be Easy, Medium, or Hard"}), 400

        q_type = data.get("type", "single")

        questions_raw = generate_questions(topic.strip(), count, q_type, difficulty)
        
        # Clean and parse JSON
        import json
        import re
        
        cleaned = re.sub(r'```json\s*|\s*```', '', questions_raw)
        try:
            questions_json = json.loads(cleaned)
            questions = questions_json.get("questions", [])
        except json.JSONDecodeError:
            # Return raw response for debugging if parsing fails
            return jsonify({
                "message": "Failed to parse AI response. The model might be overloaded or returned invalid JSON.",
                "raw_response": questions_raw
            }), 500
        
        # Save history
        from app.models.Ai.history import AIHistory
        from app.configs.extensions import db
        history = AIHistory(
            user_id=request.user_id,
            action="generate_questions",
            prompt=f"Generate {count} {q_type} questions on {topic}",
            response=str(questions_raw)
        )
        db.session.add(history)
        db.session.commit()

        return jsonify({"questions": questions}), 200
    except TimeoutError as e:
        return jsonify({"message": str(e)}), 504
    except GeminiUnavailableError as e:
        return jsonify({"message": str(e)}), 503
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/upload_pdf", methods=["POST"])
@login_required
def upload_media():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        action = request.form.get("action", "explain")
        query = request.form.get("query")
        difficulty = request.form.get("difficulty", "Medium")
        try:
            count = int(request.form.get("count", 5))
        except (TypeError, ValueError):
            return jsonify({"message": "Question count must be an integer from 1 to 15"}), 400
        if not 1 <= count <= 15:
            return jsonify({"message": "Question count must be between 1 and 15"}), 400

        if file:
            filename = werkzeug.utils.secure_filename(file.filename)
            upload_folder = os.path.join(os.getcwd(), 'temp_uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Process media (PDF or Image)
            from app.ai.services import process_media
            result = process_media(filepath, action, query, difficulty, count)

            # Cleanup
            os.remove(filepath)

            # Save history
            from app.models.Ai.history import AIHistory
            from app.configs.extensions import db
            history = AIHistory(
                 user_id=request.user_id,
                 action=f"media_{action}",
                 prompt=f"File: {filename}, Difficulty: {difficulty}, Count: {count}",
                 response=str(result)
            )
            db.session.add(history)
            db.session.commit()

            return jsonify({"result": result}), 200
    
    except TimeoutError as e:
        return jsonify({"message": str(e)}), 504
    except GeminiUnavailableError as e:
        return jsonify({"message": str(e)}), 503
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/history", methods=["GET", "DELETE"])
@login_required
def handle_ai_history():
    from app.models.Ai.history import AIHistory
    from app.configs.extensions import db

    if request.method == "DELETE":
        try:
            db.session.query(AIHistory).filter_by(user_id=request.user_id).delete()
            db.session.commit()
            return jsonify({"message": "History cleared"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    try:
        history = AIHistory.query.filter_by(user_id=request.user_id).order_by(AIHistory.created_at.desc()).all()
        
        output = []
        for h in history:
            # Clean prompt if it contains "Query: None"
            clean_prompt = h.prompt
            if clean_prompt and "Query: None" in clean_prompt:
                 # It might be "File: xxx, Query: None"
                 clean_prompt = clean_prompt.replace(", Query: None", "")
            
            output.append({
                "id": h.id,
                "action": h.action,
                "prompt": clean_prompt,
                "response": h.response,
                "created_at": h.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify({"history": output}), 200
    except Exception as e:
         return jsonify({"message": str(e)}), 500

@ai_bp.route("/save_analysis", methods=["POST"])
@login_required
def save_analysis():
    try:
        data = request.get_json()

        title = data.get("title")
        content = data.get("content")
        subject_id = data.get("subject_id")
        chapter_id = data.get("chapter_id")
        quiz_name = data.get("quiz_name")

        if not title or not content or not subject_id:

            return jsonify({"message": "Missing required fields"}), 400

        from app.models.study_material import StudyMaterial
        from app.configs.extensions import db

        material = StudyMaterial(
            title=title,
            content=content,
            subject_id=subject_id,
            chapter_id=chapter_id,
            quiz_name=quiz_name,
            user_id=request.user_id
        )
        db.session.add(material)
        db.session.commit()

        return jsonify({"message": "Study material saved successfully", "id": material.id}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/get_study_materials", methods=["GET"])
@login_required
def get_study_materials():
    try:
        subject_id = request.args.get("subject_id")
        chapter_id = request.args.get("chapter_id")
        
        from app.models.study_material import StudyMaterial
        
        query = StudyMaterial.query.filter_by(user_id=request.user_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
            
        materials = query.order_by(StudyMaterial.created_at.desc()).all()
        
        output = [{
            "id": m.id,
            "title": m.title,
            "content": m.content,
            "subject_id": m.subject_id,
            "chapter_id": m.chapter_id,
            "quiz_name": m.quiz_name,
            "created_at": m.created_at.strftime('%Y-%m-%d %H:%M')
        } for m in materials]
        
        return jsonify({"materials": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ai_bp.route("/delete_study_material/<int:id>", methods=["DELETE"])
@login_required
def delete_study_material(id):
    try:
        data = request.get_json()
        password = data.get("password")
        
        if not password:
            return jsonify({"message": "Password is required"}), 400
            
        from app.models.users import User
        from app.models.study_material import StudyMaterial
        from app.configs.extensions import db
        import bcrypt
        
        user = User.query.get(request.user_id)
        if not user or not user.check_password(password):
             return jsonify({"message": "Invalid password"}), 403
             
        material = StudyMaterial.query.get(id)
        if not material:
             return jsonify({"message": "Material not found"}), 404
             
        if material.user_id != request.user_id:
             return jsonify({"message": "Access denied"}), 403
             
        db.session.delete(material)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
