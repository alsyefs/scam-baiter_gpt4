# scam-baiter_gpt4 (Email Scam-baiting with GPT-4)
This project is based on a previous project.

# For the results of the experiment, check the folder named 'results'

# Expandable Scam-baiting Mail Server
This is a open-source scam-baiting mail server for all relevant studies. 
You can customize your repliers (also called responders in the source code), 
add your own crawlers for fetching initial scam emails and configure directories and API keys.

## Adding Crawlers
All the crawlers are in "crawler" package. We have implemented two example crawlers, which are "scamletterinfo.py" and "scamsurvivors.py" respectively.

To implement your own crawler, simply add your crawler Python file in this package and make sure to implement "fetch" function. Your crawler should
save the results in JSON format in the MAIL_SAVE_DIR directory. Here is an example of crawler output:
```json
{
    "title": "App/Share your project",
    "url": "http://scamletters.info/2022/04/app-share-your-project/",
    "date": "14.04.2022",
    "from": "j***************0@gmail.com",
    "content": "Sent from: j***************0@gmail.com\nHi,\nHappy to connect.\nI would like to give you a brief backdrop about our company as well\ncore-competency areas in App developments.\n*Spa & Massage App, Shopping App, Wedding App, Food & Drink App, Shopping\nApp, E-Commerce App, IPhone and iPad Apps, Mobile App.*\nPlease tell me what type of App development you need, please share your\ncontact details for more discussion.\nThank you\n\n[image: beacon]"
}
```
After that, you **must** import your crawler and call your "fetch" function in the "fetch_all" function of "__init__.py".

## Customized Responder

The responders are all in "responder.replier". We have 4 example repliers in this file.

To implement your own responder, you need to inhereit "Replier" class and "name" property and overwrite "_gen_text" function. The return value of "_gen_text" should be str and always ends with "[baiter_end]".

Here is an example of a responder
```python
class MyReplier(Replier):
    name = "MyReplier"

    def _gen_text(self, prompt) -> str:
        return "test[baiter_end]"
```
To enable your responder, you need to add the instance of your replier class into list "replier_list" in "/backend/responder/__init__.py", line 8.
```python
from .replier import NeoEnronReplier, NeoRawReplier, Replier, ClassifierReplier, MyReplier
replier_list = [ClassifierReplier(), NeoEnronReplier(), NeoRawReplier(), MyReplier()]
```

## Configurable Directories & Keys
All API configurations are in file "/backend/secret.py".

Here is an example secret.py config:
```python
# OpenAI GPT
OPENAI_API_KEY = ""

# MAILGUN
MAILGUN_API_KEY = ""
MAILGUN_DOMAIN_NAME = ""
MAILGUN_TARGET_EMAIL_TEST = ""

# Twilio for the phone service if needed
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_PHONE_NUMBERS = ['+445555555555', '+15555555555']
TWILIO_CALL_URL = "your endpoint to handle ongoing calls."

# Web application variables:
FLASK_SECRET_KEY = ""
DEFAULT_SUPER_ADMIN_USERNAME = ""
DEFAULT_SUPER_ADMIN_PASSWORD = ""
DEFAULT_ADMIN_USERNAME = ""
DEFAULT_ADMIN_PASSWORD = ""
DEFAULT_USER_USERNAME = ""
DEFAULT_USER_PASSWORD = ""
```

# To run:
After adding your own "/backend/secret.py" file, run as follows:
```python
pip install -r requirements.txt
python app.py
```

After running the app, it will be locally accessible at http://127.0.0.1:10234/
To expose the application to the internet, you need to use a hosting service provider or another service to run in your local machine like ngrok or localtunnel.
For example, after installing ngrok then it can be used with the command: ngrok http --domain=some-domain.com 10234

For the complete list of scam-baiting conversations, navigate to `/backend/emails` and there are folders and reports for a complete scam-baiting experiment.