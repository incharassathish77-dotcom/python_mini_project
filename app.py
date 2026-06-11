"""
Government Scheme Awareness App
Flask Backend with SQLite Database
"""

from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3
import os
import sys

# Force UTF-8 output on Windows terminals to avoid cp1252 emoji errors
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# ─── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "govtscheme_secret_2024"
app.config["SESSION_TYPE"] = "filesystem"

DATABASE = os.path.join(os.path.dirname(__file__), "database.db")

# ─── Database Helpers ─────────────────────────────────────────────────────────

def get_db():
    """Open a database connection (one per request)."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row          # dict-like rows
    return db

@app.teardown_appcontext
def close_db(exception):
    """Close DB connection at end of request."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    """Create tables and insert sample data if not already present."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # Create schemes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schemes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            category  TEXT    NOT NULL,
            eligibility TEXT  NOT NULL,
            benefits  TEXT    NOT NULL,
            documents TEXT    NOT NULL,
            procedure TEXT    NOT NULL,
            website   TEXT    NOT NULL
        )
    """)

    # Create admin users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)

    # Insert default admin if not exists
    cur.execute("SELECT COUNT(*) FROM admins")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                    ("admin", "admin123"))

    # Insert sample schemes if table is empty
    cur.execute("SELECT COUNT(*) FROM schemes")
    if cur.fetchone()[0] == 0:
        sample_schemes = [
            (
                "Beti Bachao Beti Padhao",
                "Women Welfare",
                "Female children aged 0-10 years. Applicable to families across India with focus on districts with low Child Sex Ratio.",
                "Financial assistance for girl child education, survival and protection of girl child, improvement of child sex ratio, promotion of girl child education and participation.",
                "Aadhaar Card|Birth Certificate of Girl Child|Bank Passbook|Passport Size Photo|Income Certificate|BPL Certificate (if applicable)",
                "1. Check eligibility on official portal|2. Visit nearest Sukanya Samriddhi office or post office|3. Fill the application form (Form-1)|4. Attach required documents|5. Submit application and receive acknowledgement|6. Open Sukanya Samriddhi Account|7. Track benefits through bank/post office",
                "https://wcd.nic.in/bbbp-schemes"
            ),
            (
                "National Scholarship Scheme",
                "Rural Education",
                "Students from low-income families (Annual income below ₹2,50,000). Applicable from Class 9 onwards through post-graduation. Must be Indian citizen.",
                "Financial scholarship ranging from ₹1,000 to ₹20,000 per month, full fee reimbursement for technical courses, laptop/device assistance, mentorship support.",
                "Aadhaar Card|Educational Certificates (Last Qualifying Exam)|Income Certificate|Bank Passbook|Passport Size Photo|Caste Certificate (if applicable)|Domicile Certificate",
                "1. Register on National Scholarship Portal (scholarships.gov.in)|2. Fill application form with personal and academic details|3. Upload scanned documents|4. Submit application before deadline|5. Institution verification|6. State/Central verification|7. Scholarship disbursed to bank account",
                "https://scholarships.gov.in"
            ),
            (
                "Child Nutrition Program",
                "Children Welfare",
                "Children aged 0-6 years from economically weaker sections. Pregnant women and lactating mothers. Applicable in rural and urban slum areas.",
                "Supplementary nutrition (food), Immunization, Health check-up, Referral services, Pre-school non-formal education, Nutrition and health education to mothers.",
                "Aadhaar Card|Birth Certificate|Ration Card|Income Certificate|Mother-Child Protection Card|Bank Passbook",
                "1. Visit nearest Anganwadi Centre|2. Register child and mother details|3. Submit required documents|4. Regular health check-up schedule|5. Receive supplementary nutrition|6. Avail immunization services|7. Monitor growth and development",
                "https://wcd.nic.in/icds"
            ),
            (
                "PM Kisan Samman Nidhi",
                "Rural Education",
                "Small and marginal farmers with cultivable land up to 2 hectares. Must be Indian citizen with valid land records.",
                "₹6,000 per year in three installments of ₹2,000 directly to bank account, financial support for agricultural inputs.",
                "Aadhaar Card|Land Records/Khasra|Bank Passbook|Income Certificate|Farmer Registration Certificate",
                "1. Register on PM-Kisan portal or visit CSC|2. Fill Farmer Registration Form|3. Submit land and personal documents|4. Verification by Revenue Officer|5. Approval and registration|6. Money credited directly to bank account",
                "https://pmkisan.gov.in"
            ),
            (
                "Pradhan Mantri Awas Yojana",
                "Women Welfare",
                "Economically Weaker Section (EWS) with income up to ₹3 lakh, Low Income Group (LIG) ₹3-6 lakh. Priority to women, SC/ST, minorities.",
                "Interest subsidy on home loans, ₹1.5 lakh direct benefit transfer for rural areas, affordable housing construction support.",
                "Aadhaar Card|Income Certificate|Bank Passbook|Property Documents|Passport Size Photo|Caste Certificate (SC/ST)|BPL Certificate",
                "1. Check eligibility on pmayg.nic.in|2. Apply through CSC or Gram Panchayat|3. Fill PMAY application form|4. Submit income and property documents|5. Verification by government officials|6. Allotment of house/subsidy approval|7. Construction and handover",
                "https://pmayg.nic.in"
            ),
            (
                "Sukanya Samriddhi Yojana",
                "Women Welfare",
                "Girl child below 10 years of age. Only two girl children per family eligible. Must be Indian citizen.",
                "High interest rate (currently 8.2% p.a.), Tax benefits under Section 80C, Maturity amount on girl turning 21 years, Partial withdrawal for education at age 18.",
                "Girl Child's Birth Certificate|Aadhaar Card of Parent/Guardian|Address Proof|Passport Size Photo of Girl Child|Bank Passbook",
                "1. Visit Post Office or authorized bank|2. Fill SSY account opening form|3. Submit girl child's birth certificate and KYC documents|4. Make initial deposit (minimum ₹250)|5. Receive passbook|6. Make regular deposits|7. Account matures when girl turns 21",
                "https://www.nsiindia.gov.in/InternalPage.aspx?Id_Pk=89"
            ),
        ]
        cur.executemany("""
            INSERT INTO schemes (name, category, eligibility, benefits, documents, procedure, website)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_schemes)

    db.commit()
    db.close()
    print("Database initialized successfully.")

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Home page – list all schemes."""
    db = get_db()
    schemes = db.execute("SELECT id, name, category, eligibility FROM schemes ORDER BY id").fetchall()
    lang = request.args.get("lang", "en")
    return render_template("index.html", schemes=schemes, lang=lang)


@app.route("/search")
def search():
    """Search schemes by name or category."""
    query = request.args.get("q", "").strip()
    lang  = request.args.get("lang", "en")
    results = []
    if query:
        db = get_db()
        results = db.execute(
            "SELECT id, name, category, eligibility FROM schemes "
            "WHERE name LIKE ? OR category LIKE ?",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
    return render_template("search.html", results=results, query=query, lang=lang)


@app.route("/eligibility", methods=["GET", "POST"])
def eligibility():
    """Eligibility checker form and logic."""
    lang = request.args.get("lang", "en")
    if request.method == "POST":
        try:
            age    = int(request.form.get("age", 0))
            gender = request.form.get("gender", "").lower()
            income = int(request.form.get("income", 0))
        except ValueError:
            flash("Please enter valid numeric values for Age and Income.", "danger")
            return redirect(url_for("eligibility"))

        # Build category filters based on inputs
        categories = []
        if gender == "female":
            categories.append("Women Welfare")
        if income < 250000:
            categories.append("Rural Education")
        if age < 18:
            categories.append("Children Welfare")

        db = get_db()
        if categories:
            placeholders = ",".join("?" * len(categories))
            eligible = db.execute(
                f"SELECT id, name, category, eligibility, benefits FROM schemes "
                f"WHERE category IN ({placeholders})",
                categories
            ).fetchall()
        else:
            eligible = []

        return render_template(
            "eligibility_result.html",
            eligible=eligible,
            age=age,
            gender=gender,
            income=income,
            lang=lang
        )

    return render_template("eligibility.html", lang=lang)


@app.route("/scheme/<int:scheme_id>")
def scheme_detail(scheme_id):
    """View full details of a specific scheme."""
    lang = request.args.get("lang", "en")
    db = get_db()
    scheme = db.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
    if scheme is None:
        flash("Scheme not found.", "danger")
        return redirect(url_for("index"))

    # Split pipe-separated lists into Python lists
    documents = [d.strip() for d in scheme["documents"].split("|")]
    procedure = [p.strip() for p in scheme["procedure"].split("|")]

    return render_template(
        "scheme.html",
        scheme=scheme,
        documents=documents,
        procedure=procedure,
        lang=lang
    )


# ─── Admin Routes ─────────────────────────────────────────────────────────────

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        db = get_db()
        admin = db.execute(
            "SELECT * FROM admins WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        if admin:
            # Simple session flag (use Flask-Login for production)
            from flask import session
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard listing all schemes."""
    from flask import session
    if not session.get("admin"):
        flash("Please login to access the admin panel.", "warning")
        return redirect(url_for("admin_login"))
    db = get_db()
    schemes = db.execute("SELECT id, name, category FROM schemes ORDER BY id").fetchall()
    return render_template("admin_dashboard.html", schemes=schemes)


