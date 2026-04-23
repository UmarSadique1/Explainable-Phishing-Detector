


#  PhishGuard AI — Explainable Phishing Detection System



##  Overview
PhishGuard AI is a full-stack web-based phishing detection system that uses machine learning to classify emails as **phishing** or **legitimate**, while also providing **explainable AI insights** to help users understand *why* a prediction was made.

The system is designed not only to detect phishing attacks but also to **educate users**, allowing them to develop their own ability to recognise suspicious emails before confirming with the AI analyser.





## Objectives
- Detect phishing emails using machine learning
- Provide explainable predictions using LIME and SHAP
- Allow users to analyse emails through a web interface
- Store and track analysis history
- Provide an admin dashboard with performance metrics
- Educate users on phishing detection techniques



##  Features

###  Email Analyzer
- Paste any email text
- Classifies as:
  - **Phishing**
  - **Legitimate**
- Displays prediction probability
- Provides explainability (LIME / SHAP)



### Explainable AI
- **LIME (Local Interpretable Model-Agnostic Explanations)**
  - Highlights important words influencing the prediction
- **SHAP (SHapley Additive Explanations)**
  - Provides feature importance insights



### User System
- User registration & login
- Role-based access:
  - **Admin**
  - **Standard User**
- Each user has:
  - Analysis history
  - Stored predictions



### History Page
- View previous analyses
- Includes:
  - Email text
  - Prediction
  - Probability
  - Timestamp



###  Admin Dashboard
- Total users
- Total analyses
- Phishing vs legitimate counts
- Model performance metrics:
  - Accuracy
  - Precision
  - Recall
  - F1 Score
  - ROC-AUC
- Recent activity table



###  Educational Component
- Helps users understand:
  - What phishing is
  - Common warning signs
  - Suspicious language patterns
- Supports a **“learn first, verify second”** workflow



##  Machine Learning Model

### Model Type
- Logistic Regression

### Pipeline
- TF-IDF Vectorizer
- Logistic Regression classifier

### Dataset
The model is trained on a **combined real-world dataset**:
- Enron Email Dataset (legitimate emails)
- SpamAssassin Dataset:
  - Easy Ham (legitimate)
  - Hard Ham (legitimate)
  - Spam (phishing)

---

###  Evaluation Metrics

Example performance:

- Accuracy: ~97%
- Precision: ~90%
- Recall: ~96%
- F1 Score: ~93%
- ROC-AUC: ~0.997

#### Interpretation:
- High **recall** ensures phishing emails are detected
- Slightly lower **precision** reflects acceptable false positives
- High **ROC-AUC** shows excellent classification capability



##  Installation & Setup

### 1. Clone the repository

git clone <your-repo-url>
cd explainable-phishing-detector

2. Create virtual environment:
-python3 -m venv venv

-source venv/bin/activate

3. Install dependencies

-pip install -r requirements.txt

4. Prepare dataset

-python3 scripts/prepare_email_dataset.py

5. Train model

-python3 scripts/train_baseline.py


6. Run application

python3 run.py

Open in browser:

http://127.0.0.1:5000


pwd
source venv/bin/activate
source venv/bin/activate
rm -f instance/site.db
rm -f site.db
python run.py


##  Admin Login

Email:     [Admin@PhishGuard.co.uk]

Password:  PhishGuard123!



##  Test User Accounts

| Email                                   | Password     |
| --------------------------------------- | -----------  |
| [user1@test.com](mailto:user1@test.com) | password1231 |
| [user2@test.com](mailto:user2@test.com) | password1232 |
| [user3@test.com](mailto:user3@test.com) | password1233 |
| [user4@test.com](mailto:user4@test.com) | password1234 |
| [user5@test.com](mailto:user5@test.com) | password1235 |

password1238 - user8@test.com

## Sample Legitimate Emails (Test Data)

### 1

Subject: Meeting agenda for tomorrow
Hi everyone,
Just a reminder that our project meeting is scheduled for tomorrow at 3pm.
Best regards

---

### 2

Subject: Weekly report update
Please find attached the weekly report. Let me know if you have any feedback.

---

### 3

Subject: Lunch plans
Hey, are we still on for lunch today at 1pm?

---

### 4

Subject: Project submission
The final project has been uploaded to the portal. Please review when possible.

---

### 5

Subject: Holiday request
I would like to request annual leave for next Friday.

---

## Sample Phishing Emails (Test Data)

### 1

Subject: Urgent - account verification required
We detected unusual activity. Verify your account immediately:
http://bit.ly/verify-now

---

### 2

Subject: Your bank account suspended
Click here to restore access immediately:
http://secure-login-alert.com

---

### 3

Subject: You won a prize!
Congratulations! Claim your reward now:
http://free-prize-now.com

---

### 4

Subject: Payment failed
Your payment failed. Update your details here:
http://update-payment-info.com

---

### 5

Subject: Security alert
Suspicious login detected. Confirm your identity now:
http://security-check-login.com

### 6
Subject: Meeting agenda for tomorrow

Hi everyone,

Just a reminder that our project meeting is scheduled for tomorrow at 3 pm in Room B214.
I’ve attached the updated agenda and notes from last week.

Let me know if you can’t make it.

Best regards,
Alex




### 7
Subject: Urgent – account verification required

We detected unusual activity on your account.
You must verify your information immediately to avoid suspension.

Click the link below to confirm your details:
http://bit.ly/verify-now

Failure to act within 24 hours will result in account termination.

Support Team





Author:

Umar Sadique
w1985391
Computer Science 
Final Year Project


### 8

Subject: Account notice

Hi,

There has been a minor update to your account. Please check your information when convenient to avoid any disruption:

https://example.com/update

Thank you.


