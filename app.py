from flask import Flask, request, jsonify
import re, socks
import dns
from dns import resolver
import socket
import smtplib
import time
import random
from email_split import email_split
# for the api
import json
from io import StringIO
import sys
import logging
#############################################
# FLASK STUFF
#############################################

app = Flask(__name__)

@app.route('/api/v1/verify', methods=['GET'])
def check1():
  args = request.args
  email = args.get("email")
  #Step 1: Check email
  #Check using Regex that an email meets minimum requirements, throw an error if not
  addressToVerify = email
  match = re.match(
    '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
    addressToVerify)

  if match == None:
    print('Bad Syntax in ' + addressToVerify)
    rzlt = {"email": email, "status": "invalid", "reason": "bad_syntax"}
    return jsonify(rzlt)
    #pass

  #Step 2: Getting MX record
  #socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "89.47.234.26", 1085)
  #socket.socket = socks.socksocket
  #socks.wrapmodule(smtplib)
  #Pull domain name from email address
  domain_name = email.split('@')[1]

  #get the MX record for the domain
  try:
    records = dns.resolver.resolve(domain_name, 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)
  except dns.resolver.NoAnswer:
    rzlt = {"email": email, "status": "invalid", "reason": "no_record_found"}
    return jsonify(rzlt)

  #Step 3: ping email server
  #check if the email address exists

  # Get local server hostname
  host = socket.gethostname()

  # SMTP lib setup (use debug level for full output)
  server = smtplib.SMTP()
  server.set_debuglevel(1)
  # Save the original stderr
  original_stderr = sys.stderr

  # Redirect stderr to a StringIO buffer
  sys.stderr = debug_output = StringIO()
  # SMTP Conversation
  try:
    server.connect(mxRecord)
    server.ehlo(host)  # Add this line to send the EHLO command
    server.mail(f'johndoe@www.validateforlife.com')
    code, message = server.rcpt(str(addressToVerify))
    server.quit()
  except smtplib.SMTPServerDisconnected:
    print('heated up')
    time.sleep(10)
    code = 666
  # Reset stderr to the original value
  sys.stderr = original_stderr
    # Assume 250 as Success
  if code == 250:
    print(code)
    rzlt = {"email": email, "status": "valid", "reason": "accepted_email","debug":debug_output.getvalue()}
    return jsonify(rzlt)
  elif code == 666:
    print('smtp error; status: unknown')
    rzlt = {"email": email, "status": "invalid", "reason": "smtp_error","debug":debug_output.getvalue()}
    return jsonify(rzlt)
  else:
    print(code)
    rzlt = {"email": email, "status": "invalid", "reason": "invalid_email","debug":debug_output.getvalue()}
    return jsonify(rzlt)
  debug_output.close()
