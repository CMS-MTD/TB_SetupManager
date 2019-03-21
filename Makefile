PROJECT = OTSDAQInterface
OBJDIR  = obj
INCDIR  = .
SRCDIR  = .
LIBDIR  = lib
SRCEXT  = cc
CC      = g++
SOFLAGS = -shared
MKDIR_P = mkdir -p

OUT_DIR = ${LIBDIR} ${OBJDIR}

INCFLAGS = -I$(INCDIR)
CCFLAGS     = -std=c++0x -fPIC -Werror -Wall $(INCFLAGS)


DYNLIB  = $(LIBDIR)/lib$(PROJECT).so

LDLIBS += -L$(LIBDIR) $(DYNLIB)

SRCLIST   = $(filter-out $(SRCDIR)/$(PROJECT).$(SRCEXT), $(wildcard $(SRCDIR)/*.$(SRCEXT)))
OBJLIST   = $(patsubst $(SRCDIR)/%.$(SRCEXT),$(OBJDIR)/%.o,$(SRCLIST))

#.PHONY: directories

#----------------- Main sequence ----------------------#
all : bin
#------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------#
directories: ${OUT_DIR}
#--------------------------------------------------------------------------------------------------------#
${OUT_DIR}:
	${MKDIR_P} ${OUT_DIR}

#--------------------------------------------------------------------------------------------------------#
dep :
	@echo '     ***** Making main sequence $(OBJDIR)/dependencies.d *****'
	@if [ ! -e $(OBJDIR)/dependencies.d ] ; then touch $(OBJDIR)/dependencies.d ;fi
        ifdef CPPVERBOSE
	  $(CC) -MM $(INCDIR)/*.h $(SRCDIR)/*.$(SRCEXT)  $(CCFLAGS) | sed 's/.*\.o:/$(OBJDIR)\/&/' >  $(OBJDIR)/dependencies.d
        else
	 @$(CC) -MM $(INCDIR)/*.h $(SRCDIR)/*.$(SRCEXT)  $(CCFLAGS) | sed 's/.*\.o:/$(OBJDIR)\/&/' >  $(OBJDIR)/dependencies.d
        endif

#--------------------------------------------------------------------------------------------------------#
$(OBJDIR)/%.o : $(SRCDIR)/%.$(SRCEXT)
	@echo '     Compiling $<'
        ifdef CPPVERBOSE
	  $(CC) $(CCFLAGS) -c $< -o $@
        else
	 @$(CC) $(CCFLAGS) -c $< -o $@
        endif

#--------------------------------------------------------------------------------------------------------#
dynlib :  $(DYNLIB)
#--------------------------------------------------------------------------------------------------------#
$(DYNLIB) : $(OBJLIST)
	@echo '     ***** Making dynlib *****'
        ifdef CPPVERBOSE
	  $(CC) $(SOFLAGS) -o $(DYNLIB) $(OBJLIST)
        else
	 @$(CC) $(SOFLAGS) -o $(DYNLIB) $(OBJLIST)
        endif

#--------------------------------------------------------------------------------------------------------#
bin: ${PROJECT}.cc
        ifdef CPPVERBOSE
	   $(CC) -o ${PROJECT} $(CCFLAGS) $<
        else
	  @$(CC) -o ${PROJECT} $(CCFLAGS) $<
        endif

#--------------------------------------------------------------------------------------------------------#
clean:
	rm *~; rm $(OBJDIR)/*.o; rm $(LIBDIR)/*.so; rm $(OBJDIR)/dependencies.d; rm ${PROJECT};

#--------------------------------------------------------------------------------------------------------#
-include $(OBJDIR)/dependencies.d
