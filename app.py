from flask import Flask, request, render_template, redirect, url_for
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import atexit
import smtplib
from email.message import EmailMessage
from urllib.parse import urlparse
import csv
from datetime import datetime

app = Flask(__name__)

# Set configurations for email
SMTP_SERVER = "smtp.ethereal.email"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_MAIL")     # Environment variable must be set
SENDER_PASSWORD = os.getenv("SENDER_PASS")  # Environment variable must be set

options = Options()
options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service("chromedriver-win64/chromedriver.exe"), options=options)

openaikey = os.getenv("OPENAI_API_KEY") # Environment variable must be set
client = OpenAI(api_key = openaikey)
def get_completion(prompt): 
    messages=[
        {"role": "system", "content": "Given the text, you must check if it contains any or all keywords similar but not limited to: Web design, Web Development, SEO agency, Ads Agency, Digital marketing agency, Agency, Website creation, Web and Brand design"},
        {"role": "system", "content": "Your answers will be: 'Accepted' or 'Rejected' along with a short explanation of why."},
        {"role": "system", "content": "Output format: Accepted/Rejected : Explaination"},
        {"role": "user", "content": prompt}
        ]
    query = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
    return query.choices[0].message.content

def soup(url):
    try:
        driver.get(url)     # Fetch webpage using Selenium
        webpage = BeautifulSoup(driver.page_source, "html.parser")  # Initialize BeautifulSoup
        text_elements = webpage.find_all(["p", "span", "div", "h1", "h2", "h3", "h4", "li"], limit=750) # Limit the elements as AI has limited input tokens
        
        if not text_elements:
            return ""
        
        found_texts = []
        total_words = 0

        for element in text_elements:
            text = element.get_text(strip=True) # Extract text from HTML tags in text_element
            words = text.split()   # Splitting text into a list of words

            if words:  # To avoid empty text elements
                found_texts.extend(words)
                total_words += len(words)

            if total_words >= 750:
                break   
        
        return " ".join(found_texts[:750])  # Convert to string

    except Exception as e:
        print(f"Error: {str(e)}")
        return None
       
def send_email(to_email, url, chatgpt_response):
    try:
        # To extract the domain name from given url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc  # Remove https
        if domain.startswith("www."):
            domain = domain[4:]
        
        msg = EmailMessage()
        if chatgpt_response.startswith("Accepted"):
             body = (
            f"Congratulations! \n\n"
            f"Your agency, \"{domain}\", has been approved for the CookieYes Partnership Program. "
            f"We’re excited to have you onboard! \n"
            f"We will get back to you with further details soon."
            )
        else:
            body = (
            f"Thank you for applying to the CookieYes Partnership Program!\n\n"
            f"Unfortunately, we couldn't approve {domain}'s application at this time. "
            f"Our automation systems have narrowed the reason to : \n\n[ {chatgpt_response} ]\n\n "
            f"Feel free to apply again in the future after making necessary improvements."
            )
        msg.set_content(body)
        msg["Subject"] = "CookieYes Registration"
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        print(f"Test email sent to {to_email} (Check Ethereal dashboard)")
    except Exception as e:
        print(f"Error sending email: {e}")
        
def save_to_csv(email, website, status, filename="registrations.csv"):  # CSV in app.py's directory by default
    file_exists = os.path.isfile(filename)  # Check if file exists
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Current time

    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write the header only if the file is newly created
        if not file_exists:
            writer.writerow(["Email", "Website", "Status", "Timestamp"]) 

        # Write the data
        writer.writerow([email, website, status, timestamp])
    
@app.route('/', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":    # Execute only if a POST request is received
        email = request.form.get("email")
        website = request.form.get("website")
        
        found_texts = soup(website)
        if found_texts is None or not found_texts.strip():
            return redirect(url_for("invalid"))
        else:
            chatgpt_response = get_completion(found_texts)
            send_email(email, website, chatgpt_response)
            save_to_csv(email, website, chatgpt_response)

        return redirect(url_for("end"))
    
    return render_template("index.html")


@app.route("/end")
def end():
    return render_template("thanks.html")

@app.route("/invalid")
def invalid():
    return render_template("invalid.html")

def close_driver():
    global driver
    if driver:
        driver.quit()
        
atexit.register(close_driver)
        
if __name__ == '__main__':
   app.run(debug=True)
   
