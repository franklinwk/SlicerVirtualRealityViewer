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
    public int msDelay = 200;

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
        if (totalTime * 1000 > msDelay)
        {
            string m00Hex;
            string m01Hex;
            string m02Hex;
            string m03Hex;
            string m10Hex;
            string m11Hex;
            string m12Hex;
            string m13Hex;
            string m20Hex;
            string m21Hex;
            string m22Hex;
            string m23Hex;

            Matrix4x4 matrix = Matrix4x4.TRS(OculusTransform.transform.localPosition, OculusTransform.transform.localRotation, OculusTransform.transform.localScale);

            float m00 = matrix.GetRow(0)[0];
            byte[] m00Bytes = BitConverter.GetBytes(m00);
            float m01 = matrix.GetRow(0)[1];
            byte[] m01Bytes = BitConverter.GetBytes(m01);
            float m02 = matrix.GetRow(0)[2];
            byte[] m02Bytes = BitConverter.GetBytes(m02);
            float m03 = matrix.GetRow(0)[3];
            byte[] m03Bytes = BitConverter.GetBytes(m03 * 10);

            float m10 = matrix.GetRow(1)[0];
            byte[] m10Bytes = BitConverter.GetBytes(m10);
            float m11 = matrix.GetRow(1)[1];
            byte[] m11Bytes = BitConverter.GetBytes(m11);
            float m12 = matrix.GetRow(1)[2];
            byte[] m12Bytes = BitConverter.GetBytes(m12);
            float m13 = matrix.GetRow(1)[3];
            byte[] m13Bytes = BitConverter.GetBytes(m13 * 10);

            float m20 = matrix.GetRow(2)[0];
            byte[] m20Bytes = BitConverter.GetBytes(m20);
            float m21 = matrix.GetRow(2)[1];
            byte[] m21Bytes = BitConverter.GetBytes(m21);
            float m22 = matrix.GetRow(2)[2];
            byte[] m22Bytes = BitConverter.GetBytes(m22);
            float m23 = matrix.GetRow(2)[3];
            byte[] m23Bytes = BitConverter.GetBytes(m23 * 10);

            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(m00Bytes);
                Array.Reverse(m01Bytes);
                Array.Reverse(m02Bytes);
                Array.Reverse(m03Bytes);
                Array.Reverse(m10Bytes);
                Array.Reverse(m11Bytes);
                Array.Reverse(m12Bytes);
                Array.Reverse(m13Bytes);
                Array.Reverse(m20Bytes);
                Array.Reverse(m21Bytes);
                Array.Reverse(m22Bytes);
                Array.Reverse(m23Bytes);
            }
            m00Hex = BitConverter.ToString(m00Bytes).Replace("-", "");
            m01Hex = BitConverter.ToString(m01Bytes).Replace("-", "");
            m02Hex = BitConverter.ToString(m02Bytes).Replace("-", "");
            m03Hex = BitConverter.ToString(m03Bytes).Replace("-", "");
            m10Hex = BitConverter.ToString(m10Bytes).Replace("-", "");
            m11Hex = BitConverter.ToString(m11Bytes).Replace("-", "");
            m12Hex = BitConverter.ToString(m12Bytes).Replace("-", "");
            m13Hex = BitConverter.ToString(m13Bytes).Replace("-", "");
            m20Hex = BitConverter.ToString(m20Bytes).Replace("-", "");
            m21Hex = BitConverter.ToString(m21Bytes).Replace("-", "");
            m22Hex = BitConverter.ToString(m22Bytes).Replace("-", "");
            m23Hex = BitConverter.ToString(m23Bytes).Replace("-", "");

            body = m00Hex + m10Hex + m20Hex + m01Hex + m11Hex + m21Hex + m02Hex + m12Hex + m22Hex + m03Hex + m13Hex + m23Hex;

            ulong crcULong = crcGenerator.Compute(StringToByteArray(body), 0, 0);
            CRC = crcULong.ToString("X16");

            string hexmsg = hexHeader + CRC + body;

            // Encode the data string into a byte array.
            byte[] msg = StringToByteArray(hexmsg);

            // Send the data through the socket.
            int bytesSent = sender.Send(msg);

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
