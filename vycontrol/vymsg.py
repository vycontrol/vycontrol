
import pprint


class msg:
    TYPES               = (
        'error',        # some really bad happened
        'success',      # its everything fine
        'alert',        # alert, you must pay attention
        'info',         # just information
    )

    msgs                = []

    def __init__(self):
        pass

    def add(self, t, m):
        if t in self.TYPES:
            self.msgs.append({
                "msg_type":     t,
                "msg":          m     
            })
    
    def add_error(self, m):
        self.add('error', m)

    def add_success(self, m):
        self.add('success', m)

    def add_alert(self, m):
        self.add('alert', m)
    
    def add_info(self, m):
        self.add('info', m)        

    def get_all(self):
        return self.msgs



def log(area, value = [], end = True):
    print("\n\n")
    print("######################## START LOG " + area.upper())
    pprint.pprint(value, indent=4, width=160) 

    if end == True:
        print("######################## END LOG " + area.upper())
    print("\n\n")
