"""
API Services
Includes business logic such as LLM, web crawling, and email.
"""

import openai
import requests
from flask import current_app
from bs4 import BeautifulSoup
from .utils import error_response
import re

# ==========================================
# LLM Services
# ==========================================
class LLMService:
    """Handles all LLM-related functionalities"""

    @staticmethod
    def smart_fill(type, input_data):
        """
        SmartFill function
        Uses LLM to auto-generate descriptions for resume sections (e.g., work_experience, education)
        
        Args:
            type (str): Section type ("work_experience" or "education")
            input_data (dict): Input fields (e.g., job_title, skills)
        
        Returns:
            dict: { "generated_description": str }
        """
        try:
            prompt = (
                f"Generate a concise, achievement-focused {type} description "
                f"based on the following input:\n\n{input_data}\n\n"
                "Output one professional sentence suitable for a resume."
            )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )

            description = response["choices"][0]["message"]["content"].strip()
            return {"generated_description": description}

        except Exception as e:
            current_app.logger.error(f"Error in smart_fill: {str(e)}")
            return error_response("Failed to generate description", 500)

    @staticmethod
    def generate_cover_letter(user_data, job_data, resume_data):
        """
        Generate a cover letter draft using LLM
        
        Args:
            user_data (dict): User information (name, contact, etc.)
            job_data (dict): Job posting information (title, company, requirements)
            resume_data (dict): User’s resume content
        
        Returns:
            dict: { "cover_letter_draft": str }
        """
        try:
            prompt = (
                f"Write a professional cover letter draft based on the following data:\n\n"
                f"User Info:\n{user_data}\n\n"
                f"Job Posting:\n{job_data}\n\n"
                f"Resume Summary:\n{resume_data}\n\n"
                "The tone should be formal but engaging, suitable for applying to a top company."
            )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.75,
            )

            cover_letter = response["choices"][0]["message"]["content"].strip()
            return {"cover_letter_draft": cover_letter}

        except Exception as e:
            current_app.logger.error(f"Error generating cover letter: {str(e)}")
            return error_response("Failed to generate cover letter", 500)

# ==========================================
# Scraper Services
# ==========================================
class ScraperService:
    """Handles web scraping and keyword extraction"""

    @staticmethod
    def extract_keywords(url=None, text=None):
        """
        Extract job-related keywords using simple NLP
        
        Args:
            url (str, optional): URL of job posting
            text (str, optional): Raw job description text
        
        Returns:
            dict: { "keywords": [str] }
        """
        try:
            if url and not text:
                resp = requests.get(url, timeout=10)
                soup = BeautifulSoup(resp.text, "html.parser")
                text = soup.get_text(separator=" ")

            if not text:
                return error_response("No content provided for keyword extraction", 400)

            # Basic keyword extraction
            words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
            keywords = list(set(w for w in words if len(w) > 2))[:20]

            return {"keywords": keywords}

        except Exception as e:
            current_app.logger.error(f"Error extracting keywords: {str(e)}")
            return error_response("Failed to extract keywords", 500)

    @staticmethod
    def scrape_job_posting(url):
        """
        Scrape job posting details from a given URL
        
        Args:
            url (str): Job posting URL
        
        Returns:
            dict: { "title": str, "company": str, "description": str, "location": str }
        """
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, "html.parser")

            title = soup.find("h1") or soup.find("title")
            company = soup.find(text=re.compile(r"Company|Employer", re.I))
            description = soup.get_text(separator=" ")

            return {
                "title": title.get_text(strip=True) if title else "Untitled",
                "company": company.strip() if company else "Unknown Company",
                "description": description[:1500],
            }

        except Exception as e:
            current_app.logger.error(f"Error scraping job posting: {str(e)}")
            return error_response("Failed to scrape job posting", 500)

# ==========================================
# Email Services
# ==========================================
class EmailService:
    """Handles email sending"""

    @staticmethod
    def send_verification_email(email, token):
        """
        Send verification email with a verification link
        
        Args:
            email (str): Recipient email address
            token (str): Verification token
        """
        try:
            verification_link = f"{current_app.config['FRONTEND_URL']}/verify?token={token}"

            subject = "Verify your account"
            body = (
                f"Hello,\n\nPlease verify your account by clicking the link below:\n"
                f"{verification_link}\n\nThank you!"
            )

            # Example using SendGrid (can swap with SMTP)
            api_key = current_app.config.get("SENDGRID_API_KEY")
            if not api_key:
                raise ValueError("Missing SENDGRID_API_KEY in config")

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": email}]}],
                    "from": {"email": "noreply@yourapp.com"},
                    "subject": subject,
                    "content": [{"type": "text/plain", "value": body}]
                }
            )

            if response.status_code >= 400:
                current_app.logger.error(f"Email send failed: {response.text}")
                return error_response("Failed to send verification email", 500)

            return {"message": "Verification email sent successfully."}

        except Exception as e:
            current_app.logger.error(f"Error sending verification email: {str(e)}")
            return error_response("Failed to send verification email", 500)
