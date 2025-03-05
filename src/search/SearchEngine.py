class SearchEngine:
    STATE_INIT = 0
    STATE_BUILDING = 1
    STATE_BUILD_FAILED = 2
    STATE_BUILD_COMPLETE = 3
    STATE_INFERENCE = 4
    
    def __init__(self):
        self.engine_state = self.STATE_INIT
        self.err_msg = ""