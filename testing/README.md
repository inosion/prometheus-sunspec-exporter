# Testing Notes

To test if your inveter supports SunSpec, 

Run the following 

```
# Build the test 
docker build -t inosion/sunspec-test .

# Test an IP, with target modbus address of 126
$ docker run --rm -ti  inosion/sunspec-test python3 /src/pysunspec/scripts/suns.py -i 192.168.1.40 -a 126

Timestamp: 2021-01-10T10:45:12Z

model: Common (1)

      Manufacturer (Mn):                                  SMA           
      Model (Md):                              Solar Inverter           
      Options (Opt):                                     9099           
      Version (Vr):                                  VERSION            
      Serial Number (SN):                           SERIAL_NUMBER           

model: Ethernet Link Layer (11)

      Ethernet Link Speed (Spd):                          100 Mbps      
      Interface Status Flags (CfgSt):                  0x0003           
      Link State (St):                                      1           
      MAC (MAC):                            CA:FE:BA:BA:BE:00           

model: IPv4 (12)

      Config Status (CfgSt):                                1           
      Change Status (ChgSt):                           0x0000           
      Config Capability (Cap):                         0x0005           
      IPv4 Config (Cfg):                                    1           
      Control (Ctl):                                        0           
      IP (Addr):                                192.168.0.170           
      Netmask (Msk):                            255.255.255.0           
      Gateway (Gw):                             192.168.0.170           
      DNS1 (DNS1):                              192.168.0.170           

model: Inverter (Three Phase) (103)

      Amps PhaseA (AphA):                              3276.8 A         
      Amps PhaseB (AphB):                              3276.8 A         
      Amps PhaseC (AphC):                              3276.8 A         
      WattHours (WH):                              14744840.0 Wh        
      Operating State (St):                                 0           
      Event1 (Evt1):                               0x00000000           

model: Nameplate (120)

      DERTyp (DERTyp):                                      4           
      WRtg (WRtg):                                     6000.0 W         
      VARtg (VARtg):                                   6000.0 VA        

model: Basic Settings (121)

      WMax (WMax):                                     6000.0 W         
      VRef (VRef):                                        230 V         
      VRefOfs (VRefOfs):                                    0 V         
      VAMax (VAMax):                                   6000.0 VA        
      WGra (WGra):                                         20 % WMax/sec
      ECPNomHz (ECPNomHz):                                 50 Hz        

model: Measurements_Status (122)

      PVConn (PVConn):                                 0x0001           
      ActWh (ActWh):                                 14744836 Wh        

model: Immediate Controls (123)

      WMaxLim_Ena (WMaxLim_Ena):                            1           
      OutPFSet_Ena (OutPFSet_Ena):                          0           
      VArPct_Mod (VArPct_Mod):                              1           
      VArPct_Ena (VArPct_Ena):                              0           

model: Storage (124)


model: Static Volt-VAR (126)

      NCrv (NCrv):                                          1           
      NPt (NPt):                                            8           
   01:ActPt (ActPt):                                        4           
   01:DeptRef (DeptRef):                                    2           
   01:V1 (V1):                                          100.0 % VRef    
   01:VAr1 (VAr1):                                      100.0           
   01:V2 (V2):                                          100.0 % VRef    
   01:VAr2 (VAr2):                                      100.0           
   01:V3 (V3):                                          100.0 % VRef    
   01:VAr3 (VAr3):                                      100.0 Various   
   01:V4 (V4):                                          100.0           
   01:VAr4 (VAr4):                                      100.0           
   01:V5 (V5):                                          100.0 % VRef    
   01:VAr5 (VAr5):                                      100.0           
   01:V6 (V6):                                          100.0 % VRef    
   01:VAr6 (VAr6):                                      100.0           
   01:V7 (V7):                                          100.0 % VRef    
   01:VAr7 (VAr7):                                      100.0           
   01:V8 (V8):                                          100.0 % VRef    
   01:VAr8 (VAr8):                                      100.0           
   01:ReadOnly (ReadOnly):                                  0           

model: Freq-Watt Param (127)

      WGra (WGra):                                         40 % PM/Hz   
      HzStr (HzStr):                                      0.2 Hz        
      HzStop (HzStop):                                    0.2 Hz        
      HysEna (HysEna):                                 0x0000           
      ModEna (ModEna):                                 0x0000           
      HzStopWGra (HzStopWGra):                          10000 % WMax/min

model: Dynamic Reactive Current (128)

      ArGraMod (ArGraMod):                                  1           
      ModEna (ModEna):                                 0x0000           
      FilTms (FilTms):                                     60 Secs      
      DbVMin (DbVMin):                                  65526 % VRef    
      DbVMax (DbVMax):                                     10 % VRef    
      BlkZnV (BlkZnV):                                     70 % VRef    
      HysBlkZnV (HysBlkZnV):                                5 % VRef    
      BlkZnTmms (BlkZnTmms):                                0 mSecs     

model: Watt-PF (131)

      NCrv (NCrv):                                          1           
      NPt (NPt):                                           12           
   01:ReadOnly (ReadOnly):                                  0           

model: Volt-Watt (132)

      NCrv (NCrv):                                          1           
      NPt (NPt):                                            8           
   01:ActPt (ActPt):                                        2           
   01:DeptRef (DeptRef):                                    2           
   01:V1 (V1):                                          100.0 % VRef    
   01:W1 (W1):                                          100.0 % VRef    
   01:V2 (V2):                                          100.0 % VRef    
   01:W2 (W2):                                          100.0 % VRef    
   01:V3 (V3):                                          100.0 % VRef    
   01:W3 (W3):                                          100.0 % VRef    
   01:V4 (V4):                                          100.0 % VRef    
   01:W4 (W4):                                          100.0 % VRef    
   01:V5 (V5):                                          100.0 % VRef    
   01:W5 (W5):                                          100.0 % VRef    
   01:V6 (V6):                                          100.0 % VRef    
   01:W6 (W6):                                          100.0 % VRef    
   01:V7 (V7):                                          100.0 % VRef    
   01:W7 (W7):                                          100.0 % VRef    
   01:V8 (V8):                                          100.0 % VRef    
   01:W8 (W8):                                          100.0 % VRef    
   01:RmpPt1Tms (RmpPt1Tms):                               10 Secs      
   01:RmpDecTmm (RmpDecTmm):                            12000 % WMax/min
   01:RmpIncTmm (RmpIncTmm):                            12000 % WMax/min
   01:ReadOnly (ReadOnly):                                  0           

model: Multiple MPPT Inverter Extension Model (160)

      Number of Modules (N):                                2           
   01:Input ID (ID):                                        1           
   02:Input ID (ID):                                        2 

```
