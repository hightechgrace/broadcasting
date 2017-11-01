# Broadcasting
Configuration and scripts for the live video broadcast rig.

Video Tour from September 2017:

* [Tour of the filming setup starts at 17:35](https://www.youtube.com/watch?v=Xj2yoB4EZuY&t=1055s)
* [I open up the rack for a tour at 57:57](https://www.youtube.com/watch?v=Xj2yoB4EZuY&t=3477s)

Not sure if anyone else will find this stuff useful, it's here mostly as a backup / archive for my own use. The repository is organized by physical machine:

* `colorburst` is the main broadcast and sound machine
	* Local storage for recording only, shared with smb
	* Quad Intel i7, NVidia, Windows 10
	* Main Video
		* Black Magic Decklink 4x SDI card (Microscope, DSLR viewfinder, Cat camera, Oscilloscope)
		* Magewell USB 3.0 HDMI capture dongle (to 4x1 switcher for demos)
		* AVermedia USB analog video capture dongle (analog wireless rx)
		* Logitech C920 webcam (desk cam)
		* Runs obs-studio and airserver
		* Encodes 12000kbit h.264 in hardware, streams to `spacer`
	* Tuco Flyer Video
		* Black Magic Mini Recorder PCI card, 1x SDI input
		* Additional copy of obs-studio
		* Encoding 1080p30 at 2500kBps in software with x264
	* Local Audio
		* On-board sound playback (general shop utility, playing music)
		* Line-In is the broadcast audio, via OBS.
		* This could all be replaced by software, but I had problems with both VB-Cable and Virtual Audio Cable
	* Multi-channel Audio
		* Ableton Live for mixing, filtering, and recording
		* ASIO drivers, small buffer size for low latency
		* Generates a rough audio mix in real-time for the stream and video recorders
		* Unprocessed multi-channel recordings for later edits
		* All connections to other computer inputs/outputs made via audio transformers, to avoid hearing ground loop currents caused by digital communications between the same computers.
		* Shotgun microphone: [Rode NTG-1](http://www.rode.com/microphones/ntg-1)
		* Portable headset microphone: Shure WH20XLR
		* 4-channel headphone amp for distributing the rough mix to video recorders
		* 4-channel passive mixer for combining the various shop computers (except for `fishbowl`) into a single `Aux` input for recording

* `spacer` is a Linux transcode server
	* Dual Intel, NVidia, Ubuntu
	* Nginx rtmp server relays video from `colorburst` to YouTube and Twitch
	* Runs real-time transcode for Twitch
	* Off-line transcodes for time lapses
	* Also a good place to run the status display.

* `fishbowl` is the demo machine
   * It's a Mac Mini. No special software needed for broadcast there.
   * 4x HDMI switch for sharing this input with other demo objects is `fishplex`.
   * This HDMI input is split to a monitor, HD60 recorder on `cylindroid`, and a USB3.0 HDMI grabber on `colorburst`.

* `cylindroid` is the editing and file management workstation
	* Mac Pro, local thunderbolt RAID for editing and recording
	* Final Cut Pro X (blah)
	* Direct recording for oscilloscope (BlackMagic+OBS) and `fishplex` (HD60).

* `brassica` is the CAD workstation
   * Rhino license is stuck on this box
   * Nice GPU here
   * Direct recording for the microscope (HD60+OBS).
   
* Other Hardware
	* LED panel lights: Fovitec dual temperature
	* Light C stands (for mounting of various stuff)
	* SLR mounted on a variable friction arm
