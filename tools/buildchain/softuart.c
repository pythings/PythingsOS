/*
The MIT License (MIT)

Copyright (c) 2015 plieningerweb

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <stdio.h>
#include "softuart.h"
#include "ets_sys.h"
#include "etshal.h"
#include "osapi.h"
#include "gpio.h"
#include "esp_mphal.h"
#include "user_interface.h"
#include "py/runtime.h"
#include "modmachine.h"

// 仅支持一路softuart，多路放到ESP32中考虑，ESP32还将纳入FREERTOS
softuart_t s[1];

//intialize list of gpio names and functions
const softuart_reg_t softuart_reg[] =
{
  { 0, 0 },  //gpio0，gpio0 low-reset high-run
  { 0, 0 },  //gpio1 (uart0)
  { 0, 0 },  //gpio2，when reset must be high
  { 0, 0 },  //gpio3 (uart0)
  { PERIPHS_IO_MUX_GPIO4_U, FUNC_GPIO4 },  //gpio4
  { PERIPHS_IO_MUX_GPIO5_U, FUNC_GPIO5 },  //gpio5
  { 0, 0 },
  { 0, 0 },
  { 0, 0 },
  { PERIPHS_IO_MUX_SD_DATA2_U, FUNC_GPIO9 },    // gpio9,10虽然定义为内部的flash使用，但是实际未接
  { PERIPHS_IO_MUX_SD_DATA3_U, FUNC_GPIO10 },   // 即使外接sd卡，也只需要4线，不影响gpio9和10
  { 0, 0 },
  { PERIPHS_IO_MUX_MTDI_U, FUNC_GPIO12 },  //gpio12
  { PERIPHS_IO_MUX_MTCK_U, FUNC_GPIO13 },  //gpio13
  { PERIPHS_IO_MUX_MTMS_U, FUNC_GPIO14 },  //gpio14
  { 0, 0 },  //gpio15，reset时必须拉低，所以不能做uart使用
  //@TODO TODO gpio16 is missing (?include)
};

// void* for type compatibility with etshal.h: void ets_isr_attach(int irq_no, void (*handler)(void *), void *arg);
// 接收中断服务程序
void MP_FASTCODE(softuart_gpio_irq)(void *p)
{

  // 停止rxpin中断功能，准备作为输入读取数据
  gpio_pin_intr_state_set(GPIO_ID_PIN(s->rxpin.gpio_id), GPIO_PIN_INTR_DISABLE);

  // 读取中断寄存器状态
  uint32_t gpio_status = GPIO_REG_READ(GPIO_STATUS_ADDRESS);
  
  uint8_t rxlevel = GPIO_INPUT_GET(GPIO_ID_PIN(s->rxpin.gpio_id));
  // 低电平表示开始位，只实现了(8,NONE,1)也就是8bit数据，无校验位，1停止位
  if(rxlevel == 0) {
    // 等待半个周期取下一个rx电平，半个周期是为了下一周期内对准中间   
    mp_hal_delay_us_fast(s->bit_time/2);
    // 读rx一个byte
    uint8_t rxbyte = 0;   // 用于放置rx读到的值
    for (uint8_t i = 0; i < 8; i++) {
      mp_hal_delay_us_fast(s->bit_time);
      if(GPIO_INPUT_GET(GPIO_ID_PIN(s->rxpin.gpio_id))) rxbyte = (rxbyte >> 1) | 0x80;
      else rxbyte >>= 1;
    }

    // 存入rx缓存
    uint8_t next = (s->buffer.receive_buffer_tail + 1) % SOFTUART_MAX_RX_BUFF;
    if (next != s->buffer.receive_buffer_head) {
      s->buffer.receive_buffer[s->buffer.receive_buffer_tail] = rxbyte; // save new byte
      s->buffer.receive_buffer_tail = next;
    } else {
      s->buffer.buffer_overflow = 1;
    }

    mp_hal_delay_us_fast(s->bit_time);   // 等待结束位过去

  } 

  // 清中断并重新启用rxpin的中断
  GPIO_REG_WRITE(GPIO_STATUS_W1TC_ADDRESS, gpio_status);
  gpio_pin_intr_state_set(GPIO_ID_PIN(s->rxpin.gpio_id), 3);
}

BOOL softuart_init(uint8_t txpin, uint8_t rxpin, uint32_t baudrate)
{
  // pin脚不可以使用错误退出
  if (softuart_reg[txpin].gpio_mux_name==0 || softuart_reg[rxpin].gpio_mux_name==0) return false;

  // 这是有esp-open-sdk提供的
  gpio_init();

  // init tx pin
  s->txpin.gpio_id = txpin;
  s->txpin.gpio_mux_name = softuart_reg[txpin].gpio_mux_name;
  s->txpin.gpio_func = softuart_reg[txpin].gpio_func;
  // init rx pin
  s->rxpin.gpio_id = rxpin;
  s->rxpin.gpio_mux_name = softuart_reg[rxpin].gpio_mux_name;
  s->rxpin.gpio_func = softuart_reg[rxpin].gpio_func;

  //set bit time
  if(baudrate <= 0) baudrate = SOFTUART_DEF_BAUDRATE;  // 如果<0,默认就是115200
  s->baudrate = baudrate;
  s->bit_time = (1000000 / baudrate);
  if ( ((100000000 / baudrate) - (100*s->bit_time)) > 50 ) s->bit_time--;

  //init tx pin func
  PIN_FUNC_SELECT(s->txpin.gpio_mux_name, s->txpin.gpio_func);  //enable pin as gpio
  PIN_PULLUP_EN(s->txpin.gpio_mux_name); //set pullup (UART idle is VDD)
  GPIO_OUTPUT_SET(GPIO_ID_PIN(s->txpin.gpio_id), 1); //set high for tx idle
  os_delay_us(100);

  //init rx pin func
  PIN_FUNC_SELECT(s->rxpin.gpio_mux_name, s->rxpin.gpio_func);  //enable pin as gpio
  PIN_PULLUP_EN(s->rxpin.gpio_mux_name);   //set pullup (UART idle is VDD)
  GPIO_DIS_OUTPUT(GPIO_ID_PIN(s->rxpin.gpio_id));  //set to input -> disable output
  ETS_GPIO_INTR_DISABLE();    //disable interrupts by GPIO
  ETS_GPIO_INTR_ATTACH(softuart_gpio_irq, s);    // 后面参数是传递给中断处理函数的指针，

  gpio_register_set(GPIO_PIN_ADDR(s->rxpin.gpio_id),   // 不确定功能，但是必须要做
               GPIO_PIN_INT_TYPE_SET(GPIO_PIN_INTR_DISABLE)  |
               GPIO_PIN_PAD_DRIVER_SET(GPIO_PAD_DRIVER_DISABLE) |
               GPIO_PIN_SOURCE_SET(GPIO_AS_PIN_SOURCE));
  
  GPIO_REG_WRITE(GPIO_STATUS_W1TC_ADDRESS, BIT(s->rxpin.gpio_id));  // 清除中断状态
  gpio_pin_intr_state_set(GPIO_ID_PIN(s->rxpin.gpio_id), 3); // 设置gpio中断，3表示任何边沿触发
  ETS_GPIO_INTR_ENABLE();   // 使能中断

  return true;
}

// Function for printing individual characters
void MP_FASTCODE(softuart_putchar)(uint8_t data)
{
  GPIO_OUTPUT_SET(GPIO_ID_PIN(s->txpin.gpio_id), 0);    // 先输出一个起始位0
  for (uint8_t i=0;i<8;i++) {
    mp_hal_delay_us_fast(s->bit_time);
    GPIO_OUTPUT_SET(GPIO_ID_PIN(s->txpin.gpio_id), (data >> i) & 0x01);
  }
  mp_hal_delay_us_fast(s->bit_time);
  GPIO_OUTPUT_SET(GPIO_ID_PIN(s->txpin.gpio_id), 1);
  mp_hal_delay_us_fast(s->bit_time<<3);
}

uint8_t softuart_getcount(void)
{
  return (SOFTUART_MAX_RX_BUFF - s->buffer.receive_buffer_head + s->buffer.receive_buffer_tail) % SOFTUART_MAX_RX_BUFF;  
}

uint8_t softuart_getchar(void)
{
  if (s->buffer.receive_buffer_head == s->buffer.receive_buffer_tail) return 0;   // 空return 0

  uint8_t d = s->buffer.receive_buffer[s->buffer.receive_buffer_head]; // grab next byte
  s->buffer.receive_buffer_head = (s->buffer.receive_buffer_head + 1) % SOFTUART_MAX_RX_BUFF;
  return d;
}

BOOL softuart_wait(uint32_t timeout)
{
  if (s->buffer.receive_buffer_head != s->buffer.receive_buffer_tail) return true;  // 如果有数据直接返回

  if (timeout == 0) timeout = SOFTUART_DEF_WAITUS;     // 如果是0则默认等待时间
  uint32_t starttime = system_get_time();    // 记录一下开始时间
  uint32_t now, endtime = starttime + timeout; // 计算结束时间
  BOOL nowover = false;    // 判断now是否翻转了
  while(true) {
    if (s->buffer.receive_buffer_head != s->buffer.receive_buffer_tail) return true;   // 如果收到字符那么直接返回true
    now = (uint32_t)system_get_time();
    // 只要小于starttime就表示翻转过了，单独记录是因为如果timeout_us很大，那么now翻转后也会超过startime就无法判断是否翻转过了
    if (now < starttime) nowover = true;    // 只要小于一次就表示溢出了，再超过starttime也不会改变
    if (endtime > starttime) {        // endtime没有溢出
      if (now > endtime || nowover) return false;      // now超出endtime或者now溢出，说明超过endtime了
    } else {
      if (nowover && now > endtime) return false; // endtime,now都溢出了，而且now超过endtime
    }
    ets_event_poll();
  }
}

// Flush data from buffer
void softuart_flush(void)
{
  s->buffer.receive_buffer_head = 0;
  s->buffer.receive_buffer_tail = 0;
  s->buffer.buffer_overflow = 0;
}


// ----------------------------------------------------------------------------------- mp 函数字典

STATIC mp_obj_t mp_softuart_get(mp_obj_t self) {    // 使用固定参数的第一个self类型为mp_obj_t
  //pyb_softuart_obj_t *s = MP_OBJ_TO_PTR(self);
  return mp_obj_new_int_from_uint(softuart_getchar());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_softuart_get_obj, mp_softuart_get);

STATIC mp_obj_t mp_softuart_put(mp_obj_t self, mp_obj_t data) {
  uint8_t ch = (uint8_t)mp_obj_get_int(data);
  softuart_putchar(ch);
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mp_softuart_put_obj, mp_softuart_put);

STATIC mp_obj_t mp_softuart_getcount(mp_obj_t self) {
  return mp_obj_new_int_from_uint(softuart_getcount());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_softuart_getcount_obj, mp_softuart_getcount);

STATIC mp_obj_t mp_softuart_isoverflow(mp_obj_t self) {
  if (s->buffer.buffer_overflow) return mp_const_true;
  else return mp_const_false;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_softuart_isoverflow_obj, mp_softuart_isoverflow);

STATIC mp_obj_t mp_softuart_flush(mp_obj_t self) {
  softuart_flush();
  return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_softuart_flush_obj, mp_softuart_flush);

STATIC mp_obj_t mp_softuart_wait(size_t n_args, const mp_obj_t *args)
{
  uint32_t us = (n_args == 2)? (uint32_t)mp_obj_get_int(args[1]) : SOFTUART_DEF_WAITUS;
  if (softuart_wait(us)) return mp_const_true;
  else  return mp_const_false;
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mp_softuart_wait_obj, 1, 2, mp_softuart_wait);

// 写字符串和写2进制是一样的，write('abc'),write(b'\xbb\x12\x13'),buf=bytearray(20) write(buf)或write(buf,10)
STATIC mp_obj_t mp_softuart_write(size_t n_args, const mp_obj_t *args)
{
  mp_buffer_info_t bufinfo;
  mp_get_buffer_raise(args[1], &bufinfo, MP_BUFFER_READ);
  uint8_t len = n_args == 3 ? (uint8_t)mp_obj_get_int(args[2]) : bufinfo.len;
  uint8_t *buf = (uint8_t*)bufinfo.buf;
  for (uint8_t i = 0; i < len; i++) softuart_putchar(*buf++);
  return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mp_softuart_write_obj, 2, 3, mp_softuart_write);

STATIC mp_obj_t mp_softuart_getall(mp_obj_t self) {
    uint8_t len = softuart_getcount();
    if (len == 0) return mp_const_none;
    vstr_t vstr;
    vstr_init_len(&vstr, len);    // 初始化长度
    for (uint8_t i=0;i<len;i++) vstr.buf[i]=softuart_getchar();
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_softuart_getall_obj, mp_softuart_getall);

// */

