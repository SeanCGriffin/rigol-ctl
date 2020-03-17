import numpy as np 

import pyvisa as visa

VISA_RM = visa.ResourceManager('@py')


class RigolSupply():
    def __init__(self, address, n_ch, visa_resource_manager=VISA_RM):
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
    
def power_cycle_all_supplies(supply_handlers):
    for supply in supply_handlers:
        print(supply.IDN)
        print(supply.n_ch)
        for ch in range(supply.n_ch):
            print(supply.enable_output(ch+1))
            time.sleep(1)
            print(supply.disable_output(ch+1))
    
def power_off_all_supplies(supply_handlers):
    for supply in supply_handlers:
        print(supply.IDN)
        print(supply.n_ch)
        for ch in range(supply.n_ch):
            print(supply.disable_output(ch+1))
            
            
def report_status(supply_handlers):
    for supply in supply_handlers:
        idn = supply.IDN
        channel_stats = []
        for ch in range(supply.n_ch):
            channel_stats += [supply.query(f"OUTP:STAT? CH{ch+1}")]
        print(f"Supply IDN: {idn}\t {channel_stats}")