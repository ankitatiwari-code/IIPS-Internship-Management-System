from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)

app.config["SECRET_KEY"] = "iips-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///internship_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================
# DATABASE MODELS
# =========================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    industry = db.Column(db.String(150))
    location = db.Column(db.String(150))
    internship_type = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Available")


class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )

    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    role = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    internship_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    mentor = db.relationship(
        "User",
        foreign_keys=[mentor_id]
    )

    company = db.relationship("Company")


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )

    role = db.Column(db.String(150), nullable=False)
    offer_date = db.Column(db.Date, nullable=False)
    joining_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="Pending")

    student = db.relationship("User")
    company = db.relationship("Company")


class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    internship_id = db.Column(
        db.Integer,
        db.ForeignKey("internship.id"),
        nullable=False
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    mentor_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=True
    )

    evaluation_date = db.Column(db.Date, nullable=True)

    technical_score = db.Column(db.Integer, nullable=True)
    communication_score = db.Column(db.Integer, nullable=True)
    professionalism_score = db.Column(db.Integer, nullable=True)
    overall_score = db.Column(db.Integer, nullable=True)

    technical_remarks = db.Column(db.Text)
    communication_remarks = db.Column(db.Text)
    professionalism_remarks = db.Column(db.Text)
    overall_remarks = db.Column(db.Text)

    internship = db.relationship("Internship")

    student = db.relationship(
        "User",
        foreign_keys=[student_id]
    )

    mentor = db.relationship(
        "User",
        foreign_keys=[mentor_id]
    )


# =========================
# INTERNSHIP STATUS SYNC
# =========================

def sync_internship_statuses():

    today = datetime.now().date()

    internships = Internship.query.all()

    changed = False

    for internship in internships:

        if today < internship.start_date:
            new_status = "Pending"

        elif today > internship.end_date:
            new_status = "Completed"

        else:
            new_status = "Ongoing"

        if internship.status != new_status:

            internship.status = new_status
            changed = True

    if changed:
        db.session.commit()


# =========================
# LOGIN
# =========================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =========================
# AUTHENTICATION
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=hashed_password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            if user.role == "student":
                return redirect(url_for("student_dashboard"))

            elif user.role == "mentor":
                return redirect(url_for("mentor_dashboard"))

            elif user.role == "admin":
                return redirect(url_for("admin_dashboard"))

        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))


# =========================
# STUDENT DASHBOARD
# =========================

@app.route("/student/dashboard")
@login_required
def student_dashboard():

    sync_internship_statuses()

    internships = Internship.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Internship.created_at.desc()
    ).all()

    offers_count = Offer.query.filter_by(
        student_id=current_user.id
    ).count()

    active_internship_count = Internship.query.filter_by(
        student_id=current_user.id,
        status="Ongoing"
    ).count()

    evaluation = Evaluation.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Evaluation.id.desc()
    ).first()

    if evaluation and evaluation.overall_score is not None:
        evaluation_status = "Completed"
    else:
        evaluation_status = "Pending"

    return render_template(
        "student_dashboard.html",
        internships=internships,
        applications_count=len(internships),
        offers_count=offers_count,
        active_internship_count=active_internship_count,
        evaluation_status=evaluation_status
    )


# =========================
# INTERNSHIP REGISTRATION
# =========================

