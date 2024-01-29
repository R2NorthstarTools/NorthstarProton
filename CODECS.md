
#### Commands

`ffprobe -v error -show_format -show_streams <file> | grep codec_name`

`gst-discoverer-1.0 <file>`


#### References

* [FFMPEG codecs](https://ffmpeg.org/general.html)
* [GStreamer plugins](https://gstreamer.freedesktop.org/documentation/plugins_doc.html)


#### Game matrix
| Game          | Video      | Audio    | Comments |
|--|--|--|--|
| Mafia         | indeo5     | adpcm_ms |  |
| Crimson Skies | mpegvideo  | mp2      | Not available on Steam |
|               | mpeg1video |          |  |
| DOAXVV        | vc1        |          |  |
|               | vc1image   |          | Untested |

