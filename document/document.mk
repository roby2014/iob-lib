SHELL = /bin/bash

LIB_DOC_DIR:=$(LIB_DIR)/document
LIB_SW_DIR:=$(LIB_DIR)/software
LIB_SW_PYTHON_DIR:=$(LIB_SW_DIR)/python

$(DOC).pdf: fpga_res figures $(DOC)top.tex
ifeq ($(DOC),pb)
	make -C ./figures pb_figs
endif
ifeq ($(DOC),ug)
	make -C ./figures ug_figs
	echo $(VERSION) > version.tex
	git rev-parse --short HEAD > shortHash.tex
endif
	pdflatex -jobname $(DOC) $(DOC)top.tex
	if [ -f *.bib ]; then bibtex ug; fi
	pdflatex -jobname $(DOC) $(DOC)top.tex
	pdflatex -jobname $(DOC) $(DOC)top.tex

.PHONY: view texfiles figures fpga_res clean

view: $(DOC).pdf
	evince $< &

$(DOC)top.tex: texfiles
	echo "\def\TEX{$(LIB_DOC_DIR)}" > $(DOC)top.tex
	if [ -f vivado.tex ]; then echo "\def\XILINX{Y}" >> $(DOC)top.tex; fi
	if [ -f quartus.tex ]; then echo "\def\INTEL{Y}" >> $(DOC)top.tex; fi
	if [ -f asic.tex ]; then echo "\def\ASIC{Y}" >> $(DOC)top.tex; fi
	if [ -f sm_tab.tex ]; then echo "\def\SMP{Y} \def\SM{Y}" >> $@; fi
	if [ -f sp_tab.tex ]; then echo "\def\SMP{Y} \def\SP{Y}" >> $@; fi
	if [ -f swreg.tex ]; then echo "\def\SW{Y}" >> $@; fi
	if [ -f custom.tex ]; then echo "\def\CUSTOM{Y}" >> $@; fi
	if [ -f td.tex ]; then echo "\def\TD{Y}" >> $@; fi
	echo "\input{$(LIB_DOC_DIR)/$(DOC)/$(DOC).tex}" >> $(DOC)top.tex

#tex files extracted from code comments
texfiles: $(MACRO_LIST)
	$(LIB_SW_PYTHON_DIR)/verilog2tex.py $(CORE_DIR)/hardware/src/$(TOP_MODULE).v $(VHDR) $(VSRC)


#FPGA implementation results
fpga_res: vivado.tex quartus.tex

VIVADOLOG = $(CORE_DIR)/hardware/fpga/vivado/$(XIL_FAMILY)/vivado.log
QUARTUSLOG = $(CORE_DIR)/hardware/fpga/quartus/$(INT_FAMILY)/quartus.log

vivado.tex: $(VIVADOLOG)
	cp $(VIVADOLOG) .; LOG=$< $(LIB_SW_DIR)/vivado2tex.sh

quartus.tex: $(QUARTUSLOG)
	cp $(QUARTUSLOG) .; LOG=$< $(LIB_SW_DIR)/quartus2tex.sh

$(VIVADOLOG):
	make  -C $(CORE_DIR) fpga-build FPGA_FAMILY=$(XIL_FAMILY)

$(QUARTUSLOG):
	make  -C $(CORE_DIR) fpga-build FPGA_FAMILY=$(INT_FAMILY)

#cleaning
clean:
	@find . -type f -not \( $(NOCLEAN) \) -delete
	@rm -rf figures $(DOC)top.tex
	@rm -rf $(LIB_SW_PYTHON_DIR)/__pycache__/ $(LIB_SW_PYTHON_DIR)/*.pyc
