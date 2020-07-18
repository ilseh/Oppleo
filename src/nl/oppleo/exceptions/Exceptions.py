# 
class DbException(Exception):
   pass

class ExpiredException(Exception):
    pass

class NotAuthorizedException(Exception):
    pass

class OtherRfidHasOpenSessionException(Exception):
    pass
