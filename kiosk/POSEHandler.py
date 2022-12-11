from dataTypes.pose_pb2 import *
from crypto import *
from surethingcore.loc_claim_pb2 import *
from surethingcore.loc_time_pb2 import *
from surethingcore.signature_pb2 import *
from surethingcore.loc_endorse_pb2 import *
from surethingcore.latlng_pb2 import *
from google.protobuf.timestamp_pb2 import *
 # all we need for the signed location claim
import uuid
import base64
import time

# The kiosk will be deployed in a known location
MY_LOCATION_LAT = 38.73787545779024
MY_LOCATION_LNG = -9.137825390556634
################################################
# The kiosk has a unique ID
# For now, we will call him KIOSK
KIOSK_ID = "KIOSK"

def POSEHandleMessage(bytes_string):
    """ 1. Create the Associated Data from the enc_structure skeleton
        2. Decrypt the ciphertext inside the PoseEncrypt0.body using the symmetric key
           and the AD. We will obtain the SignedLocationClaim
        3. Verify the Signature of the SignedLocationClaim (Signed by the prover)
        4. Endorse the Location Claim present in the SignedLocationClaim, by signing it and creating
           a SignedLocationEndorsement
        5. Send both LocationClaim and SignedLocationEndorsement to the Ledger
        """
    ############## 1. ##############
    enc_structure = Enc_Structure()

    enc_structure.ParseFromString(bytes_string)

    protected = HeaderMap()

    protected.ParseFromString(enc_structure.protected)
    value = Value()
    value = protected.map[6]

    body = PoseEncrypt0()

    body = enc_structure.body

    print(enc_structure)

    associated_data = generateAD(enc_structure)
    ################################

    ############## 2. ##############
    # now we just decrypt the ciphertext
    # it will internally load the pre-shared key and use the associated data to obtain the plaintext

    signedlocationClaim_bytes = aeadDecrypt(value.bstr, body.ciphertext, associated_data)

    # signed location claim - Location Claim + Signature
    ################################

    ############## 3. ##############

    signedLocationClaim = SignedLocationClaim()
    signedLocationClaim.ParseFromString(signedlocationClaim_bytes)
    print(signedLocationClaim)

    # we need to obtain the Signature object from it

    signature = Signature()
    signature = signedLocationClaim.proverSignature
    print(signature)

    # now to verify the signature we just need the actual signature and the Location Claim
    if not verifySignature(signature.value, signedLocationClaim.claim.SerializeToString()):
        print("Signatures do not match!")
        return

    # verification done, now we need to endorse this location claim
    ################################
    ############## 4. ##############

    signedLE = endorse(signedLocationClaim.claim)

    ################################
    ############## 5. ##############
    
    print(len(base64.b64encode(signedLE.SerializeToString())))
    print(base64.b64encode(signedLE.SerializeToString()))

    # Send to the ledger or display in a QR CODE
    return base64.b64encode(signedLE.SerializeToString())

    ################################


def endorse(location_claim):
    print("LOCATION CLAIM")
    print(location_claim)

    # Create the Location Endorsement
    # claimId is a uuid
    endorsement = LocationEndorsement(witnessId=KIOSK_ID, claimId=location_claim.claimId, time=Time(timestamp=Timestamp(seconds=round(time.time() * 1000))))
    # in the future, add photo as evidence

    # signature of this endorsement
    signature = sign(endorsement.SerializeToString())

    # Create the Signed Location Endorsement
    # Need to create the Signature object first
    # Nonce might be overkill
    
    return SignedLocationEndorsement(endorsement=endorsement, witnessSignature=Signature(value=signature, cryptoAlgo="RSA"))
    
    #Now send this to the Ledger
    #...





def generateAD(enc_structure):

    #Lets create an enc_structure skeleton for the AD
    skeleton_enc = Enc_Structure()

    skeleton_enc.context = enc_structure.context
    skeleton_enc.protected = enc_structure.protected

    # we also need to create an encrypt0 skeleton to be put inside the enc skeleton
    skeleton_encrypt0 = PoseEncrypt0()

    body = enc_structure.body

    skeleton_encrypt0.protected = body.protected
    #skeleton_encrypt0.unprotected.CopyFrom(body.unprotected)
    # since it is only a skeleton, we do not need the ciphertext

    skeleton_enc.body.CopyFrom(skeleton_encrypt0)


    print(skeleton_enc)
    return skeleton_enc.SerializeToString()

def createLocationClaim(proverId):

    latlng = LatLng()
    latlng.latitude = MY_LOCATION_LAT
    latlng.longitude = MY_LOCATION_LNG

    location = Location(latLng= latlng)

    timestamp = Timestamp(seconds=round(time.time() * 1000)) # current time in milliseconds

    proto_time = Time(timestamp=timestamp)

    return LocationClaim(proverId=proverId, claimId=str(uuid.uuid4()), location=location, time=proto_time)



