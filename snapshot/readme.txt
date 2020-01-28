Take snapshop of Unifi Security camera

1. Get the camera login credentials from unifi Security
  a. login Unifi Security (via Unifi Cloudkey or similar) using Unifi Security login
  b. go to Settings, Advanced, and unhide Device Password (Reveal) - copy this

2. Login to Unifi Network and obtain the IP address of the camera

A snapshop can be taken using the following cmd

    curl -v -H "Content-Type:application/json" --data "{ \"username\":\"ubnt\", \"password\":\"<password>\" }" http://<ip-address-camera>/api/1.1/snapshot -o test.jpg

Where <password> is the passwordt obtained by 1b below, and the username always is ubnt.
The <ip-address-camera> is the IP address obtained by 2.

To enable snapshot without configuring the camera password enable anonymous snapshot on the camera:

3. Login to the camera (http://<ip-address-camera>) using user ubnt en password from 1b

4. Enable Anonymous Snapshot on the camera
   a. In Configure check Enable Anonymous Snapshot and click Save Changes

Now the url http://<ip-address-camera>/api/1.1/snapshot can be used to grab a snapshot 
without username or password.

