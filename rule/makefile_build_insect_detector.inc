
BUILD_ALL += $(OUT_DIR)/insect_detector

$(OUT_DIR)/insect_detector : \
					$(OUT_OBJ_DIR)/insect_detector.o \
					libacc_detector_presence.a \
					libacconeer.a \
					libcustomer.a \

	@echo "    Linking $(notdir $@)"
	$(SUPPRESS)$(LINK.o) -Wl,--start-group $^ -Wl,--end-group $(LDLIBS) -o $@
