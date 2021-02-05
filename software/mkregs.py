#!/usr/bin/python2.7
#
#    Build Latex tables of verilog module interface signals and registers
#

import sys
import os.path
import re
import math

infile = ''

def write_mapping(name_map, width_map, init_val_map, type_map, bank_map,cube_map):
    #write output file
    global infile
    fout = open (infile+'_gen.v', 'w')

    fout.write("//This file was generated by script swreg2regmap.py\n\n")

    fout.write("//address macros\n")
    for i in range(len(name_map)):
        fout.write("`define " + str(name_map[i]) + "_ADDR " + str(i) + "\n")

    fout.write("\n\n//write registers\n")
    for i in range(len(name_map)):
        if (type_map[i] == "`W_TYP" or type_map[i] == "`RW_TYP"):
            fout.write("`REG_ARE(clk, rst, " + str(init_val_map[i]) + ", valid & wstrb & (address == " + str(i) + "), " + str(name_map[i]) + ", wdata[" + str(width_map[i]) + "-1:0])\n")
            pass
        pass
    for i in range(len(bank_map)):
        if (type_map[i] == "`BANKW_TYP"):
            fout.write("`REG_ARE(clk, rst, " + str(init_val_map[i]) + ", valid & wstrb & (address == " + str(i) + "), " + str(bank_map[i]) + ", wdata[" + str(width_map[i]) + "-1:0])\n")
            pass
        pass

    fout.write("\n\n//read registers\n")
    fout.write("`SIGNAL(rdata_int, DATA_W)\n")
    fout.write("`SIGNAL2OUT(rdata, rdata_int)\n\n")

    fout.write("always @* begin\n")
    fout.write("   rdata_int = DATA_W'd0;\n")
    fout.write("   case(address)\n")
    for i in range(len(name_map)):
        if (type_map[i] == "`R_TYP" or type_map[i] == "`RW_TYP"):
            fout.write("     " + str(i) + ": rdata_int = " + str(name_map[i]) + " | DATA_W'd0;\n")
            pass
        pass
    for i in range(len(name_map)):
        if (type_map[i] == "`BANKR_TYP"):
            fout.write("     " + str(i) + ": rdata_int = " + str(bank_map[i]) + " | DATA_W'd0;\n")
            pass
        pass
    for i in range(len(name_map)):
        if (type_map[i] == "`CUBER_TYP"):
            fout.write("     " + str(i) + ": rdata_int = " + str(cube_map[i]) + " | DATA_W'd0;\n")
            pass
        pass

    fout.write("     default: rdata_int = DATA_W'd0;\n")
    fout.write("   endcase\n")
    fout.write("end\n")

    fout.close()
    return

def write_weights(name_map, width_map):
    global infile
    fout = open(infile+'_w.vh', 'w')

    fout.write("//This file was generated by script swreg2regmap.py\n\n")

    fout.write("\n//registers width\n")
    for i in range(len(name_map)):
        fout.write("`define " + str(name_map[i]) + "_W " + str(width_map[i]) + "\n")

    fout.close()
    return

def write_h(name_map):
    global infile
    fout = open(infile+'.h', 'w')

    fout.write("//This file was generated by script swreg2regmap.py\n\n")
    fout.write("//register address mapping\n")
    for i in range(len(name_map)):
        fout.write("#define " + str(name_map[i]) + " " + str(i) + "\n")

    fout.close()
    return

def write_w_bank(bank_map,bank_width_map,cube_map,cube_width_map):
    global infile
    fout = open(infile+'_w.vh', 'a+')

    fout.write("//This file was generated by script swreg2regmap.py\n\n")
    fout.write("//Register Bank Addressing\n")
    for i in range(len(bank_map)):
        fout.write("`define " + str(bank_map[i]) + " " + str(bank_width_map[i]) + "\n")
    for i in range(len(cube_map)):
        fout.write("`define " + str(cube_map[i]) + " " + str(cube_width_map[i]) + "\n")

    fout.close()
    return




