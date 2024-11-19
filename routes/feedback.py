from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from datetime import datetime
from models import db, Feedback, FeedbackType

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback_form():
    feedback_type = request.args.get('type', 'BUG').upper()  # Default to bug if not specified
    
    if request.method == 'POST':
        feedback = Feedback(
            type=FeedbackType(request.form.get('type', 'BUG').upper()),
            title=request.form.get('title'),
            description=request.form.get('description'),
            url=request.form.get('url'),
            browser_info=request.headers.get('User-Agent'),
            user_id=current_user.id if current_user.is_authenticated else None,
            created_at=datetime.utcnow()
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback! We will review it shortly.', 'success')
        return redirect(url_for('main.index'))
        
    return render_template('feedback_form.html', 
                         feedback_type=feedback_type,
                         feedback_types=FeedbackType)
