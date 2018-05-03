class Constants:
    """Application constants template

    Please make constants.py by copying this and configure it.
    """

    class Mail:
        SMTP_SERVER = ""
        SENDER = ""
        SENDER_PASSWORD = ""
        RECIPIENTS = [  # mail addresses
            ""
        ]

    class App:
        ROOT = __file__.replace("config/constants.py", "")

    class Niconico:
        LOGIN_ID = ""  # Your niconico login id
        PASSWORD = ""  # Your niconico login password
