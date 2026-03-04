from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'inspectra-secret-key-2025'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inspectra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#  Models (Section 3) 

class Inspector(db.Model):
    __tablename__ = 'inspector'
    InspectorID    = db.Column(db.Integer, primary_key=True)
    InspectorName  = db.Column(db.String(128), nullable=False)
    InspectorEmail = db.Column(db.String(256), unique=True, nullable=False)
    PasswordHash   = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)

class Panel(db.Model):
    __tablename__ = 'panel'
    PanelID    = db.Column(db.Integer, primary_key=True)
    CellCount  = db.Column(db.Integer, nullable=False)
    CurrentValue = db.Column(db.Float)
    PanelSize  = db.Column(db.String(64))
    images     = db.relationship('Image', backref='panel', lazy=True)

class Image(db.Model):
    __tablename__ = 'image'
    ImageID     = db.Column(db.Integer, primary_key=True)
    CaptureDate = db.Column(db.String(64), nullable=False)
    ImageURL    = db.Column(db.String(512))
    PanelID     = db.Column(db.Integer, db.ForeignKey('panel.PanelID'))
    defects     = db.relationship('Defect', backref='image', lazy=True)
    report      = db.relationship('Report', backref='image', uselist=False, lazy=True)

class Defect(db.Model):
    __tablename__ = 'defect'
    DefectID     = db.Column(db.Integer, primary_key=True)
    DefectType   = db.Column(db.String(128))
    CellLocation = db.Column(db.String(64))
    RiskLevel    = db.Column(db.String(32), nullable=False)
    ImageID      = db.Column(db.Integer, db.ForeignKey('image.ImageID'))

class Report(db.Model):
    __tablename__ = 'report'
    ReportID           = db.Column(db.Integer, primary_key=True)
    SeverityScore      = db.Column(db.Float)
    DefectedCellCount  = db.Column(db.Integer)
    LifespanEstimate   = db.Column(db.String(64))
    ImageID            = db.Column(db.Integer, db.ForeignKey('image.ImageID'))

#  Access Control 

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'inspector_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

#  Mock History Records 

mock_records = [
    {"capture_date": "Dec 5, 2025 10:45 AM", "image_url": "Image (Inspection 1).png", "risk_level": "High"},
    {"capture_date": "Dec 1, 2025 1:45 PM",  "image_url": "Image (Inspection 1).png", "risk_level": "Low"},
    {"capture_date": "Nov 28, 2025 2:45 PM", "image_url": "Image (Inspection 1).png", "risk_level": "Moderate"},
]

#  Auth Routes 

@app.route('/', methods=['GET'])
def index():
    if 'inspector_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'inspector_id' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not email or not password:
            error = 'Fill in the required fields.'
        else:
            inspector = Inspector.query.filter_by(InspectorEmail=email).first()
            if inspector and inspector.check_password(password):
                session['inspector_id']   = inspector.InspectorID
                session['inspector_name'] = inspector.InspectorName
                return redirect(url_for('home'))
            else:
                error = 'Invalid email or password.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    sent = False
    if request.method == 'POST':
        sent = True
    return render_template('forgot_password.html', sent=sent)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    success = False
    if request.method == 'POST':
        success = True
    return render_template('reset_password.html', success=success)

#  Protected Routes 

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/history')
@login_required
def history():
    return render_template('history.html', records=mock_records)

@app.route('/dashboard')
@login_required
def dashboard():
    # Inspected Panels Summary
    total_panels    = Panel.query.count()
    defected_panels = db.session.query(Panel).join(Image).join(Defect).filter(
        Defect.RiskLevel.in_(['High', 'Moderate'])
    ).distinct().count()
    usable_panels   = total_panels - defected_panels

    # Top Defect Types
    defect_types = ['Microcracks', 'Hotspots', 'Finger interruptions', 'PID', 'Material Defects']
    defect_counts = {}
    for dt in defect_types:
        defect_counts[dt] = Defect.query.filter_by(DefectType=dt).count()
    max_defect = max(defect_counts.values()) if any(defect_counts.values()) else 1

    # Recent Inspection (latest image + its report)
    latest_image  = Image.query.order_by(Image.ImageID.desc()).first()
    latest_report = latest_image.report if latest_image else None
    latest_panel  = latest_image.panel  if latest_image else None

    # Technician Activity (all inspectors)
    technicians = Inspector.query.all()

    return render_template('dashboard.html',
        total_panels    = total_panels,
        defected_panels = defected_panels,
        usable_panels   = usable_panels,
        defect_counts   = defect_counts,
        max_defect      = max_defect,
        latest_image    = latest_image,
        latest_report   = latest_report,
        latest_panel    = latest_panel,
        technicians     = technicians,
    )

#  DB Init & Seed 

def seed_db():
    with app.app_context():
        db.create_all()

        # Seed inspector
        if not Inspector.query.filter_by(InspectorEmail='sszx78@gmail.com').first():
            dev = Inspector(InspectorName='Dev Inspector', InspectorEmail='sszx78@gmail.com')
            dev.set_password('password123')
            db.session.add(dev)

        # Seed demo dashboard data if no panels exist
        if Panel.query.count() == 0:
            panels = [
                Panel(CellCount=60, CurrentValue=8.5,  PanelSize='1650x992'),
                Panel(CellCount=60, CurrentValue=8.2,  PanelSize='1650x992'),
                Panel(CellCount=72, CurrentValue=9.1,  PanelSize='1956x992'),
            ]
            db.session.add_all(panels)
            db.session.flush()

            images = [
                Image(CaptureDate='Dec 5, 2025 10:45 AM', ImageURL='Image (Inspection 1).png', PanelID=panels[0].PanelID),
                Image(CaptureDate='Dec 1, 2025 1:45 PM',  ImageURL='Image (Inspection 1).png', PanelID=panels[1].PanelID),
                Image(CaptureDate='Nov 28, 2025 2:45 PM', ImageURL='Image (Inspection 1).png', PanelID=panels[2].PanelID),
            ]
            db.session.add_all(images)
            db.session.flush()

            defects = [
                Defect(DefectType='Microcracks',          CellLocation='A1', RiskLevel='High',     ImageID=images[0].ImageID),
                Defect(DefectType='Microcracks',          CellLocation='B2', RiskLevel='High',     ImageID=images[0].ImageID),
                Defect(DefectType='Hotspots',             CellLocation='C3', RiskLevel='Moderate', ImageID=images[0].ImageID),
                Defect(DefectType='Finger interruptions', CellLocation='D4', RiskLevel='Moderate', ImageID=images[1].ImageID),
                Defect(DefectType='PID',                  CellLocation='E5', RiskLevel='Low',      ImageID=images[1].ImageID),
                Defect(DefectType='Material Defects',     CellLocation='F6', RiskLevel='Low',      ImageID=images[2].ImageID),
                Defect(DefectType='Microcracks',          CellLocation='G7', RiskLevel='High',     ImageID=images[2].ImageID),
            ]
            db.session.add_all(defects)

            reports = [
                Report(SeverityScore=3.7, DefectedCellCount=4, LifespanEstimate='Short',    ImageID=images[0].ImageID),
                Report(SeverityScore=2.1, DefectedCellCount=2, LifespanEstimate='Moderate', ImageID=images[1].ImageID),
                Report(SeverityScore=1.4, DefectedCellCount=1, LifespanEstimate='Long',     ImageID=images[2].ImageID),
            ]
            db.session.add_all(reports)

        db.session.commit()

seed_db()

if __name__ == '__main__':
    app.run(debug=True)
