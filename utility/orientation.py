import math

#TODO improve, look at orientation class in testbot
def rotator_to_matrix(obj):
    r = obj.rotation
    CR = math.cos(r.z)
    SR = math.sin(r.z)
    CP = math.cos(r.x)
    SP = math.sin(r.x)
    CY = math.cos(r.y)
    SY = math.sin(r.y)

    matrix = list()
    matrix.append(myVec3(CP*CY, CP*SY, SP))
    matrix.append(myVec3(CY*SP*SR - CR*SY, SY*SP*SR + CR*CY, -CP*SR))
    matrix.append(myVec3(-CR*CY*SP - SR*SY, -CR*SY*SP + SR*CY, CP*CR))

    return matrix
