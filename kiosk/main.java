import pteidlib.PTEID_ADDR;
import pteidlib.PTEID_Certif;
import pteidlib.PTEID_ID;
import pteidlib.PTEID_PIC;
import pteidlib.PTEID_Pin;
import pteidlib.PTEID_TokenInfo;
import pteidlib.PteidException;
import pteidlib.pteid;

import java.io.FileOutputStream;
import java.nio.charset.Charset;
import java.lang.reflect.Method;
import javax.crypto.*;

import java.io.IOException;

import java.io.ByteArrayInputStream;
import java.io.InputStream;

import java.security.cert.CertificateException;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

import pt.gov.cartaodecidadao.*;

public class main{
    public static void main(String[] args){

        String[] s = readCard();
        if(s == null){
            System.out.println("null");
        }
        else{
            System.out.println(s[0] + '|' +  s[1]);
        }
    }

    public static String[] readCard() {
        String[] fields = new String[2];
        while(true){
            try {
                Thread.sleep(1000);
                System.loadLibrary("pteidlibj");
                PTEID_ReaderSet.initSDK(); //initiate the middleware

                PTEID_EIDCard card;
                PTEID_ReaderContext context;
                PTEID_ReaderSet readerSet;
                readerSet = PTEID_ReaderSet.instance();
                for (int i = 0; i < readerSet.readerCount(); i++) {
                    context = readerSet.getReaderByNum(i);
                    if (context.isCardPresent()) {
                        card = context.getEIDCard();
                        PTEID_EId eid = card.getID();
                        fields[0] = eid.getGivenName() + ' ' + eid.getSurname(); //fullname
                        fields[1] = eid.getDocumentNumber();  //CCnumber
                        //System.out.println(eid.getCardAuthKeyObj());
                        PTEID_ReaderSet.releaseSDK(); //terminate the middleware
                        return fields;
                    }
                    else{
                        //PTEID_ReaderSet.releaseSDK(); //terminate the middleware
                        //return null;
                    }
                }
            }catch(Throwable e) {
                System.out.println(e.getMessage());
            }
        }
    }
}
