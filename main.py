from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import time

# instancia de la aplicación FastAPI
app = FastAPI()

# Tiempo de cache en segundos (1 hora)
CACHE_TIME = 3600  # 1 hora
last_fetched = 0
rates_cache = {}

# Configuración CORS
origins = [
    "http://localhost:5500",  # El origen que usas para el frontend
    "http://127.0.0.1:5500",  # Si usas ambos, puedes incluir 127.0.0.1 también
]

# Agregar el middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
# URL del endpoint que devuelve los nombres de las monedas

currency_name = {
    "AED": "UAE Dirham",
    "AFN": "Afghan Afghani",
    "ALL": "Albanian Lek",
    "AMD": "Armenian Dram",
    "ANG": "Netherlands Antillian Guilder",
    "AOA": "Angolan Kwanza",
    "ARS": "Argentine Peso",
    "AUD": "Australian Dollar",
    "AWG": "Aruban Florin",
    "AZN": "Azerbaijani Manat",
    "BAM": "Bosnia and Herzegovina Convertible Mark",
    "BBD": "Barbados Dollar",
    "BDT": "Bangladeshi Taka",
    "BGN": "Bulgarian Lev",
    "BHD": "Bahraini Dinar",
    "BIF": "Burundian Franc",
    "BMD": "Bermudian Dollar",
    "BND": "Brunei Dollar",
    "BOB": "Bolivian Boliviano",
    "BRL": "Brazilian Real",
    "BSD": "Bahamian Dollar",
    "BTN": "Bhutanese Ngultrum",
    "BWP": "Botswana Pula",
    "BYN": "Belarusian Ruble",
    "BZD": "Belize Dollar",
    "CAD": "Canadian Dollar",
    "CDF": "Congolese Franc",
    "CHF": "Swiss Franc",
    "CLP": "Chilean Peso",
    "CNY": "Chinese Renminbi",
    "COP": "Colombian Peso",
    "CRC": "Costa Rican Colon",
    "CUP": "Cuban Peso",
    "CVE": "Cape Verdean Escudo",
    "CZK": "Czech Koruna",
    "DJF": "Djiboutian Franc",
    "DKK": "Danish Krone",
    "DOP": "Dominican Peso",
    "DZD": "Algerian Dinar",
    "EGP": "Egyptian Pound",
    "ERN": "Eritrean Nakfa",
    "ETB": "Ethiopian Birr",
    "EUR": "Euro",
    "FJD": "Fiji Dollar",
    "FKP": "Falkland Islands Pound",
    "FOK": "Faroese Króna",
    "GBP": "Pound Sterling",
    "GEL": "Georgian Lari",
    "GGP": "Guernsey Pound",
    "GHS": "Ghanaian Cedi",
    "GIP": "Gibraltar Pound",
    "GMD": "Gambian Dalasi",
    "GNF": "Guinean Franc",
    "GTQ": "Guatemalan Quetzal",
    "GYD": "Guyanese Dollar",
    "HKD": "Hong Kong Dollar",
    "HNL": "Honduran Lempira",
    "HRK": "Croatian Kuna",
    "HTG": "Haitian Gourde",
    "HUF": "Hungarian Forint",
    "IDR": "Indonesian Rupiah",
    "ILS": "Israeli New Shekel",
    "IMP": "Manx Pound",
    "INR": "Indian Rupee",
    "IQD": "Iraqi Dinar",
    "IRR": "Iranian Rial",
    "ISK": "Icelandic Króna",
    "JEP": "Jersey Pound",
    "JMD": "Jamaican Dollar",
    "JOD": "Jordanian Dinar",
    "JPY": "Japanese Yen",
    "KES": "Kenyan Shilling",
    "KGS": "Kyrgyzstani Som",
    "KHR": "Cambodian Riel",
    "KID": "Kiribati Dollar",
    "KMF": "Comorian Franc",
    "KRW": "South Korean Won",
    "KWD": "Kuwaiti Dinar",
    "KYD": "Cayman Islands Dollar",
    "KZT": "Kazakhstani Tenge",
    "LAK": "Lao Kip",
    "LBP": "Lebanese Pound",
    "LKR": "Sri Lanka Rupee",
    "LRD": "Liberian Dollar",
    "LSL": "Lesotho Loti",
    "LYD": "Libyan Dinar",
    "MAD": "Moroccan Dirham",
    "MDL": "Moldovan Leu",
    "MGA": "Malagasy Ariary",
    "MKD": "Macedonian Denar",
    "MMK": "Burmese Kyat",
    "MNT": "Mongolian Tögrög",
    "MOP": "Macanese Pataca",
    "MRU": "Mauritanian Ouguiya",
    "MUR": "Mauritian Rupee",
    "MVR": "Maldivian Rufiyaa",
    "MWK": "Malawian Kwacha",
    "MXN": "Mexican Peso",
    "MYR": "Malaysian Ringgit",
    "MZN": "Mozambican Metical",
    "NAD": "Namibian Dollar",
    "NGN": "Nigerian Naira",
    "NIO": "Nicaraguan Córdoba",
    "NOK": "Norwegian Krone",
    "NPR": "Nepalese Rupee",
    "NZD": "New Zealand Dollar",
    "OMR": "Omani Rial",
    "PAB": "Panamanian Balboa",
    "PEN": "Peruvian Sol",
    "PGK": "Papua New Guinean Kina",
    "PHP": "Philippine Peso",
    "PKR": "Pakistani Rupee",
    "PLN": "Polish Złoty",
    "PYG": "Paraguayan Guaraní",
    "QAR": "Qatari Riyal",
    "RON": "Romanian Leu",
    "RSD": "Serbian Dinar",
    "RUB": "Russian Ruble",
    "RWF": "Rwandan Franc",
    "SAR": "Saudi Riyal",
    "SBD": "Solomon Islands Dollar",
    "SCR": "Seychellois Rupee",
    "SDG": "Sudanese Pound",
    "SEK": "Swedish Krona",
    "SGD": "Singapore Dollar",
    "SHP": "Saint Helena Pound",
    "SLE": "Sierra Leonean Leone",
    "SLL": "Sierra Leonean Leone",
    "SOS": "Somali Shilling",
    "SRD": "Surinamese Dollar",
    "SSP": "South Sudanese Pound",
    "STN": "São Tomé and Príncipe Dobra",
    "SYP": "Syrian Pound",
    "SZL": "Eswatini Lilangeni",
    "THB": "Thai Baht",
    "TJS": "Tajikistani Somoni",
    "TMT": "Turkmenistan Manat",
    "TND": "Tunisian Dinar",
    "TOP": "Tongan Paʻanga",
    "TRY": "Turkish Lira",
    "TTD": "Trinidad and Tobago Dollar",
    "TVD": "Tuvaluan Dollar",
    "TWD": "New Taiwan Dollar",
    "TZS": "Tanzanian Shilling",
    "UAH": "Ukrainian Hryvnia",
    "UGX": "Ugandan Shilling",
    "USD": "United States Dollar",
    "UYU": "Uruguayan Peso",
    "UZS": "Uzbekistani So'm",
    "VES": "Venezuelan Bolívar Soberano",
    "VND": "Vietnamese Đồng",
    "VUV": "Vanuatu Vatu",
    "WST": "Samoan Tālā",
    "XAF": "Central African CFA Franc",
    "XCD": "East Caribbean Dollar",
    "XDR": "Special Drawing Rights",
    "XOF": "West African CFA franc",
    "XPF": "CFP Franc",
    "YER": "Yemeni Rial",
    "ZAR": "South African Rand",
    "ZMW": "Zambian Kwacha",
    "ZWL": "Zimbabwean Dollar"
}