@app.route(
    "/student/internship-registration",
    methods=["GET", "POST"]
)
@login_required
def internship_registration():

    mentors = User.query.filter_by(
        role="mentor"
    ).order_by(
        User.first_name
    ).all()

    if request.method == "POST":

        company_name = request.form.get("company")
        role = request.form.get("role")
        start_date_text = request.form.get("start_date")
        end_date_text = request.form.get("end_date")
        internship_type = request.form.get("internship_type")
        mentor_id = request.form.get("mentor_id")
        description = request.form.get("description")

        try:
            start_date = datetime.strptime(
                start_date_text,
                "%Y-%m-%d"
            ).date()

            end_date = datetime.strptime(
                end_date_text,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            flash("Please enter valid internship dates.", "error")

            return redirect(
                url_for("internship_registration")
            )

        if end_date < start_date:

            flash(
                "End date cannot be before start date.",
                "error"
            )

            return redirect(
                url_for("internship_registration")
            )

        company = Company.query.filter_by(
            name=company_name
        ).first()

        if not company:

            company = Company(
                name=company_name,
                internship_type=internship_type,
                status="Available"
            )

            db.session.add(company)
            db.session.flush()

        internship = Internship(
            student_id=current_user.id,
            company_id=company.id,
            mentor_id=int(mentor_id) if mentor_id else None,
            role=role,
            start_date=start_date,
            end_date=end_date,
            internship_type=internship_type,
            description=description,
            status="Pending"
        )

        db.session.add(internship)
        db.session.commit()

        flash(
            "Internship registration submitted successfully.",
            "success"
        )

        return redirect(
            url_for("my_internship")
        )

    return render_template(
        "internship_registration.html",
        mentors=mentors
    )


# =========================
# MY INTERNSHIP
# =========================

@app.route("/student/my-internship")
@login_required
def my_internship():

    sync_internship_statuses()

    internship = Internship.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Internship.created_at.desc()
    ).first()

    return render_template(
        "my_internship.html",
        internship=internship
    )


# =========================
# COMPANY DATABASE
# =========================

@app.route("/student/companies")
@login_required
def company_database():

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Company.query

    if search:

        query = query.filter(
            Company.name.ilike(f"%{search}%")
            | Company.industry.ilike(f"%{search}%")
            | Company.location.ilike(f"%{search}%")
        )

    companies = query.order_by(
        Company.name
    ).all()

    return render_template(
        "company_database.html",
        companies=companies,
        search=search
    )


# =========================
# OFFER TRACKING
# =========================

@app.route("/student/offers")
@login_required
def offer_tracking():

    offers = Offer.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Offer.offer_date.desc()
    ).all()

    return render_template(
        "offer_tracking.html",
        offers=offers
    )


# =========================
# MY EVALUATION
# =========================

@app.route("/student/evaluation")
@login_required
def my_evaluation():

    sync_internship_statuses()

    evaluation = Evaluation.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Evaluation.id.desc()
    ).first()

    internship = Internship.query.filter_by(
        student_id=current_user.id
    ).order_by(
        Internship.created_at.desc()
    ).first()

    return render_template(
        "my_evaluation.html",
        evaluation=evaluation,
        internship=internship
    )


# =========================
# MENTOR DASHBOARD
# =========================

@app.route("/mentor/dashboard")
@login_required
def mentor_dashboard():

    if current_user.role != "mentor":
        flash("You do not have permission to access the mentor area.", "error")
        return redirect(url_for("login"))

    sync_internship_statuses()

    assigned_internships = Internship.query.filter_by(
        mentor_id=current_user.id
    ).order_by(
        Internship.created_at.desc()
    ).all()

    assigned_count = len(assigned_internships)

    ongoing_count = Internship.query.filter_by(
        mentor_id=current_user.id,
        status="Ongoing"
    ).count()

    completed_count = Internship.query.filter_by(
        mentor_id=current_user.id,
        status="Completed"
    ).count()

    pending_evaluations = 0

    for internship in assigned_internships:

        evaluation = Evaluation.query.filter_by(
            internship_id=internship.id
        ).order_by(
            Evaluation.id.desc()
        ).first()

        if not evaluation or evaluation.overall_score is None:
            pending_evaluations += 1

    return render_template(
        "mentor_dashboard.html",
        assigned_count=assigned_count,
        ongoing_count=ongoing_count,
        completed_count=completed_count,
        pending_evaluations=pending_evaluations,
        assigned_internships=assigned_internships
    )


# =========================
# MENTOR - MY STUDENTS
# =========================

@app.route("/mentor/students")
@login_required
def my_students():

    if current_user.role != "mentor":
        flash("You do not have permission to access the mentor area.", "error")
        return redirect(url_for("login"))

    sync_internship_statuses()

    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Internship.query.filter_by(
        mentor_id=current_user.id
    )

    assigned_internships = query.order_by(
        Internship.created_at.desc()
    ).all()

    if search:

        search_lower = search.lower()

        assigned_internships = [
            internship
            for internship in assigned_internships
            if search_lower in (
                f"{internship.student.first_name} "
                f"{internship.student.last_name}"
            ).lower()
            or search_lower in internship.student.email.lower()
            or search_lower in internship.company.name.lower()
            or search_lower in internship.role.lower()
        ]

    return render_template(
        "my_students.html",
        assigned_internships=assigned_internships,
        search=search
    )


