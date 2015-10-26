using UnityEngine;
using System.Collections;

public class FollowPosition : MonoBehaviour {

    public GameObject followTarget;
	
	// Update is called once per frame
	void Update () {
        transform.position = followTarget.transform.position;
	}
}
