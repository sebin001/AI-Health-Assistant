from datetime import datetime, timedelta
from pathlib import Path
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.utils import timezone

from assist.models import MedicineReminder


class InlineLogoEmail(EmailMessage):

    def __init__(
        self,
        subject,
        body,
        from_email,
        to,
        html_content,
        logo_path=None,
        **kwargs
    ):
        super().__init__(
            subject=subject,
            body=body,
            from_email=from_email,
            to=to,
            **kwargs
        )

        self.html_content = html_content
        self.logo_path = logo_path

    def message(self, policy=None):
        """
        Create an email with the logo embedded inline.

        The logo is NOT added as a normal attachment.
        """

        # Main alternative container
        msg = MIMEMultipart("alternative")

        msg["Subject"] = self.subject
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to)
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()

        # Add extra headers if configured
        for name, value in self.extra_headers.items():
            if name not in msg:
                msg[name] = value

        # Plain-text version
        plain_part = MIMEText(
            self.body,
            "plain",
            "utf-8"
        )

        msg.attach(plain_part)

        # HTML + inline image
        related = MIMEMultipart("related")

        html_part = MIMEText(
            self.html_content,
            "html",
            "utf-8"
        )

        related.attach(html_part)

        # Add logo ONLY as inline content
        if self.logo_path and self.logo_path.exists():

            with open(
                self.logo_path,
                "rb"
            ) as logo_file:

                logo = MIMEImage(
                    logo_file.read()
                )

            logo.add_header(
                "Content-ID",
                "<ai-health-logo>"
            )

            logo.add_header(
                "Content-Disposition",
                "inline"
            )

            related.attach(logo)

        msg.attach(related)

        return msg


