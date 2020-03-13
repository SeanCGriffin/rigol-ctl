import matplotlib.pyplot as plt
import numpy as np 

import pyvisa as visa

VISA_RM = visa.ResourceManager('@py')


class RigolSupply():
    def __init__(self, address, n_ch=2, visa_resource_manager=VISA_RM):
        resource_str = f'TCPIP0::{address:s}::INSTR'
        print(resource_str)
        self.resource = VISA_RM.open_resource(resource_str, write_termination='\n', read_termination='\n')

        self.write = self.resource.write
        self.query = self.resource.query
        
        self.n_ch = n_ch
        
        self.voltages = np.zeros(n_ch)
        self.currents = np.zeros(n_ch)
        
        self.ovp_lim = np.zeros(n_ch)
        self.ocp_lim = np.zeros(n_ch)
        
        

    @property
    def IDN(self):
        return self.query("*IDN?")
    
    @property
    def IP(self):
        return self.query(":SYSTem:COMMunicate:LAN:IPADdress?")
        
    def ask(self, question):
        response = self.query(question)
        print("Question: {0:s} - Response: {1:s}".format(question, str(response)))
        return response
    
    def tell(self, statement):
        return self.write(statemnet)
    
    def enable_output(self, ch):
        return self.write(f"OUTP:STAT CH{ch},ON")
    
    def disable_output(self, ch):
        return self.write(f"OUTP:STAT CH{ch},OFF")

    def set_ocp(self, ocp):
        for ch in range(n_ch):
            self.tell(f":OUTP:OCP:VAL CH{ch},{ocp[ch]}")
    
    def get_ocp(self):
         return [self.query(f":OUTP:OCP:VAL? CH{ch}") for ch in range(self.n_ch)]
    


supply_IPs = ["10.10.1.50", "10.10.1.51", "10.10.1.52", "10.10.1.53"]
supply_channels = [2, 2, 3, 2]
fpga_ps = [0, 2]
supplies = [RigolSupply(ip) for ip,n_ch in zip(supply_IPs, supply_channels)]