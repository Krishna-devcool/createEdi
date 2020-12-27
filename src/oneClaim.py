from src.createEdi import CreateEdi

class ClaimGenerator(CreateEdi):

    def __init__(self):
        self.seg_delimiter = None
        self.ele_delimiter = None
        self.claim_list = list()
    
    def get_claim_list(self, data):
        self.Loop_ISA(data)
        return self.claim_list

    def Loop_ISA(self, data):
        assert data is not None
        for isa in data:
            self.setDelmiters(isa.get("EDI_delimiters"))
            head = self.createSegments(isa.get("LOOP_segments"))
            tail = self.getLoopSegments(isa, "has_iea")
            self.Loop_GS(isa.get("has_loop_gs"), head, tail)

    
    def Loop_GS(self, data, header = "", footer = ""):
        assert data is not None
        for gs in data:
            head = header + self.createSegments(gs.get("LOOP_segments"))
            tail = self.getLoopSegments(gs, "has_ge") + footer
            self.Loop_ST(gs.get("has_loop_st"), head, tail)        

    
    def Loop_ST(self, data, header = "", footer = ""):
        assert data is not None
        for st in data:
            head = header + self.createSegments(st.get("LOOP_segments")) + \
                self.getLoopSegments(st, "has_loop_1000a_submitter_name") + \
                self.getLoopSegments(st, "has_loop_1000b_receiver_name")
            tail = self.getLoopSegments(st, "has_se") + footer
            self.Loop_2000A_BILLING_PROVIDER_HIERARCHICAL_LEVEL(st.get("has_loop_2000a_billing_provider_hierarchical_level"), head, tail)

    
    def Loop_2000A_BILLING_PROVIDER_HIERARCHICAL_LEVEL(self, data, header = "", footer = ""):
        assert data is not None
        for hl20 in data:
            head = header + self.createSegments(hl20.get("LOOP_segments")) + \
                self.getLoopSegments(hl20, "has_loop_2010aa_billing_provider_name") + \
                self.getLoopSegments(hl20, "has_loop_2010ab_pay_to_address_name") + \
                self.getLoopSegments(hl20, "has_loop_2010ac_pay_to_plan_name")
            self.Loop_2000B_SUBSCRIBER_HIERARCHICAL_LEVEL(hl20.get("has_loop_2000b_subscriber_hierarchical_level"), head, footer)

    
    def Loop_2000B_SUBSCRIBER_HIERARCHICAL_LEVEL(self, data, header = "", footer = ""):
        assert data is not None
        for hl22 in data:
            head = header + self.createSegments(hl22.get("LOOP_segments")) + \
                self.getLoopSegments(hl22, "has_loop_2010ba_subscriber_name") + \
                self.getLoopSegments(hl22, "has_loop_2010bb_payer_name")

            if hl22.get("has_loop_2000c_patient_hierarchial_level") is None:
                self.Loop_2300_CLAIM_INFORMATION(hl22.get("has_loop_2300_claim_information"), head, footer)
            else:
                self.Loop_2000C_PATIENT_HIERARCHIAL_LEVEL(hl22.get("has_loop_2000c_patient_hierarchial_level"), head, footer)

    
    def Loop_2000C_PATIENT_HIERARCHIAL_LEVEL(self, data, header = "", footer = ""):
        assert data is not None
        for hl23 in data:
            head = header + self.createSegments(hl23.get("LOOP_segments")) + \
                self.getLoopSegments(hl23, "has_loop_2010ca_patient_name")
            self.Loop_2300_CLAIM_INFORMATION(hl23.get("has_loop_2300_claim_information"), head, footer)

    
    
    def Loop_2300_CLAIM_INFORMATION(self, data, header = "", footer = ""):
        assert data is not None
        sub_loops_keys = ["has_loop_2310a_referring_provider_name", "has_loop_2310b_rendering_provider_name", "has_loop_2310c_service_facility_location_name", \
            "has_loop_2310d_supervising_provider_name", "has_loop_2310e_ambulance_pick_up_location", "has_loop_2310f_ambulance_drop_off_location"]
        for clm in data:
            claim = header
            claim += self.createSegments(clm.get("LOOP_segments"))
            for loop_key in sub_loops_keys:
                claim += self.getLoopSegments(clm, loop_key)
            try:
                claim += self.Loop_2320_OTHER_SUBSCRIBER_INFORMATION(clm.get("has_loop_2320_other_subscriber_information"))
            except:
                pass

            try:
                claim += self.Loop_2400_SERVICE_LINE_NUMBER(clm.get("has_loop_2400_service_line_number"))
            except:
                pass
            self.claim_list.append(claim + footer)