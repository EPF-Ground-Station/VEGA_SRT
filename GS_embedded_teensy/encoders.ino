// todo rename pins
// todo add parameter for other encoder support


// todo draft:
// 16 first bits are for multi-turn counter
// 20 first bits are for angular position

void encoder_read() {

  // select the azimut encoder
  AzNCSoff;
  delayMicroseconds(10);

  // retrieve data from encoder
  uint32_t first_word = SPI.transfer16(ZERO);
  uint32_t second_word = SPI.transfer16(ZERO);
  uint32_t third_word = SPI.transfer16(ZERO);
  // unselect the azimut encoder
  AzNCSon;

  uint32_t pos_dec = (second_word << 4) + (third_word >> 12);
  float pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

  HWSerial.print("pos_deg: ");
  HWSerial.println(pos_deg);
}
