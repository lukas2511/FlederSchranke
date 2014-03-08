#include <stdio.h>
#include <inttypes.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/io.h>
#include <util/delay.h>
#include <string.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>

//#define DUMMY
#define USE_TX_BUFFER
#define ENABLE_PULLUPS
#define MICROS_OVERFLOW 1800000000

#define BAUD 115200UL
#define UBRR_VAL ((F_CPU+BAUD*8)/(BAUD*16)-1);

#define BIT_AT(REG,FROM,TO) (((REG & ( 1 << FROM )) >> FROM) << TO)

uint8_t oldstate[9];
uint8_t curstate[9];

unsigned long microseconds = 0;

/* BITS STUFF */

#ifndef _UV
#define _UV(x) (1 << (x))
#endif

#ifndef _SETBIT
#define _SETBIT(x, y) ((x) |= _UV(y))
#endif

#ifndef _CLRBIT
#define _CLRBIT(x, y) ((x) &= ~_UV(y))
#endif

/* SERIAL STUFF */

void serial_init(void);
void s_putchr(unsigned char c);
void s_putstr(char *s);
void s_puti32(uint32_t x);
void se_start_frame(uint8_t n);

#ifdef USE_TX_BUFFER
#define UART_TX_BUFFER_SIZE 4096
#define UART_TX_BUFFER_MASK ( UART_TX_BUFFER_SIZE - 1 )
#if ( UART_TX_BUFFER_SIZE & UART_TX_BUFFER_MASK )
    #error TX buffer size is not a power of 2
#endif

static volatile unsigned char UART_TxBuf[UART_TX_BUFFER_SIZE];
static volatile uint16_t UART_TxHead;
static volatile uint16_t UART_TxTail;

ISR(USART0_UDRE_vect) {
    uint16_t tmptail;
    if (UART_TxHead!=UART_TxTail) {
        tmptail = ( UART_TxTail + 1 ) & UART_TX_BUFFER_MASK;
        UART_TxTail = tmptail;      /* Store new index */
        UDR0 = UART_TxBuf[tmptail];  /* Start transmition */
    } else {
        UCSR0B &= ~(1<<UDRIE0);
    }
}
#endif

void serial_init(void) {
    UCSR0B = _UV(TXEN0) | _UV(RXEN0) | _UV(RXCIE0); // tx/rx enabled, rx interrupt
    UCSR0C = _UV(UCSZ01) | _UV(UCSZ00); // 8 bit, no parity, 1 stop
    UBRR0 = UBRR_VAL;
    do{UDR0;}while (UCSR0A & (1 << RXC0));
    UCSR0A = (1 << TXC0) | (1 << RXC0);
}

#ifdef USE_TX_BUFFER
void s_putchr(unsigned char c) {
    uint16_t tmphead;
    tmphead = (UART_TxHead + 1) & UART_TX_BUFFER_MASK;
    while (tmphead==UART_TxTail) {;} // wait for free space in buffer 
    UART_TxBuf[tmphead] = c;
    UART_TxHead = tmphead;
    UCSR0B |= (1<<UDRIE0);
}
#else
void s_putchr(unsigned char c) {
    loop_until_bit_is_set(UCSR0A, UDRE0);
    UDR0 = c;
}
#endif

void s_putstr(char *s) {
    while (*s) {
        s_putchr(*s);
        s++;
    }
}

void s_puti32(uint32_t x) {
    s_putchr((x & 0x000000FF));
    s_putchr((x & 0x0000FF00) >>  8);
    s_putchr((x & 0x00FF0000) >> 16);
    s_putchr((x & 0xFF000000) >> 24);
}

/* TIMECOUNTING STUFF */

#define clockCyclesPerMicrosecond() ( F_CPU / 1000000L )
#define clockCyclesToMicroseconds(a) ( (a) / clockCyclesPerMicrosecond() )
#define microsecondsToClockCycles(a) ( (a) * clockCyclesPerMicrosecond() )

#define MICROSECONDS_PER_TIMER0_OVERFLOW (clockCyclesToMicroseconds(64 * 256))
#define MILLIS_INC (MICROSECONDS_PER_TIMER0_OVERFLOW / 1000)
#define FRACT_INC ((MICROSECONDS_PER_TIMER0_OVERFLOW % 1000) >> 3)
#define FRACT_MAX (1000 >> 3)

void micros_init();
unsigned long millis();
unsigned long micros();

volatile unsigned long timer0_overflow_count = 0;
volatile unsigned long timer0_millis = 0;
static unsigned char timer0_fract = 0;

void micros_init() {
    TCCR0A = _UV(WGM00) | _UV(WGM01);
    TCCR0B = _UV(CS00) | _UV(CS01);
    TIMSK0 = _UV(TOIE0);
    OCR0A = 254;
}

ISR(TIMER0_OVF_vect) {
    unsigned long m = timer0_millis;
    unsigned char f = timer0_fract;
    m += MILLIS_INC;
    f += FRACT_INC;
    if (f >= FRACT_MAX) {
        f -= FRACT_MAX;
        m += 1;
    }
    timer0_fract = f;
    timer0_millis = m;
    timer0_overflow_count++;
}

unsigned long millis() {
    unsigned long m;
    uint8_t oldSREG = SREG;

    cli();
    m = timer0_millis;
    SREG = oldSREG;

    return m;
}

