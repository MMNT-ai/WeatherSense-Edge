import csv
from datetime import datetime
import os
import sys
import serial

SERIAL_PORT = "COM2"
BAUD_RATE = 9600
CSV_FILENAME = "sensor_dataset.csv"

try:
  ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
  print(f"[+] Connected to {SERIAL_PORT} successfully.")
except Exception as e:
  print(f"[-] Error opening {SERIAL_PORT}: {e}")
  print("[!] Make sure the virtual port pair is created and not busy.")
  sys.exit(1)

file_exists = os.path.isfile(CSV_FILENAME)

with open(CSV_FILENAME, mode="a", newline="") as file:
  writer = csv.writer(file)

  if not file_exists:
    header = ["Timestamp", "Temperature_C", "Humidity_Pct", "Light_Intensity"]
    writer.writerow(header)
    file.flush()
    print("[CSV Header Written] -> " + ",".join(header))

  print(f"[+] Logging data into '{CSV_FILENAME}'...")
  print("[+] Press Ctrl + C to stop.\n")
  print("-" * 65)

  try:
    while True:
      raw_line = ser.readline().decode("utf-8", errors="ignore").strip()

      if raw_line:
        if "Error" in raw_line or "DHT" in raw_line:
          print(f"[*] Sensor Status: {raw_line}")
          continue

        parts = raw_line.split(",")

        if len(parts) == 3:
          temperature, humidity, light = parts
          current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

          row = [current_time, temperature, humidity, light]

          writer.writerow(row)
          file.flush()

          csv_row_str = f"{current_time},{temperature},{humidity},{light}"
          print(f"[Written to CSV] -> {csv_row_str}")

  except KeyboardInterrupt:
    print("\n[!] Logging terminated by user.")
  finally:
    ser.close()
    print("[+] Serial port closed.")