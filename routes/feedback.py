from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from datetime import datetime
from models import db, Feedback, FeedbackType
from models.activity import Activity

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    # Default to general feedback if not specified
    feedback_type = request.args.get('type', FeedbackType.GENERAL.value)
    
    if request.method == 'POST':
        feedback = Feedback(
            type=request.form.get('type', FeedbackType.GENERAL.value),
            title=request.form.get('title'),
            description=request.form.get('description'),
            email=request.form.get('email') if not current_user.is_authenticated else current_user.email,
            url=request.form.get('url'),
            user_id=current_user.id if current_user.is_authenticated else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(feedback)
        
        # Log the feedback activity if user is authenticated
        if current_user.is_authenticated:
            Activity.log(
                user_id=current_user.id,
                action='submitted_feedback',
                details=f'Submitted {feedback.type} feedback: {feedback.title}'
            )
        
        db.session.commit()
        
        flash('Thank you for your feedback! We will review it shortly.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('feedback_form.html', 
                         feedback_type=feedback_type,
                         feedback_types=FeedbackType.choices())