def swreg_parse (program, hwsw):
    name_map = []
    width_map = []
    init_val_map = []
    type_map = []
    bank_map =[]
    bank_width_map =[]
    cube_map =[]
    cube_width_map =[]

    for line in program :
        if line.startswith("//"): continue #commented line

        subline = re.sub('\[|\]|:|,|//|\;',' ', line)
        subline = re.sub('\(',' ',subline, 1)
        subline = re.sub('\)',' ', subline, 1)

        flds = subline.split()
        if not flds : continue #empty line
        #print flds[0]
        if ('SWREG_' in flds[0]): #software accessible registers
            reg_name = flds[1] #register name
            reg_width = flds[2] #register width
            reg_init_val = flds[3] #register init val


            #register type
            if '_RW' in flds[0]:
                reg_type = '`RW_TYP'
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)
                bank_map.append("BLANK")
                bank_width_map.append("BLANK")
                cube_map.append("BLANK")
                cube_width_map.append("BLANK")

            elif '_W' in flds[0]:
                reg_type = '`W_TYP'
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)
                bank_map.append("BLANK")
                bank_width_map.append("BLANK")
                cube_map.append("BLANK")
                cube_width_map.append("BLANK")

            elif '_BANKR' in flds[0]:
                reg_n_elems = flds[4]
                reg_type = '`BANKR_TYP'
                for i in range(int(reg_n_elems)-1):
                    name_map.append(reg_name+str(i))
                    bank_map.append(reg_name+"["+str(i)+"]")
                    bank_width_map.append('['+reg_width+ "*"+str(i+1)+"-1"+':'+reg_width+"*"+str(i)+']')
                    width_map.append(reg_width)
                    init_val_map.append(reg_init_val)
                    type_map.append(reg_type)
                    cube_map.append("BLANK")
                    cube_width_map.append("BLANK")
                bank_map.append(reg_name +"["+str(i+1)+"]")
                reg_name = reg_name+str(i+1)
                bank_width_map.append('['+reg_width+ "*"+str(i+2)+"-1"+':'+reg_width+"*"+str(i+1)+']')
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)
                cube_map.append("BLANK")
                cube_width_map.append("BLANK")

            elif '_BANKW' in flds[0]:
                reg_n_elems = flds[4]
                reg_type = '`BANKW_TYP'
                for i in range(int(reg_n_elems)-1):
                    name_map.append(reg_name+str(i))
                    bank_map.append(reg_name+"["+str(i)+"]")
                    bank_width_map.append('['+reg_width+ "*"+str(i+1)+"-1"+':'+reg_width+"*"+str(i)+']')
                    width_map.append(reg_width)
                    init_val_map.append(reg_init_val)
                    type_map.append(reg_type)
                    cube_map.append("BLANK")
                    cube_width_map.append("BLANK")
                bank_map.append(reg_name +"["+str(i+1)+"]")
                reg_name = reg_name+str(i+1)
                bank_width_map.append('['+reg_width+ "*"+str(i+2)+"-1"+':'+reg_width+"*"+str(i+1)+']')
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)
                cube_map.append("BLANK")
                cube_width_map.append("BLANK")

            elif '_CUBER' in flds[0]:
                reg_type = '`CUBER_TYP'
                cube_nelements = flds[4]
                cube_nlength =flds[5]
                for i in range(int(cube_nelements)):
                    for j in range(int(cube_nlength)):
                        cube_map.append(reg_name+"["+str(i)+"]"+"["+str(j)+"]")
                        cube_width_map.append('['+reg_width+ "*"+str(i*int(cube_nlength)+j+1)+"-1"+':'+reg_width+"*"+str(i*int(cube_nlength)+j)+']')
                        width_map.append(reg_width)
                        init_val_map.append(reg_init_val)
                        type_map.append(reg_type)
                        name_map.append(reg_name+str(i)+str(j))
                        bank_map.append("BLANK")
                        bank_width_map.append("BLANK")
            else:
                reg_type = '`R_TYP'
                name_map.append(reg_name)
                width_map.append(reg_width)
                init_val_map.append(reg_init_val)
                type_map.append(reg_type)
                bank_map.append("BLANK")
                bank_width_map.append("BLANK")
                cube_map.append("BLANK")
                cube_width_map.append("BLANK")
        else: continue #not a recognized macro

    if(hwsw == "HW"):
        write_mapping(name_map, width_map, init_val_map, type_map, bank_map, cube_map)
        write_weights(name_map, width_map)
        write_w_bank(bank_map,bank_width_map,cube_map,cube_width_map)
    elif(hwsw == "SW"):

        write_h(name_map)

    return

def main () :

    global infile

    #parse command line
    if len(sys.argv) != 3:
        print("Usage: ./mkregs.py infile [HW/SW]")
        quit()
    else:
        infile = sys.argv[1]
        hwsw = sys.argv[2]

    #parse input file
    fin = open (infile, 'r')
    program = fin.readlines()
    fin.close()

    infile = infile.split('/')[-1].split('.')[0]

    swreg_parse (program, hwsw)

if __name__ == "__main__" : main ()
