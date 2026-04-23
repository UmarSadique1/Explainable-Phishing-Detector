from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user

from app import db
from app.models import Analysis, User
from app.ml.model import predict_with_lime
from app.ml.model import predict_with_lime, get_model_performance_metrics

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    SUSPICIOUS_THRESHOLD = 0.31
    HIGH_RISK_THRESHOLD = 0.60

    email_text = ""
    prediction = None
    phishing_probability = None

    risk_level = None
    risk_badge_class = None
    threshold = SUSPICIOUS_THRESHOLD
    high_risk_threshold = HIGH_RISK_THRESHOLD

    lime_weights = None
    lime_percent_weights = None
    highlighted_html = None
    lime_readable = None

    shap_weights = None
    shap_percent_weights = None
    shap_plot_base64 = None
    shap_readable = None

    error = None

    if request.method == "POST":
        email_text = request.form.get("email_text", "").strip()
        word_count = len(email_text.split())

        if not email_text:
            error = "Please paste an email to analyse."
        elif len(email_text) < 40:
            error = "Please enter a fuller email. The analysis requires more content."
        elif word_count < 6:
            error = "Please paste a realistic email with multiple words or sentences."
        else:
            result = predict_with_lime(email_text)

            phishing_probability = result.phishing_proba
            prediction = result.label

            if prediction == "Phishing":
                risk_level = "High Risk"
                risk_badge_class = "high-risk"
            elif prediction == "Suspicious":
                risk_level = "Suspicious"
                risk_badge_class = "suspicious"
            else:
                risk_level = "Likely Legitimate"
                risk_badge_class = "legitimate"

            lime_weights = result.lime_weights
            lime_percent_weights = result.lime_percent_weights
            highlighted_html = result.highlighted_html
            lime_readable = result.lime_readable

            shap_weights = result.shap_weights
            shap_percent_weights = result.shap_percent_weights
            shap_plot_base64 = result.shap_plot_base64
            shap_readable = result.shap_readable

            lime_summary_for_history = ", ".join(
                [f"{token} ({weight:.4f})" for token, weight in result.lime_weights[:5]]
            )

            analysis = Analysis(
                email_text=email_text,
                prediction=prediction,
                phishing_probability=phishing_probability,
                lime_summary=lime_summary_for_history,
                user_id=current_user.id,
            )

            db.session.add(analysis)
            db.session.commit()

    return render_template(
        "index.html",
        email_text=email_text,
        prediction=prediction,
        phishing_probability=phishing_probability,
        risk_level=risk_level,
        risk_badge_class=risk_badge_class,
        threshold=threshold,
        high_risk_threshold=high_risk_threshold,
        lime_weights=lime_weights,
        lime_percent_weights=lime_percent_weights,
        highlighted_html=highlighted_html,
        lime_readable=lime_readable,
        shap_weights=shap_weights,
        shap_percent_weights=shap_percent_weights,
        shap_plot_base64=shap_plot_base64,
        shap_readable=shap_readable,
        error=error,
        current_user=current_user,
    )

@main.route("/about")
@login_required
def about():
    return render_template("about.html", current_user=current_user)


@main.route("/history")
@login_required
def history():
    analyses = (
        Analysis.query
        .filter_by(user_id=current_user.id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    PHISHING_THRESHOLD = 0.30
    HIGH_RISK_THRESHOLD = 0.60

    formatted_analyses = []

    for analysis in analyses:
        top_indicators = []

        if analysis.lime_summary:
            parts = [item.strip() for item in analysis.lime_summary.split(",") if item.strip()]

            parsed = []
            for item in parts:
                if "(" in item and ")" in item:
                    token = item.split("(")[0].strip()
                    raw_value = item.split("(")[1].replace(")", "").strip()
                    try:
                        score = abs(float(raw_value))
                    except ValueError:
                        score = 0.0
                    parsed.append((token, score))

            parsed.sort(key=lambda x: x[1], reverse=True)
            top_indicators = [token for token, _ in parsed[:4]]

        phishing_probability = analysis.phishing_probability

        if phishing_probability >= HIGH_RISK_THRESHOLD:
            risk_level = "High Risk"
            risk_badge_class = "high-risk"
            final_label = "Phishing"
        elif phishing_probability >= PHISHING_THRESHOLD:
            risk_level = "Suspicious"
            risk_badge_class = "suspicious"
            final_label = "Suspicious"
        else:
            risk_level = "Likely Legitimate"
            risk_badge_class = "legitimate"
            final_label = "Likely Legitimate"

        if final_label == "Phishing":
            if top_indicators:
                readable_explanation = (
                    f"This email was categorised as phishing because the model detected strong suspicious language and patterns. "
                    f"The strongest indicators were {', '.join(top_indicators[:-1])} and {top_indicators[-1]}."
                    if len(top_indicators) > 1
                    else f"This email was categorised as phishing because the strongest indicator was {top_indicators[0]}."
                )
            else:
                readable_explanation = (
                    "This email was categorised as phishing because the model detected strong suspicious signals."
                )

        elif final_label == "Suspicious":
            if top_indicators:
                readable_explanation = (
                    f"This email was categorised as suspicious because several signals suggested possible phishing risk. "
                    f"The most important indicators were {', '.join(top_indicators[:-1])} and {top_indicators[-1]}."
                    if len(top_indicators) > 1
                    else f"This email was categorised as suspicious because the strongest indicator was {top_indicators[0]}."
                )
            else:
                readable_explanation = (
                    "This email was categorised as suspicious because its phishing risk score exceeded the caution threshold."
                )

        else:
            if top_indicators:
                readable_explanation = (
                    f"This email was categorised as likely legitimate because the strongest signals suggested normal or trustworthy communication. "
                    f"The most reassuring indicators were {', '.join(top_indicators[:-1])} and {top_indicators[-1]}."
                    if len(top_indicators) > 1
                    else f"This email was categorised as likely legitimate because the strongest indicator was {top_indicators[0]}."
                )
            else:
                readable_explanation = (
                    "This email was categorised as likely legitimate because its phishing risk score stayed below the suspicious threshold."
                )

        formatted_analyses.append({
            "id": analysis.id,
            "created_at": analysis.created_at,
            "prediction": final_label,
            "risk_level": risk_level,
            "risk_badge_class": risk_badge_class,
            "phishing_probability": phishing_probability,
            "email_text": analysis.email_text,
            "top_indicators": top_indicators,
            "readable_explanation": readable_explanation,
        })

    return render_template(
        "history.html",
        analyses=formatted_analyses,
        current_user=current_user,
    )


@main.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        abort(403)

    total_users = User.query.count()
    total_analyses = Analysis.query.count()

    phishing_count = Analysis.query.filter(Analysis.prediction == "Phishing").count()
    suspicious_count = Analysis.query.filter(Analysis.prediction == "Suspicious").count()
    legitimate_count = Analysis.query.filter(
        Analysis.prediction.in_(["Likely Legitimate", "Legitimate"])
    ).count()

    recent_analyses = (
        Analysis.query
        .order_by(Analysis.created_at.desc())
        .limit(10)
        .all()
    )

    performance_metrics = get_model_performance_metrics()

    return render_template(
        "admin.html",
        current_user=current_user,
        total_users=total_users,
        total_analyses=total_analyses,
        phishing_count=phishing_count,
        suspicious_count=suspicious_count,
        legitimate_count=legitimate_count,
        recent_analyses=recent_analyses,
        performance_metrics=performance_metrics,
    )

