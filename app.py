from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import atexit
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

SMTP_SERVER = "smtp.ethereal.email"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_MAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASS")

options = Options()
options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service("chromedriver-win64/chromedriver.exe"), options=options)

openaikey = os.getenv("OPENAI_API_KEY") # Environment variable must be set
client = OpenAI(api_key = openaikey)
def get_completion(prompt): 
    messages=[
        {"role": "system", "content": "Given the text, you must analyze if it aligns with keywords similar but not limited to: Web design, Web Development, SEO agency, Ads Agency, Digital marketing agency, Agency, Website creation, Web and Brand design"},
        {"role": "system", "content": "Your answers will be: 'Accepted' or 'Rejected' along with a brief explanation of why."},
        {"role": "user", "content": prompt}
        ]
    query = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
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
        driver.get(url)
        webpage = BeautifulSoup(driver.page_source, "html.parser")
        text_elements = webpage.find_all(["p", "span", "div", "h1", "h2", "h3", "h4", "li"], limit=750)
        
        if not text_elements:
            return ""
        
        found_texts = []
        total_words = 0

        for element in text_elements:
            text = element.get_text(strip=True)
            words = text.split()

            if words:  # Avoid empty text elements
                found_texts.extend(words)
                total_words += len(words)

            if total_words >= 750:
                break   
        
        return " ".join(found_texts[:750])  # Ensure only 500 words are returned

    except Exception as e:
        return f"Error: {str(e)}" 
    
    
def send_email(to_email, chatgpt_response):
    try:
        msg = EmailMessage()
        if chatgpt_response.startswith("Accepted"):
             body = (
            "Congratulations! \n\n"
            "Your agency has been approved for the CookieYes Partnership Program. "
            "We’re excited to have you onboard! \n"
            "We will get back to you with further details soon."
            )
        else:
            body = (
            f"Thank you for applying to the CookieYes Partnership Program!\n\n"
            f"Unfortunately, we couldn't approve your application at this time. "
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
        
        
@app.route('/', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        website = request.form.get("website")
        #password = request.form.get("password")
        
        found_texts = soup(website)
        if not found_texts.strip():
            print("Invalid website")
        else:
            chatgpt_response = get_completion(found_texts)
            print(chatgpt_response)
            send_email(email, chatgpt_response)

    return render_template('index.html')

def close_driver():
    global driver
    if driver:
        driver.quit()
        
atexit.register(close_driver)
        
if __name__ == '__main__':
   app.run(debug=True)
   
