
# Database Config
import pymysql # type: ignore

def get_db_connection():
    return pymysql.connect(
        host="YOUR_CLOUD_HOST_HERE",
        user="YOUR_USERNAME_HERE",
        password="YOUR_PASSWORD_HERE", 
        database="YOUR_DB_NAME",
        port=3306
    )

# Email Config
EMAIL_CONFIG = {
    "sender_email": "preetkaurgill437@gmail.com", 
    "sender_password": "qcxu iskg vcja haqr" 
}