@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    """Add a new scheme."""
    from flask import session
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        category    = request.form.get("category", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        benefits    = request.form.get("benefits", "").strip()
        documents   = request.form.get("documents", "").strip()
        procedure   = request.form.get("procedure", "").strip()
        website     = request.form.get("website", "").strip()

        if not all([name, category, eligibility, benefits, documents, procedure, website]):
            flash("All fields are required.", "danger")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO schemes (name, category, eligibility, benefits, documents, procedure, website) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, category, eligibility, benefits, documents, procedure, website)
            )
            db.commit()
            flash(f"Scheme '{name}' added successfully!", "success")
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_add.html")


@app.route("/admin/edit/<int:scheme_id>", methods=["GET", "POST"])
def admin_edit(scheme_id):
    """Edit an existing scheme."""
    from flask import session
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    db = get_db()
    scheme = db.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
    if scheme is None:
        flash("Scheme not found.", "danger")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        category    = request.form.get("category", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        benefits    = request.form.get("benefits", "").strip()
        documents   = request.form.get("documents", "").strip()
        procedure   = request.form.get("procedure", "").strip()
        website     = request.form.get("website", "").strip()

        if not all([name, category, eligibility, benefits, documents, procedure, website]):
            flash("All fields are required.", "danger")
        else:
            db.execute(
                "UPDATE schemes SET name=?, category=?, eligibility=?, benefits=?, "
                "documents=?, procedure=?, website=? WHERE id=?",
                (name, category, eligibility, benefits, documents, procedure, website, scheme_id)
            )
            db.commit()
            flash(f"Scheme '{name}' updated successfully!", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_edit.html", scheme=scheme)


@app.route("/admin/delete/<int:scheme_id>", methods=["POST"])
def admin_delete(scheme_id):
    """Delete a scheme."""
    from flask import session
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    db = get_db()
    db.execute("DELETE FROM schemes WHERE id = ?", (scheme_id,))
    db.commit()
    flash("Scheme deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    """Logout admin."""
    from flask import session
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()          # Initialize database on first run
    app.run(host="0.0.0.0", port=5000, debug=True)