class Command(BaseCommand):

    help = "Send due medicine email reminders."

    def handle(self, *args, **kwargs):

        now = timezone.localtime()
        today = now.date()

        current_minute = now.replace(
            second=0,
            microsecond=0
        )

        window_start = (
            current_minute - timedelta(minutes=2)
        )

        medicines = MedicineReminder.objects.filter(
            is_active=True,
            email_reminder=True,
            start_date__lte=today
        )

        sent_count = 0

        for medicine in medicines:

            # Ignore expired medicines
            if (
                medicine.end_date
                and medicine.end_date < today
            ):
                continue

            reminder_datetime = timezone.make_aware(
                datetime.combine(
                    today,
                    medicine.reminder_time
                ),
                timezone.get_current_timezone()
            )

            # Check whether reminder time has arrived
            if not (
                window_start
                <= reminder_datetime
                <= now
            ):
                continue

            # Prevent duplicate email for the same
            # scheduled minute.
            if medicine.last_reminder_sent:

                last_sent = timezone.localtime(
                    medicine.last_reminder_sent
                )

                if (
                    last_sent.date() == today
                    and last_sent.hour
                    == reminder_datetime.hour
                    and last_sent.minute
                    == reminder_datetime.minute
                ):
                    continue

            user = medicine.user

            if not user.email:

                self.stdout.write(
                    self.style.WARNING(
                        f"No email address for user: "
                        f"{user.username}"
                    )
                )

                continue

            subject = (
                f"Medicine Reminder - "
                f"{medicine.medicine_name}"
            )

            # ------------------------------------------------
            # PLAIN TEXT EMAIL
            # ------------------------------------------------

            plain_message = f"""
Hello {user.username},

This is your medicine reminder from AI Health Assistant.

Medicine: {medicine.medicine_name}
Dosage: {medicine.dosage}
Scheduled Time: {medicine.reminder_time.strftime("%I:%M %p")}

Please take your medicine according to your prescribed schedule.

Notes:
{medicine.notes if medicine.notes else "No additional notes."}

Stay healthy,

AI Health Assistant
Smart. Simple. Healthier.
"""

            # ------------------------------------------------
            # HTML EMAIL
            # ------------------------------------------------

            html_message = f"""
<!DOCTYPE html>
<html>

<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

</head>


<body style="
margin:0;
padding:0;
background:#f3f8fb;
font-family:Arial,Helvetica,sans-serif;
">


<table
width="100%"
cellpadding="0"
cellspacing="0"
border="0"
style="
background:#f3f8fb;
padding:35px 15px;
"
>

<tr>

<td align="center">


<!-- MAIN EMAIL CARD -->

<table
width="600"
cellpadding="0"
cellspacing="0"
border="0"
style="
max-width:600px;
width:100%;
background:#ffffff;
border-radius:18px;
overflow:hidden;
"
>


<!-- LOGO + TITLE -->

<tr>

<td
align="center"
style="
padding:28px 25px 22px;
"
>


<!-- SMALL ROUND LOGO -->

<img
src="cid:ai-health-logo"
alt="AI Health Assistant"
width="70"
height="70"
style="
display:block;
width:70px;
height:70px;
border-radius:50%;
object-fit:cover;
margin:0 auto 16px;
"
>


<div style="
font-size:27px;
line-height:1.2;
font-weight:bold;
color:#123b67;
margin-bottom:7px;
">
Medicine Reminder
</div>


<div style="
font-size:15px;
color:#66809a;
">
AI Health Assistant
</div>


</td>

</tr>


<!-- DIVIDER -->

<tr>

<td style="
padding:0 35px;
">

<div style="
height:2px;
background:#d9edf5;
font-size:0;
line-height:0;
">
&nbsp;
</div>

</td>

</tr>


<!-- GREETING -->

<tr>

<td style="
padding:28px 35px 10px;
">


<div style="
font-size:17px;
color:#526b83;
margin-bottom:14px;
">

Hello

<strong style="
color:#123b67;
">

{user.username}

</strong>,

</div>


<div style="
font-size:16px;
color:#526b83;
line-height:1.6;
">

It's time for your scheduled medicine.

</div>


</td>

</tr>


<!-- MEDICINE CARD -->

<tr>

<td style="
padding:20px 35px;
">


<table
width="100%"
cellpadding="0"
cellspacing="0"
border="0"
style="
background:#eff9fc;
border-radius:15px;
border:1px solid #dceff5;
"
>


<tr>

<td style="
padding:25px;
">


<div style="
font-size:13px;
font-weight:bold;
letter-spacing:1px;
color:#66809a;
margin-bottom:8px;
">
MEDICINE
</div>


<div style="
font-size:25px;
line-height:1.3;
font-weight:bold;
color:#123b67;
margin-bottom:22px;
">

{medicine.medicine_name}

</div>


<!-- DOSAGE + TIME -->

<table
width="100%"
cellpadding="0"
cellspacing="0"
border="0"
>

<tr>


<td
width="50%"
valign="top"
style="
padding-right:15px;
"
>

<div style="
font-size:13px;
color:#66809a;
margin-bottom:6px;
font-weight:bold;
">
DOSAGE
</div>


<div style="
font-size:17px;
font-weight:bold;
color:#123b67;
">

{medicine.dosage}

</div>


</td>


<td
width="1"
style="
background:#d5eaf1;
font-size:0;
"
>
&nbsp;
</td>


<td
width="50%"
valign="top"
style="
padding-left:20px;
"
>

<div style="
font-size:13px;
color:#66809a;
margin-bottom:6px;
font-weight:bold;
">
SCHEDULED TIME
</div>


<div style="
font-size:17px;
font-weight:bold;
color:#123b67;
">

{medicine.reminder_time.strftime("%I:%M %p")}

</div>


</td>


</tr>

</table>


</td>

</tr>

</table>


</td>

</tr>


<!-- NOTES -->

<tr>

<td style="
padding:5px 35px 15px;
">


<div style="
font-size:14px;
font-weight:bold;
color:#526b83;
margin-bottom:7px;
">
Notes
</div>


<div style="
font-size:14px;
color:#526b83;
line-height:1.6;
">

{medicine.notes if medicine.notes else "No additional notes."}

</div>


</td>

</tr>


<!-- MESSAGE -->

<tr>

<td style="
padding:10px 35px 15px;
">


<div style="
font-size:14px;
color:#526b83;
line-height:1.7;
">

Please take your medicine according to your
prescribed schedule.

</div>


</td>

</tr>


<!-- SIGNATURE -->

<tr>

<td style="
padding:10px 35px 30px;
">


<div style="
font-size:15px;
font-weight:bold;
color:#123b67;
line-height:1.6;
">

Stay healthy,<br>

AI Health Assistant

</div>


</td>

</tr>


<!-- FOOTER -->

<tr>

<td
align="center"
style="
padding:20px;
background:#123b67;
color:#ffffff;
font-size:13px;
letter-spacing:0.5px;
"
>

Smart. Simple. Healthier.

</td>

</tr>


</table>


</td>

</tr>

</table>


</body>

</html>
"""

            try:

                # ------------------------------------------------
                # LOGO
                # ------------------------------------------------

                logo_path = (
                    Path(settings.BASE_DIR)
                    / "static"
                    / "images"
                    / "ai.png"
                )


                # ------------------------------------------------
                # CREATE EMAIL
                # ------------------------------------------------

                email = InlineLogoEmail(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                    html_content=html_message,
                    logo_path=logo_path
                )


                # ------------------------------------------------
                # SEND EMAIL
                # ------------------------------------------------

                connection = get_connection()

                connection.send_messages(
                    [email]
                )


                # ------------------------------------------------
                # SAVE LAST SENT
                # ------------------------------------------------

                medicine.last_reminder_sent = timezone.now()

                medicine.save(
                    update_fields=[
                        "last_reminder_sent"
                    ]
                )


                sent_count += 1


                self.stdout.write(
                    self.style.SUCCESS(
                        f"Reminder sent: "
                        f"{medicine.medicine_name} "
                        f"→ {user.email}"
                    )
                )


            except Exception as error:

                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to send reminder for "
                        f"{medicine.medicine_name}: "
                        f"{error}"
                    )
                )


        self.stdout.write(
            self.style.SUCCESS(
                f"Medicine reminder check completed. "
                f"Emails sent: {sent_count}"
            )
        )