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
    
    @property
    def IDENTITY(self):
        return f"IDN: {self.IDN.split(',')[-2]} IP: {self.IP}"
        
    def ask(self, question, verbose=False):
        response = self.query(question)
        if verbose:
            print("Question: {0:s} - Response: {1:s}".format(question, str(response)))
        return response
    
    def tell(self, statement):
        return self.write(statement)
    
    def enable_output(self, ch):
        return self.tell(f"OUTP:STAT CH{ch},ON")
    
    def disable_output(self, ch):
        return self.tell(f"OUTP:STAT CH{ch},OFF")

    def set_ocp(self, ocp):
        for ch in range(n_ch):
            self.tell(f":OUTP:OCP:VAL CH{ch},{ocp[ch]}")
    
    def get_ocp(self):
        return [self.query(f":OUTP:OCP:VAL? CH{ch}") for ch in range(self.n_ch)]



def apply_to_all(supply_hanlers, ask=None, tell=None):
    for supply in supply_handlers:
        if ask is not None:
            supply.ask(ask)
        if tell is not None:
            supply.tell(tell)
                    
def power_on_fpga(supply_handlers, fpga_pair):
    supply_handlers[fpga_pair[0]].enable_output(fpga_pair[1])
    
def power_off_fpga(supply_handlers, fpga_pair):
    supply_handlers[fpga_pair[0]].disable_output(fpga_pair[1])
    
def power_cycle_fpga(supply_handlers, fpga_pair, sleepytime=1):
    power_off_fpga(supply_handlers, fpga_pair)
    time.sleep(sleepttime)
    power_on_fpga(supply_handlers, fpga_pair)
    
def power_cycle_all_supplies(supply_handlers):
    for supply in supply_handlers:
        for ch in range(supply.n_ch):
            print(supply.enable_output(ch+1))
            time.sleep(1)
            print(supply.disable_output(ch+1))

def report_status(supply_handlers):
    for supply in supply_handlers:
        print(supply.IDENTITY)
        print(f"\tChannel\t| Status\t| V\t\t| I (A)\t\t| P (W)  ")
        channel_stats = []
        channel_out_vals = []
        for ch in range(supply.n_ch):
            stat = supply.query(f"OUTP:STAT? CH{ch+1}")
            vals = supply.query(f"MEASure:ALL? CH{ch+1}")
            vals = vals.split(',')
            vals = [float(i) for i in vals]
            print(f"\t{ch+1:7d}\t| {stat:8s}\t| {vals[0]:3.4f}\t| {vals[1]:3.4f}\t| {vals[2]:3.4f}")
        print()
        
def power_up_all(supply_handlers, verbose=False):
    for supply in supply_handlers:
        for ch in range(supply.n_ch):
            supply.enable_output(ch+1)        
    if verbose:
        report_status(supply_handlers)
    
    
def power_down_all(supply_handlers, verbose=False):
    for supply in supply_handlers:
        for ch in range(supply.n_ch):
            supply.disable_output(ch+1)
    if verbose:
        report_status(supply_handlers)