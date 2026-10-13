from flask import Blueprint, jsonify, request
from app.models.users import User
from app.models.activity import ActivityLog
from app.configs.extensions import db
from app.auth.decors import protect_super_admin, login_required, admin_required

users_bp = Blueprint("users", __name__, url_prefix="/users")

@users_bp.route("/getusers", methods=["GET"])
@login_required
@admin_required
def get_users():
    try:
        users = User.query.all()
        output = []
        for user in users:
            output.append({
                "id": user.id,
                "user_name": user.user_name,
                "email": user.email,
                "fullname": user.fullname,
                "qualification": user.qualification,
                "dob": user.dob.strftime('%Y-%m-%d') if user.dob else None,
                "isadmin": user.isadmin,
                "is_blocked": user.is_blocked if hasattr(user, 'is_blocked') else False
            })
        return jsonify({"users": output}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/getuser/<int:id>", methods=["GET"])
@login_required
@protect_super_admin
def get_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "user_name": user.user_name,
            "email": user.email,
            "fullname": user.fullname,
            "qualification": user.qualification,
            "dob": user.dob.strftime('%Y-%m-%d') if user.dob else None,
            "isadmin": user.isadmin,
            "is_blocked": user.is_blocked if hasattr(user, 'is_blocked') else False
        }
        return jsonify({"user": user_data}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/updateuser/<int:id>", methods=["PUT"])
@login_required
@admin_required
@protect_super_admin
def update_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        data = request.get_json()
        
        if "fullname" in data:
            user.fullname = data["fullname"]
        if "qualification" in data:
            user.qualification = data["qualification"]
        db.session.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/deleteuser/<int:id>", methods=["DELETE"])
@login_required
@admin_required
@protect_super_admin
def delete_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        db.session.delete(user)
        ActivityLog.log(request.user_id, "Deleted User", f"Deleted user: {user.user_name} ({user.email})")
        db.session.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/blockuser/<int:id>", methods=["POST"])
@login_required
@admin_required
@protect_super_admin
def block_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "User not found"}), 404
            
        if hasattr(user, 'is_blocked'):
            user.is_blocked = not user.is_blocked
            action = "Blocked User" if user.is_blocked else "Unblocked User"
            ActivityLog.log(request.user_id, action, f"{action}: {user.user_name}")
            db.session.commit()
            return jsonify({"message": f"User {action.lower()} successfully", "is_blocked": user.is_blocked}), 200
        else:
             return jsonify({"message": "Block functionality not supported by model"}), 501
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/dashboard_stats", methods=["GET"])
@login_required
def dashboard_stats():
    try:
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt, MockQuiz
        from app.models.quiz import Quiz
        from app.models.question import Question
        from app.models.mock_quiz import MockQuestion
        from datetime import datetime

        user_id = request.user_id
        
        # 1. Standard Quizzes
        std_scores = Scores.query.filter_by(user_id=user_id).all()
        # 2. Mock Attempts
        mock_attempts = MockAttempt.query.filter_by(user_id=user_id).all()

        total_quizzes = len(std_scores) + len(mock_attempts)
        
        total_obtained = 0
        total_possible = 0
        
        # Calculate Standard Quiz Stats
        for s in std_scores:
            total_obtained += s.total_score
            # Calculate max possible for this quiz (count questions)
            q_count = Question.query.filter_by(quiz_id=s.quiz_id).count()
            total_possible += (q_count if q_count > 0 else 1) # Avoid div by zero

        # Calculate Mock Quiz Stats
        for m in mock_attempts:
            total_obtained += m.score
            # Calculate max possible
            # We need to query MockQuestions for this mock_quiz_id
            mq_count = MockQuestion.query.filter_by(mock_quiz_id=m.mock_quiz_id).count()
            # Assuming 1 mark per question for now implies total_possible += mq_count
            # If we used marks, we'd sum marks. Let's assume 1 mark per question for consistency in this quick refactor.
            total_possible += (mq_count if mq_count > 0 else 1)

        avg_score = 0
        if total_possible > 0:
            avg_score = round((total_obtained / total_possible) * 100, 1)

        # Days Active
        # Find earliest activity or fallback to 1
        dates = [s.timestamp for s in std_scores] + [m.submitted_at for m in mock_attempts]
        days_active = 0
        if dates:
            first_activity = min(dates)
            delta = datetime.utcnow() - first_activity
            days_active = delta.days + 1 # Include today
        
        # Recent Activity
        activities = []
        for s in std_scores:
            quiz = Quiz.query.get(s.quiz_id)
            activities.append({
                "type": "Standard",
                "title": quiz.name if quiz else "Unknown Quiz",
                "score": s.total_score,
                "date": s.timestamp
            })
        for m in mock_attempts:
            mq = MockQuiz.query.get(m.mock_quiz_id)
            activities.append({
                "type": "Mock",
                "title": mq.title if mq else "Unknown Mock Quiz",
                "score": m.score,
                "date": m.submitted_at
            })
            
        # Sort by date desc
        activities.sort(key=lambda x: x['date'], reverse=True)
        recent = activities[:5]
        # Format dates for JSON
        for a in recent:
            a['date'] = a['date'].strftime('%Y-%m-%d %H:%M')

        return jsonify({
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "days_active": days_active,
            "recent_activity": recent
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    try:
        from app.models.score import Scores
        from app.models.mock_quiz import MockAttempt, MockQuiz
        from app.models.quiz import Quiz
        from app.models.question import Question
        from app.models.mock_quiz import MockQuestion
        from datetime import datetime

        user_id = request.user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        activities = []
        # Calculate Stats (Similar logic to dashboard_stats)
        std_scores = Scores.query.filter_by(user_id=user_id).all()
        mock_attempts = MockAttempt.query.filter_by(user_id=user_id).all()

        total_quizzes = len(std_scores) + len(mock_attempts)
        
        total_obtained = 0
        total_possible = 0
        
        for s in std_scores:
            total_obtained += s.total_score
            q_count = Question.query.filter_by(quiz_id=s.quiz_id).count()
            total_possible += (q_count if q_count > 0 else 1)

        for m in mock_attempts:
            total_obtained += m.score
            mq_count = MockQuestion.query.filter_by(mock_quiz_id=m.mock_quiz_id).count()
            total_possible += (mq_count if mq_count > 0 else 1)

        avg_score = 0
        if total_possible > 0:
            avg_score = round((total_obtained / total_possible) * 100, 1)

        dates = [s.timestamp for s in std_scores] + [m.submitted_at for m in mock_attempts]
        days_active = 0
        if dates:
            first_activity = min(dates)
            delta = datetime.utcnow() - first_activity
            days_active = delta.days + 1 
        
        if user.isadmin:
            # For admin, show action tokens
            admin_logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
            for log in admin_logs:
                activities.append({
                    "type": "Action",
                    "title": log.action,
                    "details": log.details,
                    "date": log.timestamp.strftime('%Y-%m-%d %H:%M')
                })
        else:
            # For regular users, show quiz attempts
            for s in std_scores:
                quiz = Quiz.query.get(s.quiz_id)
                activities.append({
                    "type": "Standard",
                    "title": quiz.name if quiz else "Unknown Quiz",
                    "score": s.total_score,
                    "date": s.timestamp
                })
            for m in mock_attempts:
                mq = MockQuiz.query.get(m.mock_quiz_id)
                activities.append({
                    "type": "Mock",
                    "title": mq.title if mq else "Unknown Mock Quiz",
                    "score": m.score,
                    "date": m.submitted_at
                })
            
            activities.sort(key=lambda x: x['date'], reverse=True)
            activities = activities[:10]
            for a in activities:
                if isinstance(a['date'], datetime):
                    a['date'] = a['date'].strftime('%Y-%m-%d %H:%M')
        
        recent = activities # Already formatted and limited

        user_data = {
            "id": user.id,
            "username": user.user_name,
            "email": user.email,
            "fullname": user.fullname,
            "qualification": user.qualification,
            "dob": user.dob.strftime('%Y-%m-%d') if user.dob else "",
            "isadmin": user.isadmin
        }

        stats = {
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "days_active": days_active,
            "recent_activity": recent
        }

        return jsonify({"user": user_data, "stats": stats}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@users_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    try:
        user_id = request.user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        data = request.get_json()

        if "fullname" in data:
            user.fullname = data["fullname"]
        if "qualification" in data:
            user.qualification = data["qualification"]
        if "dob" in data:
            try:
                from datetime import datetime
                if data["dob"]:
                    user.dob = datetime.strptime(data["dob"], '%Y-%m-%d').date()
            except ValueError:
                pass # Ignore invalid date format

        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500