// ----------------------------------------------------------------------------------- mp 基本类结构

// 函数字典
STATIC const mp_rom_map_elem_t softuart_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_get), MP_ROM_PTR(&mp_softuart_get_obj) },             // get a char
    { MP_ROM_QSTR(MP_QSTR_put), MP_ROM_PTR(&mp_softuart_put_obj) },             // put a char
    { MP_ROM_QSTR(MP_QSTR_getcount), MP_ROM_PTR(&mp_softuart_getcount_obj) },   // get rx count
    { MP_ROM_QSTR(MP_QSTR_flush), MP_ROM_PTR(&mp_softuart_flush_obj) },         // flush rx buf
    { MP_ROM_QSTR(MP_QSTR_isoverflow), MP_ROM_PTR(&mp_softuart_isoverflow_obj) },    // rx is overflow

    { MP_ROM_QSTR(MP_QSTR_wait), MP_ROM_PTR(&mp_softuart_wait_obj) },           // wait for rx available
    { MP_ROM_QSTR(MP_QSTR_write), MP_ROM_PTR(&mp_softuart_write_obj) },         // write buf
    { MP_ROM_QSTR(MP_QSTR_getall), MP_ROM_PTR(&mp_softuart_getall_obj) },       // get all rx buf
};
MP_DEFINE_CONST_DICT(mp_softuart_locals_dict, softuart_locals_dict_table);

