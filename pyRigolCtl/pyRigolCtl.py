import numpy as np 
import pyvisa as visa
import yaml 
import time

VISA_RM = visa.ResourceManager('@py')
class RigolSupply():
    
    '''Used to control a single Rigol PSU.'''
    
    
    def __init__(self, address, n_ch, visa_resource_manager=VISA_RM):
        resource_str = f'TCPIP0::{address:s}::INSTR'
        #print(f"Building {resource_str}")
        self.resource = VISA_RM.open_resource(resource_str, write_termination='\n', read_termination='\n')

        self.write = self.resource.write
        self.query = self.resource.query
        
        self.n_ch = n_ch
        
        self.voltages = np.zeros(n_ch)
        #self.currents = np.zeros(n_ch)
        
        #self.ovp = np.zeros(n_ch)
        self.ocp = np.zeros(n_ch)
        
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
    
    
    def set_voltage(self, ch, voltage):
        self.tell(f":SOURCE{ch}:VOLT {voltage}")
        
    def get_voltage(self):
        return [self.query(f":SOURCE{ch+1}:VOLT?") for ch in range(self.n_ch)]        
    
    def set_ocp(self, ch, ocp):
        self.tell(f":OUTP:OCP:VAL CH{ch},{ocp}")
    
    def get_ocp(self):
        return [self.query(f":OUTP:OCP:VAL? CH{ch+1}") for ch in range(self.n_ch)]

    
class RigolArray():    
    
    '''
    
    Used to build and deploy an array of RigolSupply objects.
    Designed to be used with configuration files: 
    
        #Supply voltages.
        #Note: Negative voltage is interpreted in software as "do not use".
        S3:
            IP: "10.10.1.53"
            NCH: 2
            CH1:
                V: -99
                OCP: 0.01
            CH2: 
                V: 3.6
                OCP: 2.0

        S2:
            IP: "10.10.1.52"
            NCH: 3
            CH1:
                V: 5.0
                OCP: 1.25
            CH2: 
                V: -99
                OCP: 0.01
            CH3:
                V: 2.4
                OCP: 3.0        
        
    '''
    
    def __init__(self, psconfig_filename):
        with open(psconfig_filename) as f:
            supply_cfg = yaml.load(f, Loader=yaml.FullLoader)

        self.supply_handlers = []
        for supply in supply_cfg:
            ps = RigolSupply(supply_cfg[supply]['IP'], supply_cfg[supply]['NCH'])   
            print(ps.IDENTITY)

            for ch in range(ps.n_ch):
                ps.tell(f":OUTP:OCP CH{ch+1},ON")
                ps.voltages[ch] = supply_cfg[supply][f"CH{ch+1}"]['V']
                ps.ocp[ch] = supply_cfg[supply][f"CH{ch+1}"]['OCP']
                if ps.voltages[ch] > 0:
                    ps.set_voltage(ch+1, ps.voltages[ch])
                    ps.set_ocp(ch+1, ps.ocp[ch])
                else:
                    ps.set_voltage(ch+1, 0)
                    ps.set_ocp(ch+1, 0.001)            


            self.supply_handlers += [ps]

        print()        
    
    def apply_to_all(self, ask=None, tell=None):
        for supply in self.supply_handlers:
            if ask is not None:
                supply.ask(ask)
            if tell is not None:
                supply.tell(tell)

    def power_cycle_all_supplies(self):
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                print(supply.enable_output(ch+1))
                time.sleep(1)
                print(supply.disable_output(ch+1))

    def report_status(self):
        for supply in self.supply_handlers:
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

    def power_up_all(self, verbose=False):
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                if supply.voltages[ch] > 0:
                    supply.enable_output(ch+1)        
        if verbose:
            time.sleep(1.0)
            self.report_status()


    def power_down_all(self, verbose=False):
        if verbose:
            self.report_status()
            print("----------------------")
        for supply in self.supply_handlers:
            for ch in range(supply.n_ch):
                supply.disable_output(ch+1)
        if verbose:
            time.sleep(1.0)
            self.report_status()