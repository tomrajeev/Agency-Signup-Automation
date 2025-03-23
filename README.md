
# Agency Signup Automation

This project automates the agency verification process for CookieYes using Generative AI and automated email notifications. It eliminates the need for manual verification by leveraging GPT-4 to analyze agency websites and determine eligibility based on predefined criteria.

# Tech Stack

Python (Flask)

OpenAI GPT-4 (for AI-based decision making)

BeautifulSoup (for web scraping)

Selenium (for rendering JavaScript reliant webpages)

Ethereal Mail (for testing emails)


## Features

- Web scraping to extract relevant content from agency websites.
- AI-driven website analysis using GPT-4.
- Email notifications (Welcome or Rejection emails).
- Ethereal Mail integration for testing email workflows.


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SENDER_MAIL`

`SENDER_PASS`

`OPENAI_API_KEY`

Since this is Ethereal Mail based system, the MAIL and PASS can be obtained from: https://ethereal.email/

It is also possible to use the Gmail system by changing `SMTP_SERVER` to 'smtp.gmail.com'

The OpenAI key must be aquired from : https://platform.openai.com/docs/overview


## Deployment

To deploy this project run it as any other Flask app after:

```bash
  pip install -r requirements.txt
```

Default url : http://127.0.0.1:5000/

Ensure the correct version of chromedriver, compatible with your Chrome browser, is available : https://googlechromelabs.github.io/chrome-for-testing/