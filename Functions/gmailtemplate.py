import smtplib, os
from sys import argv
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders


class Gmail:
	'''To use this class, create the object with initialized variables.
		Then run functions in order '''
	
	def __init__(self, username, password):
		''' When initialized put username and password as 1st
			 and 2nd arg'''
		self.username = username
		self.password = password
		
	def input_address(self, to_addr, from_addr):
		'''1st argument is the email addresss that you're mailing to and
			2nd is your email address'''
		self.to_addr = to_addr
		self.from_addr = from_addr
	
	def email_content(self, subject, text, attachments):
		''' Subject of email, body of text, list of attachment files
			in the same directory as script (e.g. ['file1.txt',
			'file2.txt']'''
		self.subject = subject
		self.text = text
		self.attachments = attachments
	def server(self, server, port):
		'''Server and Port of the service you're using
			For reference: Gmail server and port = smtp.gmail.com:587'''
		self.server = server
		self.port = port
	
	def send_mail(self):
		msg = MIMEMultipart()
		msg['To'] = self.to_addr
		msg['From'] = self.from_addr
		msg['Subject'] = self.subject

		msg.attach( MIMEText(self.text) )
		
		for fil in self.attachments:
			part= MIMEBase('application', 'octet-stream')	
			part.set_payload( open(fil, 'rb').read() )
			encoders.encode_base64(part)
			part.add_header('Content-Disposition',
				'attachment; filename = "{0}"'.format(os.path.basename(fil)))
			msg.attach(part)

		try:	
			session = smtplib.SMTP(self.server, self.port)
			session.starttls()
			session.login(self.username, self.password)
			session.sendmail(self.from_addr, self.to_addr,
							 msg.as_string())
			session.quit()
			print ('Succes')
		except:
			print ('Failure')
		
def main():
	pass

if __name__ == '__main__':
	main()
