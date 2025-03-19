from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from openai import OpenAI
import os
import atexit

app = Flask(__name__)

options = Options()
#options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service("chromedriver-win64/chromedriver.exe"), options=options)

openaikey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key = openaikey)
def get_completion(prompt): 
    messages=[
        {"role": "system", "content": "Given the text, you must analyze if it aligns with keywords similar to: Services Web design, Web Development ,SEO agency, Ads Agency, Digital marketing agency, Agency, Website creation"},
        {"role": "system", "content": "Your answers will be: 'Accepted' or 'Rejected'"},
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
        #response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        driver.get(url)
        webpage = BeautifulSoup(driver.page_source, "html.parser")
        text_elements = webpage.find_all(["p", "span", "div", "h1", "h2", "h3", "h4", "li"], limit=500) 
        if not text_elements:
            return ""
        keywords = ["services", "website design", "web development", "SEO agency", "ads agency", "digital marketing agency", "agency", "website creation", "marketing"]
        found_texts = []
        total_words = 0
        for element in text_elements:
            text = element.get_text(strip=True)
            words = text.split()
            if any(word in text.lower() for word in keywords):
                found_texts.append(text)    
                total_words += len(words)
            if total_words >= 500:
                break   
        return " ".join(found_texts[:500])
    
    except Exception as e:
        #driver.quit()
        return f"Error: {str(e)}"
    
    
@app.route('/', methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        website = request.form.get("website")
        password = request.form.get("password")
        
        found_texts = soup(website)
        if not found_texts.strip():
            chatgpt = "Rejected by default"
            print( f"\nKeywords found: {chatgpt}")
        else:
            chatgpt = get_completion(found_texts)
            print( f"\nKeywords found: {chatgpt}")
    atexit.register(close_driver)
    return render_template('index.html')

def close_driver():
    global driver
    if driver:
        driver.quit()
        
if __name__ == '__main__':
   app.run(debug=True)
   
