# Can NOT be an enum
class GWDCObjectType:
    # Object is a normal object run by the system
    NORMAL = 0
    # Object was created by uploading files
    UPLOADED = 1
    # Object is from an external source
    EXTERNAL = 2