unsigned long micros() {
    unsigned long m;
    uint8_t oldSREG = SREG, t;
    cli();
    m = timer0_overflow_count;
    t = TCNT0;
    if ((TIFR0 & _BV(TOV0)) && (t < 255))
        m++;
    SREG = oldSREG;
    return ((m << 8) + t) * (64 / clockCyclesPerMicrosecond());
}

/* MAIN STUFF */

void init_registers() {
    DDRA  &= 255;
    DDRB  &= 255;
    DDRC  &= 255;
    DDRD  &= 255 & ~(_UV(4) | _UV(5) | _UV(6));
    DDRE  &= 255 & ~(_UV(0) | _UV(1) | _UV(2) | _UV(6) | _UV(7));
    DDRF  &= 255;
    DDRG  &= 255 & ~(_UV(3) | _UV(4) | _UV(6) | _UV(7));
    DDRH  &= 255 & ~(_UV(2) | _UV(7));
    DDRJ  &= 255 & ~(_UV(2) | _UV(3) | _UV(4) | _UV(5) | _UV(6) | _UV(7));
    DDRK  &= 255;
    DDRL  &= 255;
#ifdef ENABLE_PULLUPS
    PORTA |= 255;
    PORTB |= 255;
    PORTC |= 255;
    PORTD |= 255 & ~(_UV(4) | _UV(5) | _UV(6));
    PORTE |= 255 & ~(_UV(0) | _UV(1) | _UV(2) | _UV(6) | _UV(7));
    PORTF |= 255;
    PORTG |= 255 & ~(_UV(3) | _UV(4) | _UV(6) | _UV(7));
    PORTH |= 255 & ~(_UV(2) | _UV(7));
    PORTJ |= 255 & ~(_UV(2) | _UV(3) | _UV(4) | _UV(5) | _UV(6) | _UV(7));
    PORTK |= 255;
    PORTL |= 255;
#else
    PORTA &= 255;
    PORTB &= 255;
    PORTC &= 255;
    PORTD &= 255 & ~(_UV(4) | _UV(5) | _UV(6));
    PORTE &= 255 & ~(_UV(0) | _UV(1) | _UV(2) | _UV(6) | _UV(7));
    PORTF &= 255;
    PORTG &= 255 & ~(_UV(3) | _UV(4) | _UV(6) | _UV(7));
    PORTH &= 255 & ~(_UV(2) | _UV(7));
    PORTJ &= 255 & ~(_UV(2) | _UV(3) | _UV(4) | _UV(5) | _UV(6) | _UV(7));
    PORTK &= 255;
    PORTL &= 255;
#endif
}

uint8_t tmpj;

void fill_curstate() {
    curstate[0] = PINA;
    curstate[1] = PINB;
    curstate[2] = PINC;
    curstate[3] = (PIND & ~(_UV(4) | _UV(5) | _UV(6))) | ((PINE & ~(_UV(0) | _UV(1) | _UV(2) | _UV(6) | _UV(7))) << 1);
    curstate[4] = PINF;
    tmpj=PINJ;
    curstate[5] = (PINH & ~(_UV(2) | _UV(7))) | BIT_AT(tmpj,0,2) | BIT_AT(tmpj,1,7);
    curstate[6] = PINK;
    curstate[7] = PINL;
    curstate[8] = (((PING & ( 1 << 0 )) >> 0) << 7) | (((PING & ( 1 << 1 )) >> 1) << 6) | (((PING & ( 1 << 2 )) >> 2) << 5) | (((PING & ( 1 << 5 )) >> 5) << 4);
}

int i;

void soft_reset() {
  wdt_enable(WDTO_15MS);
  _delay_ms(20);
} // YOLO

int main() {
    wdt_disable();
    wdt_enable(WDTO_250MS);

    serial_init();

    init_registers();
    micros_init();

    sei();

    fill_curstate();
    memcpy(&oldstate, &curstate, sizeof oldstate);
    s_putchr('S');
    s_putchr('.');
    s_putchr('.');
    s_putchr('.');
    s_putchr('.');
    s_putchr(sizeof curstate + 1 + sizeof microseconds);
    for(i=0;i<sizeof curstate;i++) {
        s_putchr(curstate[i]);
    }
    s_putchr('I');
    s_puti32(microseconds);
    s_putchr('.');
    s_putchr('.');
    s_putchr('.');
    s_putchr('.');
    s_putchr('E');

    while(1) {
        #ifndef DUMMY
        fill_curstate();
        #endif
        microseconds = micros();
        #ifndef DUMMY
        if(memcmp(&oldstate, &curstate, sizeof oldstate)) {
            memcpy(&oldstate, &curstate, sizeof oldstate);
        #else
        if(1) {
        #endif
            s_putchr('S');
            s_putchr('.');
            s_putchr('.');
            s_putchr('.');
            s_putchr('.');
            s_putchr(sizeof curstate + 1 + sizeof microseconds);
            for(i=0;i<sizeof curstate;i++) {
                s_putchr(curstate[i]);
            }
            s_putchr('T');
            s_puti32(microseconds);
            s_putchr('.');
            s_putchr('.');
            s_putchr('.');
            s_putchr('.');
            s_putchr('E');
        }
        if(microseconds>MICROS_OVERFLOW){
            soft_reset();
        }
        wdt_reset();
    }
    return 0;
}
