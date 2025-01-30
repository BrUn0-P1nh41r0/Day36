import requests
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


today = datetime.today()
yesterday = today - timedelta(days=1)
day_before_yesterday = today - timedelta(days=2)
yesterday_day = yesterday.strftime("%Y-%m-%d")
day_before_day = day_before_yesterday.strftime("%Y-%m-%d")

parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "outputsize": "compact",
    "apikey": STOCK_API_KEY,
}

parameters_news = {
    "q":"tesla",
    "from":yesterday_day,
    "to":yesterday_day,
    "language":"en",
    "sortBy":"publishedAt",
    "apiKey":NEWS_API_KEY,
}

def get_stock():
    stock = requests.get(url=STOCK_ENDPOINT, params=parameters)
    data = stock.json()
    print(data)
    day1 = float(data["Time Series (Daily)"][yesterday_day]["4. close"])
    day2 = float(data["Time Series (Daily)"][day_before_day]["4. close"])

    price_dif = abs(day1 - day2)
    percentage_change = (price_dif / day1) * 100
    significant_change = percentage_change >= 5

    return significant_change, percentage_change,price_dif

news_to_print = []
def return_articles():
    news = requests.get(url=NEWS_ENDPOINT, params=parameters_news)
    data_news = news.json()
    for i in range(3):
        news_to_print.append(data_news["articles"][i])

        # Convert to readable text
    formatted_text = format_news(news_to_print)
    return formatted_text

def format_news(articles):
    formatted_news = ""
    for index, article in enumerate(articles, start=1):
        title = article.get("title", "No title")
        description = article.get("description", "No description available.")
        url = article.get("url", "#")
        formatted_news += f"""📌{index}. {title} 
- Brief:{description}
- Read more: [🔗 {url}]

"""
    return formatted_news

stock_validation, percentage, raw_price = get_stock()
articles_to_send = return_articles()

if stock_validation:
    if raw_price > 0:
        email_body = f"""{STOCK}: 🔺{percentage:.2f}%
{articles_to_send}
"""
        message_to_send = MIMEText(email_body, "plain", "utf-8")
    else:
        email_body = f"""{STOCK}: 🔻{percentage:.2f}%
{articles_to_send}
"""
        message_to_send = MIMEText(email_body, "plain", "utf-8")
else:
    email_body = "Not a significant update!"
    message_to_send = MIMEText(email_body, "plain", "utf-8")

msg = MIMEMultipart()
msg['From'] = MY_EMAIL
msg['To'] = "bpinheiro44@yahoo.com"
msg['Subject'] = "Stock Price Update!"

# Attach the plain text message with UTF-8 encoding
msg.attach(message_to_send)

with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
    connection.sendmail(from_addr=MY_EMAIL,
                        to_addrs="bpinheiro44@yahoo.com",
                        msg=msg.as_string())
