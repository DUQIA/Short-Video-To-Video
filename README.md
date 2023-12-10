# Short-Video-To-Video

<div align="center">

|         | cloab | huggingface | Maxiduration(s) |
| :-------: | :-------: | :-------: | :-------: |
| DEMO | [![colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1v1ABcStbUwuCEIQOchLFPFsrD8jUpDr7?usp=sharing) | [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/ximod1a/Short-Video-To-Video) | 60 |
| Whisper | [![colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1P1n-xNz0aNRoMv_n40QYKAZZ4wdvJDNa?usp=sharing) | [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/ximod1a/whisper) | 20 |

| Process | Short Video To Video | Whisper |
| :-------: | :-------: | :-------: |
| ✅ | Video separation |  |
| ✅ | Vocals separation |  |
| ✅ | Vocals merge mono |  |
| ✅ | Send Whisper |  |
| ✅ |  | Speech to text |
| ✅ | Text to speech |  |
| ✅ | Vocals time verify |  |
| ✅ | video merge |  |

</div>

**Attention**
- Currently, only one person’s voice is supported!
-  The currently referenced space is up to one hour. [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/hf-audio/whisper-large-v3)
-  Currently, only Google translator is supported. If you need other `Translator`, first select the `Translator` and submit. You will get `Language has been reloaded, please select again!` Then, select the `Language`.

**The two slowest steps in the current process:**
- Video being recognized as DTS.
- Sending to Whisper.
