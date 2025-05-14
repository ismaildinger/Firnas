#define STEP_PIN 7
#define DIR_PIN 8

void setup() {
  Serial.begin(9600);
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  Serial.println("🚀 Arduino başlatıldı. Kamera komutu bekleniyor...");
}

void step_motor(bool direction, int steps = 10) {
  Serial.print("↪️ Yön: ");
  Serial.println(direction == HIGH ? "Sağ" : "Sol");

  digitalWrite(DIR_PIN, direction);
  int delay_us = 1000;

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delay_us);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(delay_us);

    // hızlanma (isteğe bağlı)
    if (delay_us > 400) delay_us -= 10;
  }

  Serial.println("✅ Adımlar tamamlandı.");
}

void loop() {
  if (Serial.available()) {
    String komut = Serial.readStringUntil('\n');
    komut.trim();

    if (komut == "LEFT") {
      step_motor(LOW);
    } else if (komut == "RIGHT") {
      step_motor(HIGH);
    } else if (komut == "STOP") {
      Serial.println("⏸ Durduruldu.");
    } else {
      Serial.println("⚠️ Bilinmeyen komut.");
    }
  }
}
