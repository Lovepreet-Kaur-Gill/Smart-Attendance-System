
# Database Config
import pymysql # type: ignore

def get_db_connection():
    return pymysql.connect(
        host="bwmuy19rmyneoudpdoiz-mysql.services.clever-cloud.com",
        user= "uuzigjqx0sdqftxw",
        password= "D4wntDqB8Q7eSBggYRon",
        database="bwmuy19rmyneoudpdoiz",
        port=3306
    )

# Email Config
EMAIL_CONFIG = {
    "sender_email": "preetkaurgill437@gmail.com", 
    "sender_password": "qcxu iskg vcja haqr" 
}