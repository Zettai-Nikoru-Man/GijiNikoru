from src.app.batch.mail_job_log import JobLogMailer
from src.app.config.constants import Constants

JobLogMailer.mail(Constants.Mail.SENDER, Constants.Mail.RECIPIENTS)
