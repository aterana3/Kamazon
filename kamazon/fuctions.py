import qrcode
from io import BytesIO
import base64
import geoip2.database
import os
from django.conf import settings

def get_city_from_ip(ip_address):
    print("exc")
    reader = None
    try:
        reader = geoip2.database.Reader(settings.GEOCITY_PATH)
        response = reader.city(ip_address)
        city = response.city.name
        return city if city else 'Unknown'
    except geoip2.errors.AddressNotFoundError:
        return 'Unknown'
    except Exception as e:
        print(f"Error getting city from IP: {e}")
        return 'Unknown'
    finally:
        print("finish")
        if reader:
            reader.close()

    
def generate_qrcode(data):
    qr_code_stream = BytesIO()

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    img.save(qr_code_stream, format="PNG")
    return base64.b64encode(qr_code_stream.getvalue()).decode('utf-8')