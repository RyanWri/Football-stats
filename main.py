from fastapi import FastAPI
from email_validator import validate_email, EmailNotValidError
from api.models.contact_email import ContactForm
from api.routers.contact_email import send_contact_form_to_my_email


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/predictions")
def get_predictions():
    # Logic to retrieve predictions
    return {"message": "This is the GET predictions endpoint"}


@app.post("/predictions")
def create_prediction():
    # Logic to create a new prediction
    return {"message": "This is the POST predictions endpoint"}


@app.post("/send-email")
async def send_email(contact_form: ContactForm):
    try:
        # Check that the email address is valid.
        emailinfo = validate_email(contact_form.from_address, check_deliverability=True)
        # After this point, use only the normalized form of the email address
        email = emailinfo.normalized
        send_contact_form_to_my_email(email, "test email", contact_form.message)
        return {"message": "Email sent successfully"}

    except EmailNotValidError as email_err:
        # The exception message is human-readable explanation of why it's not a valid (or deliverable) email address.
        print(str(email_err))
        return {"message": "Invalid email address"}

    except Exception as e:
        print(e)
        return {"message": "email delivery failed"}
