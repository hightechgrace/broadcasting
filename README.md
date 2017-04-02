# Broadcasting
Configuration and scripts for the live video broadcast rig.

Not sure if anyone else will find this stuff useful, it's here mostly as a backup / archive for my own use. The repository is organized by physical machine:

* `colorburst` is the main broadcast machine
	* Black Magic Decklink 4x SDI card
	* Quad Intel i7, NVidia, Windows 10
	* Local storage for recording only, shared with smb
	* Runs obs-studio and airserver
	* Encodes 12000kbit h.264 in hardware, streams to `spacer`

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

* `squarebot` is the sound workstation
	* Macbook Air, just the builtin SSD for audio recording
	* Records multi-channel audio (M-Track 8 + Ableton)
	* Generates a rough audio mix that's distributed to `colorburst` and the other video recorders.

* `brassica` is the CAD workstation
   * Rhino license is stuck on this box
   * Nice GPU here
   * Direct recording for the microscope (HD60+OBS).

