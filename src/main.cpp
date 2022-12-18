#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <Bounce2.h>
#include <platform.h>

//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
Adafruit_NeoPixel led = Adafruit_NeoPixel(1, NEO_DATA, NEO_GRB | NEO_KHZ800);
Bounce motion = Bounce();

const char reports[] = {'1', '0'};
unsigned long lastReport;
uint8_t tmp;

void setLED(uint8_t r, uint8_t g, uint8_t b){
  led.setPixelColor(0, led.Color(r, g, b));
  led.show();
}

void setup() {
  // Power up the neoPixel
  pinMode(NEO_PWR, 1);
  digitalWrite(NEO_PWR, 1);
  led.setBrightness(4);
  led.clear();

  // Prep the serial interface
  Serial.begin(57600);

  // Prep the input IO pin
  pinMode(MOTION_GPIO_PIN, INPUT_PULLUP);
  motion.interval(5);
  motion.attach(MOTION_GPIO_PIN);

  // Set time of last report
  lastReport = millis();
}

void loop() {
  motion.update();
  if(motion.changed() || (millis() - lastReport > REPORT_TIME_MSEC)) {
    tmp = motion.read();
    Serial.print(reports[tmp]);
    if(tmp)
      setLED(0,255,0);
    else
      setLED(255,0,0);
    lastReport = millis();
  }
}