// 映射到类的__init__
STATIC mp_obj_t mp_softuart_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum {ARG_tx, ARG_rx, ARG_baudrate};
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_tx,       MP_ARG_INT, {.u_int = 14} },
        { MP_QSTR_rx,       MP_ARG_INT, {.u_int = 12} },      
        { MP_QSTR_baudrate, MP_ARG_INT, {.u_int = 115200} },
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    // create new object
    pyb_softuart_obj_t *self = m_new_obj(pyb_softuart_obj_t);  // 获得属性
    self->base.type = &mp_softuart_type;        // 类型是统一的mp_obj_type_t变量

    // configure softuart
    if (!softuart_init((uint8_t)args[ARG_tx].u_int, (uint8_t)args[ARG_rx].u_int, (uint32_t)args[ARG_baudrate].u_int)) {
      mp_raise_ValueError("softuart cannot intialize");
    }

    return MP_OBJ_FROM_PTR(self);
}

// 映射到类的__str__和__repr__
STATIC void mp_softuart_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    //pyb_softuart_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_printf(print, "softuart(tx=%u, rx=%u, baudrate=%u)", (s->txpin).gpio_id, (s->rxpin).gpio_id, s->baudrate);
}

// 映射到python类的函数体，必须在包内注册，如modmachine.h/.c
const mp_obj_type_t mp_softuart_type = {
    { &mp_type_type },
    .name = MP_QSTR_SOFTUART,           // 必须在所属的包中注册，此处modmachine.c中注册
    .print = mp_softuart_print,         // 映射到__str__
    .make_new = mp_softuart_make_new,   // 映射到__init__
    .locals_dict = (mp_obj_dict_t*)&mp_softuart_locals_dict,    // 功能映射到locals_dict上
};

// */

