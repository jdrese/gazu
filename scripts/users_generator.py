#!/usr/bin/env python
# -*- coding: utf-8 -*-

# imports
import os
import string
import random
import gazu
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def create_message(user_name, kitsu_server, login, password):
    """ Generates the html body message

    Args:
        user_name (str): user name to use on the body
        kitsu_server (str): Kitsu webpage
        login (str): full login address
        password (str): password to create for the user
    Returns:
        str: A formated HTML page that contains a welcome page to Kitsu
    """

    # creates basic HTML structure
    htlm_message = """\
    <html>
      <head>
      </head>
      <body style="margin: 25px;">
        <center>
          {body_message}
        </center>
      </body>
    </html>
    """

    # creates body message
    body = """\
    <h3>Bienvenue sur Kitsu {name}</h3>
    <br>

    <p>Bienvenu sur <b>Kitsu</b> notre plateforme de suivi de production.</p>
    <img src={image}></img>

    <p>Tu peux accéder sur la plateforme sur {kitsu}</p>
    <br><br>

    <p>Voici tes codes d'accès.</p>
    <p>Login(email): {email}</p>
    <p>Password: <b>{user_pass}</b></p>
    """

    # path to Kitsu image
    kitsu_image = os.path.abspath(os.path.join(
        __file__, "../../resources/images/kitsu.jpg"))  # CHANGE IMAGE HERE

    body = body.format(image=kitsu_image,
                       name=user_name,
                       kitsu=kitsu_server,
                       email=login,
                       user_pass=password)

    return htlm_message.format(body_message=body)


def set_kitsu(host, login, password):
    """ Log into your Kitsu server

    Args:
        host (str): path to your Kitsu server
        login (str): your Kitsu login
        password (str): your Kistu password
    """

    # checks for host string end
    if not host.endswith("/"):
        host += "/"

    # set gazu host
    gazu.client.set_host("{}api".format(host))

    # login
    return gazu.log_in(login, password)


def setup_smtp(smtp_server, port, tls_encryption=False, login=None,
               password=None):
    """ Setups the smtp service

    Args:
        smtp_server (str): your smtp outgoing email server service
        port (int): your smtp outgoing server port
        tls_encryption (bool): If tls encryption type is required

    Returns:
        SMTP: the smtp mailing service (class object)
    """

    service = SMTP(smtp_server, port)

    if tls_encryption:
        service.starttls()
        service.login(login, password)

    return service


def generate_kitsu_users(users):
    """ Generates Kitsu user accounts

    Args:
        users (list): string list for your users
    """

    # set Kitsu address
    kitsu_server = "https://your.kitsu.server.com/"  # SET YOUR KITSU ADDRESS

    # set email sender
    sender = "admin.user@yourdomain.com"  # ADMIN KITSU USER / EMAIL SENDER
    admin = "yourKitsuPassword"  # YOUR KITSU ADMIN PASSWORD

    # loop though users and generates accounts
    for user in users:

        print("\n\n#-----------------------------#")
        print("Creating user: {}".format(user))

        print("Login into Kitsu as admin...")
        # logins into Kitsu / needs to relog for each user
        set_kitsu(kitsu_server, sender, admin)

        # set user name ------------------------------------------------------#
        first_name = user.split(".")[0]
        last_name = user.split(".")[-1]
        user_email = "{}@yourdomain.com".format(user)  # NEW USER KITSU EMAIL

        # create Kitsu user --------------------------------------------------#
        has_user = gazu.person.get_person_by_email(user_email)
        if has_user:
            print("User {} already exists in the DB! Passing...".format(user))
            continue

        # creates Kitsu user -------------------------------------------------#
        print("Creating Kitsu user")
        gazu.person.new_person(first_name=first_name,
                               last_name=last_name,
                               email=user_email)

        # generate user password ---------------------------------------------#
        characters = string.ascii_letters + string.digits
        password = ("".join(random.choice(characters)
                    for x in range(random.randint(10, 10))))  # @unusedVariable
        # --------------------------------------------------------------------#

        # changing user password ---------------------------------------------#
        print("Login into user to edit password...")
        set_kitsu(kitsu_server, user_email, "default")
        gazu.client.post("/auth/change-password",
                         {"old_password": "default",
                          "password": "{}".format(password),
                          "password_2": "{}".format(password)})
        # --------------------------------------------------------------------#

        # setups email -------------------------------------------------------#
        print("Generating email...")
        recipients = [sender]  # ADD HERE OTHER RECIPIENTS
        mail = MIMEMultipart('alternative')
        mail['Subject'] = "Bienvenu sur Kitsu"  # THE EMAIL SUBJECT
        mail['From'] = sender
        mail['To'] = user_email
        mail['Cc'] = ", ".join(recipients)

        # creates the HTML message
        msg = (create_message(
            user_name="{} {}".format(first_name.title(), last_name.title()),
            kitsu_server=kitsu_server,
            login=user_email,
            password=password))

        # sets MIME top HTML type
        content = MIMEText(msg, 'html')

        # Attach into message container.
        mail.attach(content)
        # --------------------------------------------------------------------#

        # setups SMTP server -------------------------------------------------#
        print("Setup SMTP server...")
        mail_service = setup_smtp('smtp.yourdomaine.com',  # SMTP OUT SERVER
                                  21,  # SMPT PORT
                                  True,  # SET TRUE IF ENCRIPTION IS TLS
                                  "your@email.be",
                                  "youremailpassword")
        # --------------------------------------------------------------------#

        # sends email --------------------------------------------------------#
        print("Sending email...")
        mail_service.sendmail(sender, recipients, mail.as_string())
        mail_service.quit()
        # --------------------------------------------------------------------#

        print("User created")


if __name__ == "__main__":
    users = ["user.a",
             "user.b",
             ]

    print("Start Generating accounts")
    generate_kitsu_users(users)
    print("Finished")
