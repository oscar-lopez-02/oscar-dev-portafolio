from machine import Pin, I2C
from machine import PWM
import ssd1306
import framebuf
import time
import lcd_api  # Library for LCD API
import pico_i2c_lcd # Library for I2C LCD control on Pico

# I2C setup for OLED display (I2C1, SDA on GP18, SCL on GP19, 400kHz frequency)
sda = Pin(18)
scl = Pin(19)

i2c = I2C(1, sda=Pin(18), scl=Pin(19), freq=400000)
oled_display = ssd1306.SSD1306_I2C(128, 64, i2c, 0x3C)

# I2C setup for LCD display (I2C0, SDA on GP4, SCL on GP1, 400kHz frequency)
I2C_ADDR = 0x27  # I2C address of the LCD
I2C_NUM_ROWS = 2  # Number of rows on the LCD
I2C_NUM_COLS = 16 # Number of columns on the LCD

i2c = I2C(0, sda=Pin(4), scl=Pin(1), freq=400000)
lcd_display = pico_i2c_lcd.I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)


class Servo():
    # Define constants for the Servo class
    MAX_DUTY_CYCLE = 2**16 - 1  # Maximum duty cycle value (65535) used for scaling
    SLEEP_PERIOD_IN_SECONDS = 2  # Default sleep period for observing servo movement
    MILLISECONDS_PER_SECOND = 1000  # Conversion factor for milliseconds
    SERVO_PERIOD_IN_MILLISECONDS = 20  # Servo signal period (20 ms)
    SERVO_FREQUENCY = int(MILLISECONDS_PER_SECOND / SERVO_PERIOD_IN_MILLISECONDS)  # Servo PWM frequency (50 Hz)
    
    # Duty cycle values corresponding to specific servo positions
    SERVO_RIGHT_TURN_DUTY = 0.5  #Set duty to 0.5 milliseconds
    SERVO_GO_STRAIGHT_DUTY = 1.5 #Set duty to 1.5 milliseconds
    SERVO_LEFT_TURN_DUTY = 2.4   #Set duty to 2.4 milliseconds
    SERVO_NORTH_EAST_DUTY = 1.0  #Set duty to 1.0 milliseconds
    SERVO_NORTH_WEST_DUTY = 2.0  #Set duty to 1.0 milliseconds

    def __init__(self, pin, display, frequency=50):
        # Initialize the PWM pin and set frequency
        self.pwm_pin = PWM(pin)
        self.pwm_pin.freq(frequency)
        self.duty_cycle = 0  # Initialize duty cycle value
        self.oled_display = oled_display  # Store the display instance
        self.lcd_display = lcd_display  # Store LCD instance

    def set_position_by_duty_cycle(self, duty_cycle_period):
        # Calculate duty cycle percentage and scale it to the maximum value
        self.duty_cycle_period = duty_cycle_period

        self.duty_cycle_percentage = (duty_cycle_period / Servo.SERVO_PERIOD_IN_MILLISECONDS) * 100
        self.duty_cycle = Servo.MAX_DUTY_CYCLE * (self.duty_cycle_percentage / 100)
        self.pwm_pin.duty_u16(int(self.duty_cycle))  # Send scaled duty cycle to the PWM pin
    
    def set_position_by_angle(self, angle, description=""):
        """Convert angle to duty cycle and move the servo."""
        min_duty = Servo.SERVO_RIGHT_TURN_DUTY
        max_duty = Servo.SERVO_LEFT_TURN_DUTY
        duty_cycle_period = min_duty + (angle / 180.0) * (max_duty - min_duty)
        self.set_position_by_duty_cycle(duty_cycle_period)
        # Updates OLED display
        self.display_text("Servo set to:", f"Angle: {angle} deg", description)


    def display_text(self, line1="", line2="", line3=""):
        """ Displays the lines on the OLED display."""
        self.oled_display.fill(0)  # Clear the screen
        self.oled_display.text(line1, 0, 0)   # Line 1 (Y=0)
        self.oled_display.text(line2, 0, 16)  # Line 2 (Y=16)
        self.oled_display.text(line3, 0, 32)  # Line 3 (Y=32)
        self.oled_display.show()  # Update display
        """ Displays 2 lines on the LCD display"""
        self.lcd_display.clear()
        self.lcd_display.putstr(f"{line1}\n{line2}")


    def process_file(self, file_name):
        """Reads servo commands from a file and moves the servo accordingly."""
        with open(file_name, "r") as file:
            for line in file:
                data = line.strip().split(",")
                if len(data) != 2:
                    continue  # Skip invalid lines

                angle = int(data[0])  
                duration = int(data[1])  

                # Move servo and update OLED display
                self.set_position_by_angle(angle, f"Moving for {duration} sec")
                print(f"Servo set to {angle} degrees for {duration} seconds.")
                time.sleep(duration)  # Wait before reading next command
    

servo = Servo(Pin(0), oled_display, 50)  # Initialize Servo
servo.process_file("servo_commands.txt")  # Read file and execute movements