# =========================
# MENTOR - STUDENT EVALUATION
# =========================

@app.route(
    "/mentor/evaluation/<int:internship_id>",
    methods=["GET", "POST"]
)
@login_required
def student_evaluation(internship_id):

    if current_user.role != "mentor":
        flash("You do not have permission to access the mentor area.", "error")
        return redirect(url_for("login"))

    sync_internship_statuses()

    internship = Internship.query.filter_by(
        id=internship_id,
        mentor_id=current_user.id
    ).first_or_404()

    evaluation = Evaluation.query.filter_by(
        internship_id=internship.id
    ).order_by(
        Evaluation.id.desc()
    ).first()

    if request.method == "POST":

        score_map = {
            "Excellent": 5,
            "Good": 4,
            "Satisfactory": 3,
            "Needs Improvement": 2
        }

        technical = request.form.get("technical_skills")
        communication = request.form.get("communication")
        professionalism = request.form.get("professionalism")
        overall = request.form.get("overall_performance")
        mentor_remarks = request.form.get(
            "mentor_remarks",
            ""
        ).strip()

        if not technical or not communication or not professionalism or not overall:

            flash(
                "Please select a score for all evaluation categories.",
                "error"
            )

            return redirect(
                url_for(
                    "student_evaluation",
                    internship_id=internship.id
                )
            )

        if evaluation is None:

            evaluation = Evaluation(
                internship_id=internship.id,
                student_id=internship.student_id,
                mentor_id=current_user.id
            )

            db.session.add(evaluation)

        evaluation.evaluation_date = datetime.utcnow().date()

        evaluation.technical_score = score_map.get(technical)
        evaluation.communication_score = score_map.get(communication)
        evaluation.professionalism_score = score_map.get(professionalism)
        evaluation.overall_score = score_map.get(overall)

        evaluation.technical_remarks = mentor_remarks
        evaluation.communication_remarks = mentor_remarks
        evaluation.professionalism_remarks = mentor_remarks
        evaluation.overall_remarks = mentor_remarks

        db.session.commit()

        flash(
            "Student evaluation submitted successfully.",
            "success"
        )

        return redirect(
            url_for("my_students")
        )

    return render_template(
        "student_evaluation.html",
        internship=internship,
        evaluation=evaluation
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    sync_internship_statuses()

    total_students = User.query.filter_by(
        role="student"
    ).count()

    active_internships = Internship.query.filter_by(
        status="Ongoing"
    ).count()

    registered_companies = Company.query.count()

    internships = Internship.query.order_by(
        Internship.created_at.desc()
    ).limit(5).all()

    pending_evaluations = 0

    for internship in Internship.query.all():

        evaluation = Evaluation.query.filter_by(
            internship_id=internship.id
        ).order_by(
            Evaluation.id.desc()
        ).first()

        if not evaluation or evaluation.overall_score is None:
            pending_evaluations += 1

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        active_internships=active_internships,
        registered_companies=registered_companies,
        pending_evaluations=pending_evaluations,
        internships=internships
    )


# =========================
# ADMIN ANALYTICS
# =========================

@app.route("/admin/analytics")
@login_required
def analytics():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    sync_internship_statuses()

    total_internships = Internship.query.count()

    completed_internships = Internship.query.filter_by(
        status="Completed"
    ).count()

    ongoing_internships = Internship.query.filter_by(
        status="Ongoing"
    ).count()

    pending_internships = Internship.query.filter_by(
        status="Pending"
    ).count()

    registered_companies = Company.query.count()

    if total_internships > 0:

        completed_percentage = round(
            (completed_internships / total_internships) * 100
        )

        ongoing_percentage = round(
            (ongoing_internships / total_internships) * 100
        )

        pending_percentage = round(
            (pending_internships / total_internships) * 100
        )

    else:

        completed_percentage = 0
        ongoing_percentage = 0
        pending_percentage = 0

    industry_data = []

    companies = Company.query.all()

    for company in companies:

        internships = Internship.query.filter_by(
            company_id=company.id
        ).all()

        total = len(internships)

        completed = sum(
            1
            for internship in internships
            if internship.status == "Completed"
        )

        ongoing = sum(
            1
            for internship in internships
            if internship.status == "Ongoing"
        )

        industry_data.append({
            "name": company.industry or "Other",
            "total": total,
            "completed": completed,
            "ongoing": ongoing
        })

    return render_template(
        "analytics.html",
        total_internships=total_internships,
        completed_internships=completed_internships,
        ongoing_internships=ongoing_internships,
        pending_internships=pending_internships,
        registered_companies=registered_companies,
        completed_percentage=completed_percentage,
        ongoing_percentage=ongoing_percentage,
        pending_percentage=pending_percentage,
        industry_data=industry_data
    )


