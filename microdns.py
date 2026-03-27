#Author : iw0雨渊(Gitee:@wth_iw0 GitHub:@iw0_wth)
#Date : 2025.8.8
#Description : DNS Server Based on Micropython.This project can provide assistance for DNS Spoofing,Evil Twin Attack and MITM on ESP32/ESP8266.
#Copyright © 2025 iw0雨渊. All rights reserved.
#Version : 1.0.0
#License : MIT License
#Contact : EMAIL
#Contact : tianqi2021_001@163.com
#Github : https://github.com/iw0-wth
import socket
import struct
import time
import gc
import dns_list

class DNSServer:
    """DNS服务器类"""
    
    def __init__(self, port=53, ttl=300):
        self.port = port
        self.ttl = ttl
        self.socket = None
        self.running = False
        
        # DNS记录映射表
        self.dns_records = dns_list.DNS_LIST
        
        # 默认DNS服务器（用于转发查询）
        self.upstream_dns = '8.8.8.8'
    
    def start(self):
        """启动DNS服务器"""
        try:
            # 创建UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('0.0.0.0', self.port))
            
            self.running = True
            print(f"[dns]DNS服务器正在监听端口 {self.port}")
            
            while self.running:
                try:
                    # 接收DNS查询
                    data, addr = self.socket.recvfrom(512)
                    if data:
                        # 处理DNS查询
                        response = self.handle_dns_query(data)
                        if response:
                            self.socket.sendto(response, addr)
                            
                except Exception as e:
                    print(f"[dns]处理DNS查询时出错: {e}")
                    continue
                    
        except Exception as e:
            print(f"[dns]启动DNS服务器失败: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止DNS服务器"""
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
        print("[DNS]DNS服务器已停止")
    
    def handle_dns_query(self, data):
        """处理DNS查询"""
        try:
            # 解析DNS查询头部
            header = self.parse_dns_header(data)
            
            # 检查是否为查询请求
            if header['qr'] != 0:  # 不是查询请求
                return None
            
            # 解析查询部分
            query_info = self.parse_dns_query(data, 12)
            domain_name = query_info['name']
            query_type = query_info['type']
            
            print(f"[dns]收到DNS查询: {domain_name} (类型: {query_type})")
            
            # 检查查询类型
            if query_type == 1:  # A记录查询
                return self.handle_a_query(data, domain_name)
            elif query_type == 28:  # AAAA记录查询
                return self.handle_aaaa_query(data, domain_name)
            else:
                # 其他类型查询，返回空响应
                return self.create_empty_response(data)
                
        except Exception as e:
            print(f"[dns]解析DNS查询失败: {e}")
            return None
    
    def parse_dns_header(self, data):
        """解析DNS头部"""
        if len(data) < 12:
            raise ValueError("DNS数据包太短")
        
        # 解析DNS头部字段
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', data[:12])
        
        return {
            'id': id,
            'qr': (flags >> 15) & 1,      # 查询/响应标志
            'opcode': (flags >> 11) & 15,  # 操作码
            'aa': (flags >> 10) & 1,       # 权威应答
            'tc': (flags >> 9) & 1,        # 截断标志
            'rd': (flags >> 8) & 1,        # 期望递归
            'ra': (flags >> 7) & 1,        # 递归可用
            'z': (flags >> 4) & 7,         # 保留字段
            'rcode': flags & 15,           # 响应码
            'qdcount': qdcount,
            'ancount': ancount,
            'nscount': nscount,
            'arcount': arcount
        }
    
    def parse_dns_query(self, data, offset):
        """解析DNS查询部分"""
        # 解析域名
        name, new_offset = self.parse_domain_name(data, offset)
        
        # 解析查询类型和类
        if len(data) < new_offset + 4:
            raise ValueError("DNS查询数据不完整")
        
        qtype, qclass = struct.unpack('!HH', data[new_offset:new_offset+4])
        
        return {
            'name': name,
            'type': qtype,
            'class': qclass
        }
    
    def parse_domain_name(self, data, offset):
        """解析域名"""
        name_parts = []
        current_offset = offset
        
        while current_offset < len(data):
            length = data[current_offset]
            current_offset += 1
            
            if length == 0:
                break
            elif (length & 0xC0) == 0xC0:
                # 压缩指针
                pointer = ((length & 0x3F) << 8) | data[current_offset]
                current_offset += 1
                compressed_name, _ = self.parse_domain_name(data, pointer)
                name_parts.append(compressed_name)
                break
            else:
                # 普通标签
                if current_offset + length <= len(data):
                    try:
                        label = data[current_offset:current_offset + length].decode('ascii')
                    except:
                        label = data[current_offset:current_offset + length].decode('ascii', 'ignore')
                    name_parts.append(label)
                    current_offset += length
                else:
                    break
        
        return '.'.join(name_parts), current_offset
    
    def handle_a_query(self, data, domain_name):
        """处理A记录查询"""
        # 查找域名对应的IP地址
        ip_address = self.lookup_domain(domain_name)
        
        # 所有域名都应该解析到ESP32的IP地址
        print(f"[dns]解析 {domain_name} -> {ip_address}")
        return self.create_a_response(data, domain_name, ip_address)
    
    def handle_aaaa_query(self, data, domain_name):
        """处理AAAA记录查询"""
        # 对于IPv6查询，返回空响应（因为我们主要处理IPv4）
        return self.create_empty_response(data)
    
    def lookup_domain(self, domain_name):
        """查找域名对应的IP地址"""
        # 直接匹配
        if domain_name in self.dns_records:
            return self.dns_records[domain_name]
        
        # 通配符匹配
        for pattern, ip in self.dns_records.items():
            if pattern.startswith('*.'):
                suffix = pattern[2:]  # 去掉 '*.' 前缀
                if domain_name.endswith('.' + suffix):
                    return ip
        
        # 默认返回ESP32的IP地址
        return '192.168.4.1'
    
    def create_a_response(self, data, domain_name, ip_address):
        """创建A记录响应"""
        # 解析原始查询
        header = self.parse_dns_header(data)
        query_info = self.parse_dns_query(data, 12)
        
        # 构建响应
        response = bytearray()
        
        # 响应头部
        response.extend(struct.pack('!H', header['id']))  # ID
        response.extend(struct.pack('!H', 0x8180))        # 标志 (响应 + 递归可用)
        response.extend(struct.pack('!H', 1))             # 查询数量
        response.extend(struct.pack('!H', 1))             # 应答数量
        response.extend(struct.pack('!H', 0))             # 权威数量
        response.extend(struct.pack('!H', 0))             # 附加数量
        
        # 查询部分
        response.extend(self.encode_domain_name(domain_name))
        response.extend(struct.pack('!HH', 1, 1))         # 类型(A)和类(IN)
        
        # 应答部分
        response.extend(self.encode_domain_name(domain_name))
        response.extend(struct.pack('!HH', 1, 1))         # 类型(A)和类(IN)
        response.extend(struct.pack('!I', self.ttl))      # TTL
        response.extend(struct.pack('!H', 4))             # 数据长度
        response.extend(struct.pack('!4B', *map(int, ip_address.split('.'))))     # IP地址
        
        return bytes(response)
    
    def create_empty_response(self, data):
        """创建空响应（用于不支持的查询类型）"""
        header = self.parse_dns_header(data)
        
        response = bytearray()
        response.extend(struct.pack('!H', header['id']))  # ID
        response.extend(struct.pack('!H', 0x8183))        # 标志 (响应 + 名称错误)
        response.extend(struct.pack('!H', 1))             # 查询数量
        response.extend(struct.pack('!H', 0))             # 应答数量
        response.extend(struct.pack('!H', 0))             # 权威数量
        response.extend(struct.pack('!H', 0))             # 附加数量
        
        # 复制查询部分
        response.extend(data[12:])
        
        return bytes(response)
    
    def encode_domain_name(self, domain_name):
        """编码域名"""
        encoded = bytearray()
        for part in domain_name.split('.'):
            encoded.append(len(part))
            encoded.extend(part.encode('ascii'))
        encoded.append(0)  # 结束标记
        return encoded