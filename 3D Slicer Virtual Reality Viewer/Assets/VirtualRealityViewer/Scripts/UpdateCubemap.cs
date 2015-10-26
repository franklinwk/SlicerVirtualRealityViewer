using UnityEngine;
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Drawing;

public class UpdateCubemap : MonoBehaviour {

    public string filepath = "C:/Work/data/left.jpg";
    private float totalTime = 0f;

    // Use this for initialization
    void Start() {
        
        // Initialize cubemap texture
        Texture2D tex = new Texture2D(3600, 600, TextureFormat.RGB24, false);

        var bytes = System.IO.File.ReadAllBytes(filepath);
        tex.LoadImage(bytes);
        GetComponent<Renderer>().material.mainTexture = tex;


        /*
        // Find cubemap window and get dimensions
        //System.IntPtr desktopHwnd = FindWindowEx(GetDesktopWindow(), IntPtr.Zero, "Progman", "Program Manager");
        System.IntPtr hwnd = FindWindow(null, "Right 3D Widget");
        var rect = new Rectangle(0,15,700,700);
        //var rect = new Rectangle();
        GetWindowRect(hwnd, ref rect);

        // Save window capture
        var bmp = new Bitmap(rect.Width, rect.Height);
        System.Drawing.Graphics memoryGraphics = System.Drawing.Graphics.FromImage(bmp);
        IntPtr dc = memoryGraphics.GetHdc();
        PrintWindow(hwnd, dc, 0);
        memoryGraphics.ReleaseHdc(dc);

        // Save image to memory stream
        System.IO.MemoryStream ms = new System.IO.MemoryStream();
        bmp.Save(ms, System.Drawing.Imaging.ImageFormat.Png);
        ms.Seek(0, System.IO.SeekOrigin.Begin);

        // Load image and apply to cube
        tex.LoadImage(ms.ToArray());
        GetComponent<Renderer>().material.mainTexture = tex;
        //*/





    }

    [DllImport("User32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint nFlags);

    [DllImport("user32.dll")]
    static extern bool GetWindowRect(IntPtr handle, ref System.Drawing.Rectangle rect);

    [DllImport("user32.dll", EntryPoint = "GetDesktopWindow")]
    static extern IntPtr GetDesktopWindow();

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    static extern IntPtr FindWindowEx(IntPtr parentHandle, IntPtr childAfter, string lclassName, string windowTitle);

    [DllImport("user32.dll")]
    static extern IntPtr FindWindow(string className, string windowTitle);

    // Update is called once per frame
    void Update () {
        if (totalTime*1000 > 500)
        {
            Texture2D tex = new Texture2D(3600, 600, TextureFormat.RGB24, false);
            var bytes = System.IO.File.ReadAllBytes(filepath);
            tex.LoadImage(bytes);
            GetComponent<Renderer>().material.mainTexture = tex;
            totalTime = 0f;
        }

        totalTime = totalTime + Time.deltaTime;
    }
}
