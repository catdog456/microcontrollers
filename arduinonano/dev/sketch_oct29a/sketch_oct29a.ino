
#include <SPI.h>
#define CE  9
 
#define CHANNELS  64
int channel[CHANNELS];
 
int  line;
char grey[] = " .:-=+*aRW";
 
// nRF24L01P registers we need
#define _NRF24_CONFIG      0x00
#define _NRF24_EN_AA       0x01
#define _NRF24_RF_CH       0x05
#define _NRF24_RF_SETUP    0x06
#define _NRF24_RPD         0x09
 
byte getRegister(byte r)
{
 byte c;
 
 PORTB &=~_BV(2);
 c = SPI.transfer(r&0x1F);
 c = SPI.transfer(0);  
 PORTB |= _BV(2);
 
 return(c);
}
 
void setRegister(byte r, byte v)
{
 PORTB &=~_BV(2);
 SPI.transfer((r&0x1F)|0x20);
 SPI.transfer(v);
 PORTB |= _BV(2);
}
 
void powerUp(void)
{
 setRegister(_NRF24_CONFIG,getRegister(_NRF24_CONFIG)|0x02);
 delayMicroseconds(130);
}
 
void powerDown(void)
{
 setRegister(_NRF24_CONFIG,getRegister(_NRF24_CONFIG)&~0x02);
}
 
void enable(void)
{
   PORTB |= _BV(1);
}
 
void disable(void)
{
   PORTB &=~_BV(1);
}
 
void setRX(void)
{
 setRegister(_NRF24_CONFIG,getRegister(_NRF24_CONFIG)|0x01);
 enable();
 // this is slightly shorter than
 // the recommended delay of 130 usec
 // - but it works for me and speeds things up a little...
 delayMicroseconds(100);
}
 
void scanChannels(void)
{
 disable();
 for( int j=0 ; j<200  ; j++)
 {
   for( int i=0 ; i<CHANNELS ; i++)
   {
     setRegister(_NRF24_RF_CH,(128*i)/CHANNELS);
     
     setRX();
     
     delayMicroseconds(40);
     
     disable();
 
     if( getRegister(_NRF24_RPD)>0 )   channel[i]++;
   }
 }
}
 
void outputChannels(void)
{
 int norm = 0;
 
 for( int i=0 ; i<CHANNELS ; i++)
   if( channel[i]>norm ) norm = channel[i];
   
 Serial.print('|');
 for( int i=0 ; i<CHANNELS ; i++)
 {
   int pos;
   
   if( norm!=0 ) pos = (channel[i]*10)/norm;
   else          pos = 0;
   
   if( pos==0 && channel[i]>0 ) pos++;
   
   if( pos>9 ) pos = 9;
 
   Serial.print(grey[pos]);
   channel[i] = 0;
 }
 
 Serial.print("| ");
 Serial.println(norm);
}
 
void printChannels(void)
{
 Serial.println(">      1 2  3 4  5  6 7 8  9 10 11 12 13  14                     <");
}
 
void setup()
{
 Serial.begin(57600);
 
 Serial.println("Starting 2.4GHz Scanner ...");
 Serial.println();
 
 Serial.println("Channel Layout");
 printChannels();
 
 // Setup SPI
 SPI.begin();
 SPI.setDataMode(SPI_MODE0);
 SPI.setClockDivider(SPI_CLOCK_DIV2);
 SPI.setBitOrder(MSBFIRST);
 
 // Activate Chip Enable
 pinMode(CE,OUTPUT);
 disable();
 
 powerUp();
 
 setRegister(_NRF24_EN_AA,0x0);
 
 setRegister(_NRF24_RF_SETUP,0x0F);
 
 line = 0;
}
 
void loop()
{
 scanChannels();
 
 outputChannels();
 
 if( line++>12 )
 {
   printChannels();
   line = 0;
 }
}
