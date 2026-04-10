from groq import Groq
import os


def generate_customer_email(data, decision, reasons):
    try:
        # ✅ Create client INSIDE function
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are a bank manager.

Write a professional email to a customer regarding suspicious activity.

Details:
- Decision: {decision}
- Reasons: {reasons}
- Transaction Data: {data}

The email should:
- Be polite and professional
- Inform about suspicious activity
- Suggest next steps
- NOT mention AI

Return ONLY the email text.
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("CUSTOMER EMAIL GEN ERROR:", str(e))

        return "Dear Customer, we detected unusual activity. Please contact the bank."