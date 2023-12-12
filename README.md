# Short-Video-To-Video

<div align="center">

|         | cloab | huggingface | Maxiduration(s) | API |
| :-------: | :-------: | :-------: | :-------: | :-------: |
| DEMO | [![colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1v1ABcStbUwuCEIQOchLFPFsrD8jUpDr7?usp=sharing) | [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/ximod1a/Short-Video-To-Video) | 60 | ❌ |
| Whisper | [![colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1P1n-xNz0aNRoMv_n40QYKAZZ4wdvJDNa?usp=sharing) | [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/ximod1a/whisper) | 20 | ❌ |

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

**⚠️Attention**
- Currently, only one person’s voice is supported!
-  The currently referenced space is up to one hour. [![huggingface](https://img.shields.io/badge/%F0%9F%A4%97-Open%20in%20Spacce-grue)](https://huggingface.co/spaces/hf-audio/whisper-large-v3)
-  Currently, only Google translator is supported. If you need other `Translator`, first select the `Translator` and submit. You will get `Language has been reloaded, please select again!` Then, select the `Language`.

**⭕The two slowest steps in the current process:**
- Video being recognized as DTS.
- Sending to Whisper.

# Use other translators:
- In the `translates` variable of [list_dict](huggingface/list_dict.py)，find the corresponding Translator, and change `None` to the `variate_name` in the .py file you created.
- And add `from you_flie_name import variate_name` at the top of [list_dict](huggingface/list_dict.py).
- Add the following code in [colab](https://colab.research.google.com/) and run it step by step.
- `!pip install translators` install
- `import translators as ts` import
- `Language_list = ts.translate_text('text', translator='translators', from_language='auto', to_language=None)`Replace 'translators' with the key corresponding to the value you set in [list_dict](huggingface/list_dict.py), this will result in a `TranslatorError` exception, which contains a complete list of this translator, copy it.
- Translate to English: Replace the empty `dict_values` list in the following code.
- ⚠️Note, most codes are supported in the `url`.If you can’t find the code in the second line of the printout, you can try [ISO-639-2](https://support.isan.org/hc/en-us/articles/360012734159-List-of-ISO-639-2-Language-Codes), or ask GPT or Copilot.
```
import bs4
import requests

url = 'https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes#Table'
response = requests.get(url)
soup = bs4.BeautifulSoup(response.text, 'html.parser')

dict_values = []
dict_keys = []
for x in dict_values:
  id = soup.select(f'#{x}')
  if id:
    vl = id[0].get_text()
    dict_keys.append(vl)
  else:
    dict_keys.append('none')

dicts = dict(zip(dict_keys, dict_values))
print(dicts)
print(dicts['none'])
```
