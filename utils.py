
# 📁 utils.py
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

CATEGORY_KEYWORDS = {
    "Recharge": ["recharge", "top-up", "prepaid"],
    "Shopping": ["amazon", "flipkart", "myntra", "snapdeal", "shopping"],
    "Bills": ["bill", "electricity", "water", "gas", "broadband", "postpaid"],
    "Food": ["swiggy", "zomato", "domino", "pizza", "restaurant", "eatery"],
    "UPI Transfer": ["vpa", "upi", "gpay", "to", "from", "paytm"],
    "Loan/EMI": ["axio", "emi", "loan", "cashe", "finzoomers"],
}

IGNORED_KEYWORDS = [
    "payment reminder", "scheduled downtime", "upi service alert", "loan offer",
    "bill due", "insurance reminder", "credit card offer", "reward points",
    "monthly statement", "otp", "refund processed", "Order successfully placed", "Avoid Late Payment Fees"
]

MERCHANT_PATTERNS = [
    r'(?:paid to|sent to|credited from|debited at|purchase at|spent at|payment to|received from)\s+([A-Za-z0-9&\s]{3,})',
    r'at\s+([A-Za-z0-9&\s]{3,})',
    r'to\s+([A-Za-z0-9&\s]{3,})',
    r'via\s+([A-Za-z0-9&\s]{3,})',
]

AMOUNT_PATTERNS = [
    r'Rs\.?\s?[\d,]+\.\d{2}',
    r'INR\s?[\d,]+\.\d{2}',
    r'₹\s?[\d,]+\.\d{2}',
    r'Amount\s?[\d,]+\.\d{2}',
    r'Amount\s?[\d,]+'
]
