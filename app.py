import os
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from dotenv import load_dotenv
from paystackapi.paystack import Paystack as PaystackAPI
from paystackapi.transaction import Transaction # CORRECT IMPORT
import traceback
import sys
from urllib.parse import urlparse

# IMPORTANT: Load environment variables at the very beginning
load_dotenv() 

# Configure Paystack API after loading environment variables
paystack = PaystackAPI(secret_key=os.getenv("PAYSTACK_SECRET_KEY"))

# Configure Gemini API with your API key from the environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) 

app = Flask(__name__)

# Configure a secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "your_strong_fallback_secret_key")

# Database configuration - CHANGE THESE TO YOUR CREDENTIALS
db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': os.getenv("MYSQL_PASSWORD"), 
    'database': 'knowledge_navigator'
}

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    if 'DATABASE_URL' in os.environ:
        # Use urlparse to break down the DATABASE_URL string
        url = urlparse(os.environ['DATABASE_URL'])
        
        # Check if the URL scheme is 'mysql' or 'mysql+pymysql'
        if url.scheme in ['mysql', 'mysql+pymysql']:
            return mysql.connector.connect(
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port if url.port else 3306,
                database=url.path[1:]
            )
    else:
        # Your local configuration will be used for development
        return mysql.connector.connect(**db_config)


@app.route('/')
def home():
    """Renders the homepage of the application."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash('Please provide both username and password.', 'error')
        return render_template('login.html')

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id, username, password FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

    except Exception as e:
        print(f"Login database error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        flash('Database error. Please try again later.', 'error')
        return render_template('login.html')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not username or not password or not email:
        flash('Please provide username, email, and password.', 'error')
        return render_template('register.html')

    hashed_password = generate_password_hash(password)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            flash('Username or email already exists. Please choose another.', 'error')
            return render_template('register.html')

        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, hashed_password))
        conn.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login_page'))

    except Exception as e:
        # This will now print the full traceback to the logs
        print(f"Registration database error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        flash('An error occurred while registering. Please try again.', 'error')
        return render_template('register.html')

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('home'))

@app.route('/modules')
def modules_page():
    if 'user_id' not in session:
        flash('Please log in to view the modules.', 'error')
        return redirect(url_for('login_page'))
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT title, description, slug, is_premium FROM modules ORDER BY id')
        modules = cursor.fetchall()
        return render_template('modules.html', username=session.get('username'), modules=modules)
    except mysql.connector.Error:
        flash('Database error. Please try again later.', 'error')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/modules/<slug>')
def module_page(slug):
    if 'user_id' not in session:
        flash('Please log in to view this module.', 'error')
        return redirect(url_for('login_page'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT title, is_premium FROM modules WHERE slug = %s', (slug,))
        module = cursor.fetchone()

        if not module:
            flash('Module not found.', 'error')
            return redirect(url_for('modules_page'))

        if module['is_premium']:
            cursor.execute('SELECT is_pro_member FROM users WHERE id = %s', (session.get('user_id'),))
            user_status = cursor.fetchone()

            if not user_status or not user_status['is_pro_member']:
                flash('This is a premium module. Please subscribe to gain access.', 'error')
                return redirect(url_for('subscription_page'))

        return render_template(f'{slug}_module.html', username=session.get('username'), title=module['title'])

    except mysql.connector.Error:
        flash('Database error. Please try again later.', 'error')
        return redirect(url_for('dashboard'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/ai-explain', methods=['POST'])
def ai_explain():
    if 'user_id' not in session:
        return jsonify({'error': 'You must be logged in to use this feature.'}), 401

    question = request.form.get('question', '').strip()
    if not question:
        return jsonify({'error': 'No question provided.'}), 400

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"Explain the following concept in a very simple way, like you're talking to a middle school student. Keep the explanation concise and easy to understand. The concept is: '{question}'"

        response = model.generate_content(prompt)

        if response.text:
            explanation = response.text
        else:
            explanation = "Sorry, I couldn't generate an explanation for that. Please try another question."
            
        return jsonify({'explanation': explanation})

    except Exception as e:
        print(f"Gemini API error: {e}")
        return jsonify({'error': 'Failed to connect to AI service. Please try again.'}), 500
    
@app.route('/subscription')
def subscription_page():
    if 'user_id' not in session:
        flash('Please log in to manage your subscription.', 'error')
        return redirect(url_for('login_page'))
    
    return render_template('subscription.html', username=session.get('username'))
    
@app.route('/create-paystack-payment', methods=['POST'])
def create_paystack_payment():
    if 'user_id' not in session:
        flash('Please log in to subscribe.', 'error')
        return redirect(url_for('login_page'))

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM users WHERE id = %s", (session.get('user_id'),))
        user_info = cursor.fetchone()
        
        if not user_info or not user_info['email']:
            flash('Your account needs a valid email to subscribe.', 'error')
            return redirect(url_for('subscription_page'))
            
        user_email = user_info['email']

    except mysql.connector.Error:
        flash('Database error. Please try again.', 'error')
        return redirect(url_for('subscription_page'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    amount_kobo = 500  

    try:
        # CORRECTED: Call initialize on the imported Transaction class
        response = Transaction.initialize(
            email=user_email,
            amount=amount_kobo,
            callback_url=url_for('paystack_callback', _external=True)
        )

        if response and response.get('status'):
            authorization_url = response['data']['authorization_url']
            return redirect(authorization_url, code=302)
        else:
            flash('Payment initialization failed. Please try again.', 'error')
            return redirect(url_for('subscription_page'))

    except Exception as e:
        print(f"Paystack API Error: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('subscription_page'))

@app.route('/paystack/callback')
def paystack_callback():
    reference = request.args.get('reference')
    if not reference:
        flash('Payment verification failed. No reference found.', 'error')
        return redirect(url_for('subscription_page'))

    conn = None
    cursor = None
    try:
        # CORRECTED: Call verify on the imported Transaction class
        response = Transaction.verify(reference=reference)

        if response and response['data']['status'] == 'success':
            user_email = response['data']['customer']['email']

            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE email = %s', (user_email,))
            user_info = cursor.fetchone()
            
            if user_info:
                user_id = user_info[0]
                cursor.execute('UPDATE users SET is_pro_member = TRUE WHERE id = %s', (user_id,))
                conn.commit()
                flash('Subscription successful! You now have full access.', 'success')
            else:
                flash('Payment successful, but we could not find your account.', 'error')

        else:
            flash('Payment failed. Please try again.', 'error')
            return redirect(url_for('subscription_page'))

    except Exception as e:
        print(f"Paystack API Error: {e}")
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('subscription_page'))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for('modules_page'))

if __name__ == '__main__':
    app.run(debug=True)








