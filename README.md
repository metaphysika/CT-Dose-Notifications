# CT Dose Notification System
## Overview

This script is designed to monitor CT dose metrics and send automated notifications when doses exceed predefined thresholds. It utilizes data from radiological exams, specifically CT scans, extracted from an OpenREM database. The script identifies cases that surpass dose limits and emails the relevant staff. It also maintains a record of all notifications for review and quality assurance purposes.
## Features

    - Automated scanning of CT dose metrics from a database.
    - Customizable dose limits for different types of CT exams.
    - Email notifications sent to specified recipients when doses exceed set limits.
    - Archiving of notification events for future analysis and reporting.
    - Integration with Django framework for database operations.
    - Use of OpenREM for dose data extraction and management.

## Prerequisites

    - Python 3.x installation.
    - OpenREM installed and configured in the specified Python environment.
    - Relevant Python packages: django, pandas, datetime, openpyxl, py.
    - The emailsender module available in the script's directory or Python path.
    - A configured SMTP server to handle outgoing emails.

## Installation

Ensure all required Python libraries are installed. Use pip to install any missing packages:

pip install django pandas datetime openpyxl py

## Configuration


    - is_email: Set to True to enable sending emails, False to disable.
    - projectpath: The path to your OpenREM installation.
    - Dose limit functions at the bottom of the script (dose_limit([...], limit)): Configure these with the relevant exam types and dose limits.
    - emailname: Update with the actual email address where notifications will be sent.


## Running the Script

To run the script, execute it in your Python environment. The script will automatically connect to the OpenREM database, extract the necessary dose data, check against the set limits, and send out email notifications as configured.
How It Works


    - The script initializes the Django environment to access the OpenREM database.
    - It then queries the CtIrradiationEventData model for recent CT dose data.
    - Using predefined dose limits, it identifies exams where the dose exceeds the threshold.
    - For each instance, it records the notification details and sends an email to the configured address if is_email is set to True.
    - The notifications are also saved in an Excel workbook for archival purposes.


## Output


    - Email notifications sent to specified recipients with details of the dose event.
    - A record of notifications saved in an Excel file located at the script's specified path.


## Notes

    - Ensure that the OpenREM database connection details are correct and that the script has access to the database.
    - The SMTP server details need to be configured in the emailsender module for email functionality.
    - The script should be run with appropriate permissions to access the file system for reading and writing Excel files.

## Disclaimer

This script is provided "as is" without any warranty. It is intended to be used by qualified professionals who can ensure that the script's use is appropriate within their radiology and IT environment. Always test the script in a non-production setting before use.
