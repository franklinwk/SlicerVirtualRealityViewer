using UnityEngine;
using System.Collections;

public class UpdateCubemapFromWebcam : MonoBehaviour {

	private WebCamTexture webcamTexture;
	public string webcamName = "XSplit Broadcaster";

	// Initialization
	void Start () {
		// Resolution of input should be 3600 x 600 or something with the same ratio
		//WebCamDevice[] devices = WebCamTexture.devices;
		webcamTexture = new WebCamTexture (webcamName);
		webcamTexture.Play ();
		GetComponent<Renderer> ().material.mainTexture = webcamTexture;
	}
}
