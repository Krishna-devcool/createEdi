from ast import literal_eval

class CreateEdi(object):

    def __init__(self):
        self.seg_delimiter = None
        self.ele_delimiter = None
        self.comp_delimiter = None

    def createSegments(self, data):
        data = literal_eval(data)
        edi = ""
        for seg in data:
            edi += self.ele_delimiter.join(seg) + self.seg_delimiter
        return edi
    
    def getLoopSegments(self, data, key):
        edi = ""
        try:
            for loop in data.get(key):
                edi += self.createSegments(loop.get("LOOP_segments"))
        except:
            pass

        return edi

    def setDelmiters(self, delimiters):
        self.seg_delimiter, self.ele_delimiter, self.comp_delimiter = delimiters[0], delimiters[1], delimiters[3]

    def Loop_ISA(self, data):
        assert data is not None
        edi = ""
        for isa in data:
            self.setDelmiters(isa.get("EDI_delimiters"))
            edi = self.createSegments(isa.get("LOOP_segments")) + \
                self.Loop_GS(isa.get("has_loop_gs")) + \
                self.getLoopSegments(isa, "has_iea")
        return edi

    
    def Loop_GS(self, data):
        assert data is not None
        edi = ""
        for gs in data:
            edi = self.createSegments(gs.get("LOOP_segments")) + \
                self.Loop_ST(gs.get("has_loop_st")) + \
                self.getLoopSegments(gs, "has_ge")

        return edi
        

    
    def Loop_ST(self, data):
        assert data is not None
        st_edi = dict()
        for st in data:
            st_level = int(st.get("Transaction Set Control Number"))
            st_data = self.createSegments(st.get("LOOP_segments")) + \
                self.getLoopSegments(st, "has_loop_1000a_submitter_name") + \
                self.getLoopSegments(st, "has_loop_1000b_receiver_name") + \
                self.Loop_2000A_BILLING_PROVIDER_HIERARCHICAL_LEVEL(st.get("has_loop_2000a_billing_provider_hierarchical_level")) + \
                self.getLoopSegments(st, "has_se")
            st_edi[st_level] = st_data
        
        edi = ""
        for i in sorted(st_edi.keys()):
            edi += st_edi[i]

        return edi

    
    def Loop_2000A_BILLING_PROVIDER_HIERARCHICAL_LEVEL(self, data):
        assert data is not None
        hl20_edi = dict()
        for hl20 in data:
            hl20_level = int(hl20.get("Hierarchical ID Number"))
            hl20_data = self.createSegments(hl20.get("LOOP_segments")) + \
                self.getLoopSegments(hl20, "has_loop_2010aa_billing_provider_name") + \
                self.getLoopSegments(hl20, "has_loop_2010ab_pay_to_address_name") + \
                self.getLoopSegments(hl20, "has_loop_2010ac_pay_to_plan_name") + \
                self.Loop_2000B_SUBSCRIBER_HIERARCHICAL_LEVEL(hl20.get("has_loop_2000b_subscriber_hierarchical_level"))

            hl20_edi[hl20_level] = hl20_data

        edi = ""
        for i in sorted(hl20_edi.keys()):
            edi += hl20_edi[i]

        return edi

    
    def Loop_2000B_SUBSCRIBER_HIERARCHICAL_LEVEL(self, data):
        assert data is not None
        hl22_edi = dict()
        for hl22 in data:
            hl22_level = int(hl22.get("Hierarchical ID Number"))
            hl22_data = self.createSegments(hl22.get("LOOP_segments")) + \
                self.getLoopSegments(hl22, "has_loop_2010ba_subscriber_name") + \
                self.getLoopSegments(hl22, "has_loop_2010bb_payer_name")

            if hl22.get("has_loop_2000c_patient_hierarchial_level") is None:
                hl22_data += self.Loop_2300_CLAIM_INFORMATION(hl22.get("has_loop_2300_claim_information"))
            else:
                hl22_data += self.Loop_2000C_PATIENT_HIERARCHIAL_LEVEL(hl22.get("has_loop_2000c_patient_hierarchial_level"))

            hl22_edi[hl22_level] = hl22_data
        
        edi = ""
        for i in sorted(hl22_edi.keys()):
            edi += hl22_edi[i]

        return edi


    
    def Loop_2000C_PATIENT_HIERARCHIAL_LEVEL(self, data):
        assert data is not None
        hl23_edi = dict()
        for hl23 in data:
            hl23_level = int(hl23.get("Hierarchical ID Number"))
            hl23_data = self.createSegments(hl23.get("LOOP_segments")) + \
                self.getLoopSegments(hl23, "has_loop_2010ca_patient_name") + \
                self.Loop_2300_CLAIM_INFORMATION(hl23.get("has_loop_2300_claim_information"))

            hl23_edi[hl23_level] = hl23_data
        
        edi = ""
        for i in sorted(hl23_edi.keys()):
            edi += hl23_edi[i]

        return edi


    
    def Loop_2300_CLAIM_INFORMATION(self, data):
        assert data is not None
        edi = ""
        sub_loops_keys = ["has_loop_2310a_referring_provider_name", "has_loop_2310b_rendering_provider_name", "has_loop_2310c_service_facility_location_name", \
            "has_loop_2310d_supervising_provider_name", "has_loop_2310e_ambulance_pick_up_location", "has_loop_2310f_ambulance_drop_off_location"]
        for clm in data:
            edi += self.createSegments(clm.get("LOOP_segments"))
            for loop_key in sub_loops_keys:
                edi += self.getLoopSegments(clm, loop_key)
            try:
                edi += self.Loop_2320_OTHER_SUBSCRIBER_INFORMATION(clm.get("has_loop_2320_other_subscriber_information"))
            except:
                pass

            try:
                edi += self.Loop_2400_SERVICE_LINE_NUMBER(clm.get("has_loop_2400_service_line_number"))
            except:
                pass

        return edi

    def Loop_2320_OTHER_SUBSCRIBER_INFORMATION(self, data):
        assert data is not None
        edi = ""
        sub_loops_keys = ["has_loop_2330a_other_subscriber_name", "has_loop_2330b_other_payer_name", "has_loop_2330c_other_payer_referring_provider", \
            "has_loop_2330d_other_payer_rendering_provider", "has_loop_2330e_other_payer_serive_facility_location", "has_loop_2330f_other_payer_supervising_provider", \
            "has_loop_2330g_other_payer_billing_provider"]
        for loop_2320 in data:
            edi += self.createSegments(loop_2320.get("LOOP_segments"))
            for loop_key in sub_loops_keys:
                edi += self.getLoopSegments(loop_2320, loop_key)

        return edi

    def Loop_2400_SERVICE_LINE_NUMBER(self, data):
        assert data is not None
        lx_edi = dict()
        sub_loops_keys = ["has_loop_2410_drug_identification", "has_loop_2420a_rendering_provider_name", "has_loop_2420b_purchased_service_provider_name" \
            "has_loop_2420c_service_facility_location_name", "has_loop_2420d_supervising_provider_name", "has_loop_2420e_ordering_provider_name" \
            "has_loop_2420f_referring_provider_name", "has_loop_2420g_ambulance_pick_up_location", "has_loop_2420h_ambulance_drop_off_location", \
            "has_loop_2430_line_adjudication_information", "has_loop_2440_form_identification_code"]
        for lx in data:
            lx_level = int(lx.get("Assigned Number"))
            lx_data = self.createSegments(lx.get("LOOP_segments"))
            for loop_key in sub_loops_keys:
                lx_data += self.getLoopSegments(lx, loop_key)

            lx_edi[lx_level] = lx_data

        edi = ""
        for i in sorted(lx_edi.keys()):
            edi += lx_edi[i]

        return edi
