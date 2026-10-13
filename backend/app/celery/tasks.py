from celery import shared_task
from flask_mail import Message
from app.configs.extensions import mail
from app.models.users import User

@shared_task(ignore_result=True)
def notify_new_quiz(quiz_title, subject_name):
    # Fetch all users (In real production, batch this or use a more efficient way)
    # Since we are outside request context, we need to ensure we can access DB if needed.
    # Celery app context is handled by our init script.
    
    users = User.query.all()
    emails = [user.email for user in users if user.email]
    
    if not emails:
        return "No users to notify."

    # Send individually or as bcc? For privacy, usually individual or BCC.
    # For simplicity here, we'll iterate or use BCC if list is small. 
    # Let's send one email with BCC to avoid loop overhead here, 
    # OR iterate and spawn sub-tasks if list is huge.
    
    # Simple approach: BCC
    msg = Message(f"New Quiz Available: {quiz_title}", bcc=emails)
    msg.body = f"Hello Student,\n\nA new quiz '{quiz_title}' in subject '{subject_name}' has been added.\nCheck it out now!\n\nHappy Learning,\nQuizzy Team"
    
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending quiz notification: {e}")

@shared_task(ignore_result=True)
def notify_marks_released(user_email, quiz_title, score):
    msg = Message(f"Quiz Results: {quiz_title}", recipients=[user_email])
    msg.body = f"Hello,\n\nYour results for the quiz '{quiz_title}' are available.\nYou scored: {score}.\n\nView detailed analysis on the dashboard.\n\nRegards,\nQuizzy Team"
    
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending marks notification: {e}")

@shared_task(ignore_result=True)
def send_reset_password_email(email, reset_link):
    msg = Message("Reset Your Password", recipients=[email])
    msg.body = f"Hello,\n\nClick the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email.\n\nRegards,\nQuizzy Team"
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending reset password email: {e}")
