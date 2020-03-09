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

#ifndef SOFTUART_H_
#define SOFTUART_H_


#include "os_type.h"
#include "py/obj.h"

// 接收缓存的大小
#define SOFTUART_MAX_RX_BUFF    256         // 默认rx缓存大小，最大就是256个
#define SOFTUART_DEF_BAUDRATE   115200      // 默认连接速率
#define SOFTUART_DEF_WAITUS     10000       // 默认等待rx时间，10000us

// gpio的寄存器映射功能，此为常量
typedef struct {
  uint32_t gpio_mux_name;
  uint8_t gpio_func;
} softuart_reg_t;

// gpio的具体参数
typedef struct softuart_pin_t {
  uint8_t gpio_id;
  uint32_t gpio_mux_name;
  uint8_t gpio_func;
} softuart_pin_t;

// uart缓存
typedef struct softuart_buffer_t {
  char receive_buffer[SOFTUART_MAX_RX_BUFF];
  uint8_t receive_buffer_tail;    // 缓存最大256个
  uint8_t receive_buffer_head;
  uint8_t buffer_overflow;
} softuart_buffer_t;

// uart整体结构，每个softuart都有单独的数据结构
typedef struct {
  softuart_pin_t txpin;
  softuart_pin_t rxpin;
  volatile softuart_buffer_t buffer;
  uint32_t baudrate;
  uint16_t bit_time;
} softuart_t;

// ---------------------------------------------------------------------------------------------- 映射到mp的结构体

// 映射到python类的结构体，包含self的属性，在make_new中初始化
typedef struct _pyb_softuart_obj_t {
  mp_obj_base_t base;     // 指向mp对象变量，也就是明确self的功能函数
} pyb_softuart_obj_t;

#endif /* SOFTUART_H_ */