# =========================
# ADMIN COMPANY MANAGEMENT
# =========================

@app.route("/admin/companies")
@login_required
def company_management():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    companies = Company.query.order_by(
        Company.name.asc()
    ).all()

    return render_template(
        "company_management.html",
        companies=companies
    )


# =========================
# ADMIN INTERNSHIP MANAGEMENT
# =========================

@app.route("/admin/internships")
@login_required
def internship_management():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    sync_internship_statuses()

    internships = Internship.query.order_by(
        Internship.created_at.desc()
    ).all()

    return render_template(
        "internship_management.html",
        internships=internships
    )


# =========================
# ADMIN STUDENT MANAGEMENT
# =========================

@app.route("/admin/students")
@login_required
def student_management():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    sync_internship_statuses()

    students = User.query.filter_by(
        role="student"
    ).order_by(
        User.first_name.asc()
    ).all()

    student_internships = {}

    for student in students:

        internship = Internship.query.filter_by(
            student_id=student.id
        ).order_by(
            Internship.created_at.desc()
        ).first()

        student_internships[student.id] = internship

    return render_template(
        "student_management.html",
        students=students,
        student_internships=student_internships
    )


# =========================
# ADMIN OFFER MANAGEMENT
# =========================

@app.route(
    "/admin/offers",
    methods=["GET", "POST"]
)
@login_required
def offer_management():

    if current_user.role != "admin":
        flash(
            "You do not have permission to access the admin area.",
            "error"
        )
        return redirect(url_for("login"))

    students = User.query.filter_by(
        role="student"
    ).order_by(
        User.first_name.asc()
    ).all()

    companies = Company.query.order_by(
        Company.name.asc()
    ).all()

    if request.method == "POST":

        student_id = request.form.get("student_id")
        company_id = request.form.get("company_id")
        role = request.form.get("role")
        offer_date_text = request.form.get("offer_date")
        joining_date_text = request.form.get("joining_date")
        status = request.form.get("status")

        if not student_id or not company_id or not role or not offer_date_text:

            flash(
                "Please fill in all required offer details.",
                "error"
            )

            return redirect(
                url_for("offer_management")
            )

        try:

            offer_date = datetime.strptime(
                offer_date_text,
                "%Y-%m-%d"
            ).date()

            if joining_date_text:

                joining_date = datetime.strptime(
                    joining_date_text,
                    "%Y-%m-%d"
                ).date()

            else:

                joining_date = None

        except (ValueError, TypeError):

            flash(
                "Please enter valid dates.",
                "error"
            )

            return redirect(
                url_for("offer_management")
            )

        if joining_date and joining_date < offer_date:

            flash(
                "Joining date cannot be before the offer date.",
                "error"
            )

            return redirect(
                url_for("offer_management")
            )

        if status not in [
            "Pending",
            "Accepted",
            "Rejected"
        ]:

            status = "Pending"

        offer = Offer(
            student_id=int(student_id),
            company_id=int(company_id),
            role=role.strip(),
            offer_date=offer_date,
            joining_date=joining_date,
            status=status
        )

        db.session.add(offer)
        db.session.commit()

        flash(
            "Offer created successfully.",
            "success"
        )

        return redirect(
            url_for("offer_management")
        )

    offers = Offer.query.order_by(
        Offer.offer_date.desc()
    ).all()

    return render_template(
        "offer_management.html",
        offers=offers,
        students=students,
        companies=companies
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return "IIPS Internship Management System is running!"


# =========================
# CREATE DATABASE TABLES
# =========================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)