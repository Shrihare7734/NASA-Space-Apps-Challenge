import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import requests
import io
import time

#API KEYS
WEATHER_API_KEY = "06c921750b9a82d8f5d1294e1586276f"
NASA_API_KEY = "DEMO_KEY"  

#Functions
def get_location():
    try:
        ip_data = requests.get("https://ipinfo.io/").json()
        return ip_data['city']
    except:
        return None

def fetch_weather(city):
    try:
        api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
        data = requests.get(api).json()
        if data.get("cod") != 200:
            messagebox.showerror("Error", f"City '{city}' not found!")
            return None
        return data
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch weather.\n{e}")
        return None

def fetch_forecast(city):
    try:
        api = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}"
        data = requests.get(api).json()
        if data.get("cod") != "200":
            return None
        return data
    except:
        return None

def fetch_nasa_apod():
    try:
        api = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
        data = requests.get(api).json()
        return data
    except:
        return None

def kelvin_to_celsius(k):
    return int(k - 273.15)

def update_weather(event=None):
    city = textField.get() or get_location()
    if not city:
        messagebox.showerror("Error", "Could not detect location. Please enter a city.")
        return

    #Current Weather 
    weather = fetch_weather(city)
    if not weather:
        return

    condition = weather['weather'][0]['main']
    temp = kelvin_to_celsius(weather['main']['temp'])
    min_temp = kelvin_to_celsius(weather['main']['temp_min'])
    max_temp = kelvin_to_celsius(weather['main']['temp_max'])
    pressure = weather['main']['pressure']
    humidity = weather['main']['humidity']
    wind = weather['wind']['speed']
    sunrise = time.strftime('%I:%M %p', time.gmtime(weather['sys']['sunrise'] - 21600))
    sunset = time.strftime('%I:%M %p', time.gmtime(weather['sys']['sunset'] - 21600))

    label1.config(text=f"{city} | {condition} | {temp}°C")
    label2.config(text=(
        f"Min: {min_temp}°C | Max: {max_temp}°C\n"
        f"Pressure: {pressure} hPa | Humidity: {humidity}%\n"
        f"Wind: {wind} m/s\nSunrise: {sunrise} | Sunset: {sunset}"
    ))

    #3-Day Forecast 
    forecast = fetch_forecast(city)
    if forecast:
        for i in range(3):
            day_data = forecast['list'][i*8]  
            date_txt = day_data['dt_txt'].split()[0]
            temp_min = kelvin_to_celsius(day_data['main']['temp_min'])
            temp_max = kelvin_to_celsius(day_data['main']['temp_max'])
            condition_day = day_data['weather'][0]['main']
            icon_code = day_data['weather'][0]['icon']

            # Fetch icon
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
            icon_bytes = requests.get(icon_url).content
            icon_image = Image.open(io.BytesIO(icon_bytes)).resize((50,50))
            icon_photo = ImageTk.PhotoImage(icon_image)
            forecast_icons[i].config(image=icon_photo)
            forecast_icons[i].image = icon_photo

            forecast_labels[i].config(text=f"{date_txt}\n{condition_day}\n{temp_min}°C/{temp_max}°C")

    #NASA APOD
    nasa_data = fetch_nasa_apod()
    if nasa_data and 'url' in nasa_data:
        try:
            image_bytes = requests.get(nasa_data['url']).content
            image = Image.open(io.BytesIO(image_bytes)).resize((300,200))
            photo = ImageTk.PhotoImage(image)
            nasa_label.config(image=photo)
            nasa_label.image = photo
            nasa_title.config(text=f"NASA APOD: {nasa_data.get('title','')}")
        except:
            nasa_label.config(image='')
            nasa_title.config(text='')

# GUI
canvas = tk.Tk()
canvas.geometry("750x800")
canvas.title("NASA Space Weather App")

f_small = ("poppins", 14, "bold")
f_large = ("poppins", 28, "bold")

textField = tk.Entry(canvas, justify='center', font=f_large)
textField.pack(pady=20)
textField.focus()
textField.bind('<Return>', update_weather)

label1 = tk.Label(canvas, font=f_large)
label1.pack(pady=10)
label2 = tk.Label(canvas, font=f_small, justify="left")
label2.pack(pady=10)

#Forecast GUI
forecast_frame = tk.Frame(canvas)
forecast_frame.pack(pady=10)
forecast_icons = []
forecast_labels = []
for i in range(3):
    day_frame = tk.Frame(forecast_frame)
    day_frame.pack(side='left', padx=10)
    icon_label = tk.Label(day_frame)
    icon_label.pack()
    text_label = tk.Label(day_frame, font=f_small)
    text_label.pack()
    forecast_icons.append(icon_label)
    forecast_labels.append(text_label)

#NASA APOD
nasa_title = tk.Label(canvas, font=f_small, wraplength=700)
nasa_title.pack(pady=5)
nasa_label = tk.Label(canvas)
nasa_label.pack(pady=5)

#Initialize
update_weather()

canvas.mainloop()