class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

# Función para obtener las tasas de cambio de la API


async def fetch_rates():
    global last_fetched, rates_cache
    current_time = time.time()

    # Si el cache no ha expirado, devolver las tasas almacenadas
    if current_time - last_fetched < CACHE_TIME:
        return rates_cache

    # Si el cache ha expirado, obtener las tasas de la API
    async with httpx.AsyncClient() as client:
        response = await client.get(API_URL)

    if response.status_code != 200:
        raise HTTPException(
            status_code=500, detail="Error obteniendo las tasas de cambio")

    data = response.json()
    rates_cache = data["rates"]
    last_fetched = current_time
    return rates_cache


@app.post("/convert/", tags=['Currency'])
async def convert_currency(request: ConversionRequest):
    from_currency = request.from_currency
    to_currency = request.to_currency
    amount = request.amount

    # Obtener las tasas de cambio desde el caché
    rates = await fetch_rates()

    # Verificar si las monedas están disponibles
    if from_currency not in rates or to_currency not in rates:
        raise HTTPException(status_code=400, detail="Invalid currencies")

    # Realizar la conversión
    from_rate = rates[from_currency]
    to_rate = rates[to_currency]
    converted_amount = (amount / from_rate) * to_rate

    # Obtener el nombre de la moneda desde el diccionario de nombres
    from_currency_name = currency_name.get(from_currency, from_currency)
    to_currency_name = currency_name.get(to_currency, to_currency)

    return {
        "converted_amount": converted_amount,
        "rates": rates,  # Lista de todas las divisas
        "currency_names": currency_name,  # Devolver todas las monedas con sus nombres
        "selected_currency_names": {
            from_currency: from_currency_name,
            to_currency: to_currency_name
        }
    }
