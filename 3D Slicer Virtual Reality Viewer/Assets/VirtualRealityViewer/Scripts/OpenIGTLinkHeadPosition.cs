using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
//using System.Runtime.InteropServices;

public class OpenIGTLinkHeadPosition : MonoBehaviour {

    public string ipString = "127.0.0.1";
    public int port = 18944;
    public GameObject OculusTransform;

    private float testX = 0.2f;
    private float testY = 0.2f;
    private float testZ = 0.2f;

    private float totalTime = 0f;

    // Header information:
    // Version 1
    // Type Transform
    // Device Name OculusRiftPosition
    // Time 0
    // Body size 30 bytes
    private string hexHeader = "00015452414E53464F524D0000004F63756C757352696674506F736974696F6E000000000000000000000000000000000030";
    //CRC ECMA-182
    private CRC64 crcGenerator;
    private string CRC;
    private string crcPolynomialBinary = "10100001011110000111000011110101110101001111010100011011010010011";
    private ulong crcPolynomial;
    //Identity matrix without translation
    private string bodyHeader = "3F8000000000000000000000000000003F8000000000000000000000000000003F800000";
    private string body;

    private Socket sender;
    private IPEndPoint remoteEP;

    // Use this for initialization
    void Start () {
        crcGenerator = new CRC64();
        crcPolynomial = Convert.ToUInt64(crcPolynomialBinary, 2);
        crcGenerator.Init(crcPolynomial);



        //byte[] bytes = new byte[1024];
        try
        {
            // Establish the remote endpoint for the socket.
            // This example uses port 11000 on the local computer.
            IPAddress ipAddress = IPAddress.Parse(ipString);
            remoteEP = new IPEndPoint(ipAddress, 18944);

            // Create a TCP/IP  socket.
            sender = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

            try
            {
                // Connect the socket to the remote endpoint. Catch any errors.
                sender.Connect(remoteEP);
            }
            catch (ArgumentNullException ane)
            {
                Console.WriteLine("ArgumentNullException : {0}", ane.ToString());
            }
            catch (SocketException se)
            {
                Console.WriteLine("SocketException : {0}", se.ToString());
            }
            catch (Exception e)
            {
                Console.WriteLine("Unexpected exception : {0}", e.ToString());
            }
        }
        catch (Exception e)
        {
            Console.WriteLine(e.ToString());
        }
    }

    // Update is called once per frame
    void Update()
    {
        // Repeat once every 10 seconds
        if (totalTime * 1000 > 50)
        {
            string xHex;
            string yHex;
            string zHex;
            float x = OculusTransform.transform.position.x;
            float y = OculusTransform.transform.position.y;
            float z = OculusTransform.transform.position.z;
            
            byte[] xBytes = BitConverter.GetBytes(x*10);
            byte[] yBytes = BitConverter.GetBytes(y*10);
            byte[] zBytes = BitConverter.GetBytes(z*10);
            
            if (BitConverter.IsLittleEndian)
            {
              Array.Reverse(xBytes);
              Array.Reverse(yBytes);
              Array.Reverse(zBytes);         
            }
            xHex = BitConverter.ToString(xBytes).Replace("-","");
            yHex = BitConverter.ToString(yBytes).Replace("-","");
            zHex = BitConverter.ToString(zBytes).Replace("-","");

            body = bodyHeader + xHex + yHex + zHex;

            ulong crcULong = crcGenerator.Compute(StringToByteArray(body), 0, 0);
            CRC = crcULong.ToString("X16");

            string hexmsg = hexHeader + CRC + body;

            // Encode the data string into a byte array.
            byte[] msg = StringToByteArray(hexmsg);

            // Send the data through the socket.
            int bytesSent = sender.Send(msg);
            print(bytesSent);

            // Reset timer
            totalTime = 0f;
        }
        totalTime = totalTime + Time.deltaTime;
    }

    void OnApplicationQuit()
    {
        // Release the socket.
        sender.Shutdown(SocketShutdown.Both);
        sender.Close();
    }

    static byte[] StringToByteArray(string hex)
    {
        byte[] arr = new byte[hex.Length >> 1];

        for (int i = 0; i < hex.Length >> 1; ++i)
        {
            arr[i] = (byte)((GetHexVal(hex[i << 1]) << 4) + (GetHexVal(hex[(i << 1) + 1])));
        }

        return arr;
    }

    static int GetHexVal(char hex)
    {
        int val = (int)hex;
        //For uppercase A-F letters:
        return val - (val < 58 ? 48 : 55);
        //For lowercase a-f letters:
        //return val - (val < 58 ? 48 : 87);
    }

}


public class CRC64
{
    private ulong[] _table;

    private ulong CmTab(int index, ulong poly)
    {
        ulong retval = (ulong)index;
        ulong topbit = (ulong)1L << (64 - 1);
        ulong mask = 0xffffffffffffffffUL;

        retval <<= (64 - 8);
        for (int i = 0; i < 8; i++)
        {
            if ((retval & topbit) != 0)
                retval = (retval << 1) ^ poly;
            else
                retval <<= 1;
        }
        return retval & mask;
    }

    private ulong[] GenStdCrcTable(ulong poly)
    {
        ulong[] table = new ulong[256];
        for (var i = 0; i < 256; i++)
            table[i] = CmTab(i, poly);
        return table;
    }

    private ulong TableValue(ulong[] table, byte b, ulong crc)
    {
        return table[((crc >> 56) ^ b) & 0xffUL] ^ (crc << 8);
    }

    public void Init(ulong poly)
    {
        _table = GenStdCrcTable(poly);
    }

    public ulong Compute(byte[] bytes, ulong initial, ulong final)
    {
        ulong current = initial;
        for (var i = 0; i < bytes.Length; i++)
        {
            current = TableValue(_table, bytes[i], current);
        }
        return current ^ final;

    }
}
